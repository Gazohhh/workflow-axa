"""duplicate_skills hook: a session start names second copies of workflow-axa skills and asks the owner to delete them."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "hooks/duplicate_skills.py"


def write(path, text="x"):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))
    return path


class DuplicateSkillsHookTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.base = Path(temp.name).resolve()
        self.plugin = self.base / "plugin"
        self.home = self.base / "home"
        self.config = self.base / "config"
        self.project = self.base / "project"
        for folder in (self.home, self.config, self.project):
            folder.mkdir()
        outside = tempfile.TemporaryDirectory()  # override markers live outside the home, config and project trees
        self.addCleanup(outside.cleanup)
        self.cache = Path(outside.name).resolve() / "gate"
        write(self.plugin / ".claude-plugin/plugin.json",
              json.dumps({"name": "workflow-axa", "skills": ["./skills/tdd", "./skills/rule-maker"]}))
        write(self.plugin / "skills/tdd/SKILL.md", "plugin tdd")
        write(self.plugin / "skills/rule-maker/SKILL.md", "plugin rule-maker")
        write(self.plugin / "skills/rule-maker/rules/START.md", "start")
        write(self.plugin / "skills/rule-maker/rules/CORE.md", "core")

    def fire(self, event=None, *, raw=None, config=True, plugin=True, cache=None):
        env = dict(os.environ, USERPROFILE=str(self.home), HOME=str(self.home),
                   WORKFLOW_AXA_GATE_CACHE=str(cache or self.cache))
        for name in ("CLAUDE_PLUGIN_ROOT", "CLAUDE_CONFIG_DIR", "HOMEDRIVE", "HOMEPATH"):
            env.pop(name, None)
        if plugin:
            env["CLAUDE_PLUGIN_ROOT"] = str(self.plugin if plugin is True else plugin)
        if config:
            env["CLAUDE_CONFIG_DIR"] = str(self.config)
        if raw is None:
            raw = json.dumps({"hook_event_name": "SessionStart", "session_id": "s1", "cwd": str(self.project)}
                             if event is None else event)
        result = subprocess.run([sys.executable, "-X", "utf8", "-I", str(HOOK)], input=raw,
                                capture_output=True, text=True, encoding="utf-8", env=env)
        return result.returncode, result.stdout.strip()

    def message(self, **kwargs):
        code, out = self.fire(**kwargs)
        self.assertEqual(code, 0)
        data = json.loads(out)
        self.assertEqual(list(data), ["hookSpecificOutput"])
        self.assertEqual(sorted(data["hookSpecificOutput"]), ["additionalContext", "hookEventName"])
        self.assertEqual(data["hookSpecificOutput"]["hookEventName"], "SessionStart")
        return data["hookSpecificOutput"]["additionalContext"]

    def test_duplicate_in_config_dir_is_named_with_a_request_to_delete(self):
        write(self.config / "skills/tdd/SKILL.md", "another tdd")
        note = self.message()
        self.assertIn(str(self.config / "skills" / "tdd"), note.splitlines())
        self.assertIn("different results", note)
        self.assertIn("first reply", note)
        self.assertIn("explain the ways to settle it", note)  # T20: options, not a demand to delete
        self.assertIn("Do not change them yourself", note)
        self.assertIn("Nothing is paused", note)
        self.assertNotIn("continue with duplicates", note)
        for banned in (";", "—", "'"):
            self.assertNotIn(banned, note)

    def test_duplicate_in_project_skills_is_named(self):
        write(self.project / ".claude/skills/rule-maker/SKILL.md", "project copy")
        note = self.message()
        self.assertIn(str(self.project / ".claude" / "skills" / "rule-maker"), note.splitlines())
        self.assertIn("explain the ways to settle it", note)

    def test_every_duplicate_gets_its_own_line(self):
        write(self.config / "skills/tdd/SKILL.md")
        write(self.config / "skills/rule-maker/SKILL.md")
        write(self.project / ".claude/skills/tdd/SKILL.md")
        lines = self.message().splitlines()
        for path in (self.config / "skills" / "tdd", self.config / "skills" / "rule-maker",
                     self.project / ".claude" / "skills" / "tdd"):
            self.assertEqual(lines.count(str(path)), 1, path)

    def test_equal_bytes_still_count(self):
        write(self.config / "skills/tdd/SKILL.md", "plugin tdd")
        self.assertIn(str(self.config / "skills" / "tdd"), self.message().splitlines())

    def test_without_config_dir_variable_the_home_claude_folder_is_checked(self):
        write(self.home / ".claude/skills/tdd/SKILL.md")
        write(self.config / "skills/rule-maker/SKILL.md")  # not the config dir in this run
        lines = self.message(config=False).splitlines()
        self.assertIn(str(self.home / ".claude" / "skills" / "tdd"), lines)
        self.assertNotIn(str(self.config / "skills" / "rule-maker"), lines)

    def test_without_plugin_root_variable_the_names_come_from_this_package(self):
        write(self.config / "skills/workflow-clarify/SKILL.md")
        write(self.config / "skills/not-a-workflow-axa-skill/SKILL.md")
        lines = self.message(plugin=False).splitlines()
        self.assertIn(str(self.config / "skills" / "workflow-clarify"), lines)
        self.assertNotIn(str(self.config / "skills" / "not-a-workflow-axa-skill"), lines)

    def test_no_duplicate_prints_nothing(self):
        self.assertEqual(self.fire(), (0, ""))
        self.assertEqual(self.fire({"hook_event_name": "SessionStart", "session_id": "s1"}), (0, ""))

    def test_event_without_cwd_still_checks_the_config_dir(self):
        write(self.config / "skills/tdd/SKILL.md")
        note = self.message(event={"hook_event_name": "SessionStart", "session_id": "s1"})
        self.assertIn(str(self.config / "skills" / "tdd"), note.splitlines())

    def test_unregistered_name_and_folder_without_skill_file_are_not_reported(self):
        write(self.config / "skills/superpowers/SKILL.md")
        write(self.config / "skills/tdd/README.md")
        (self.config / "skills/rule-maker/SKILL.md").mkdir(parents=True)  # a folder, not a file
        write(self.project / ".claude/skills/other/SKILL.md")
        (self.project / ".claude/skills/tdd").mkdir()
        self.assertEqual(self.fire(), (0, ""))

    def test_project_copy_inside_the_plugin_checkout_is_reported(self):
        # Working on the plugin's own repository: its .claude/skills is still a second visible place.
        write(self.plugin / ".claude/skills/tdd/SKILL.md")
        event = {"hook_event_name": "SessionStart", "session_id": "s1", "cwd": str(self.plugin)}
        self.assertIn(str(self.plugin / ".claude" / "skills" / "tdd"), self.message(event=event).splitlines())

    def test_session_started_in_the_home_folder_names_each_copy_once(self):
        # <cwd>/.claude/skills and <home>/.claude/skills are the same folder here, also in another letter case.
        write(self.home / ".claude/skills/tdd/SKILL.md")
        for cwd in (str(self.home), str(self.home).swapcase() if os.name == "nt" else str(self.home)):
            with self.subTest(cwd=cwd):
                event = {"hook_event_name": "SessionStart", "session_id": "s1", "cwd": cwd}
                lines = self.message(event=event, config=False).splitlines()
                self.assertEqual([line for line in lines if line.lower().endswith("tdd")],
                                 [str(self.home / ".claude" / "skills" / "tdd")])

    def test_session_started_in_a_subfolder_checks_parents_up_to_the_repository_root(self):
        # Claude Code loads project skills from the start folder and every parent up to the repository root.
        (self.project / "repo/.git").mkdir(parents=True)
        write(self.project / "repo/.claude/skills/tdd/SKILL.md")
        write(self.project / ".claude/skills/rule-maker/SKILL.md")  # above the repository root: not loaded
        (self.project / "repo/src/deep").mkdir(parents=True)
        event = {"hook_event_name": "SessionStart", "session_id": "s1", "cwd": str(self.project / "repo/src/deep")}
        lines = self.message(event=event).splitlines()
        self.assertIn(str(self.project / "repo" / ".claude" / "skills" / "tdd"), lines)
        self.assertNotIn(str(self.project / ".claude" / "skills" / "rule-maker"), lines)

    def test_outside_a_repository_only_the_start_folder_is_checked(self):
        write(self.project / ".claude/skills/tdd/SKILL.md")
        (self.project / "sub").mkdir()
        event = {"hook_event_name": "SessionStart", "session_id": "s1", "cwd": str(self.project / "sub")}
        self.assertEqual(self.fire(event), (0, ""))

    def test_deeply_nested_input_is_silent(self):
        write(self.config / "skills/tdd/SKILL.md")
        self.assertEqual(self.fire(raw="[" * 200000), (0, ""))

    def test_request_says_to_remove_a_link_itself(self):
        write(self.config / "skills/tdd/SKILL.md")
        self.assertIn("If an entry is a link, remove only the link, not the folder it points at.", self.message())

    def test_import_written_from_the_home_folder_or_relative_to_the_config_dir(self):
        folder = self.rules_copy(core="changed")
        write(self.config / "CLAUDE.md", "@~/.agents/skills/rule-maker/rules/START.md\n")
        self.assertIn(str(folder), self.message())
        inner = self.config / "shared/rule-maker/rules"
        write(inner / "START.md", "start")
        write(inner / "CORE.md", "changed")
        write(self.config / "CLAUDE.md", "@shared/rule-maker/rules/START.md\n")
        self.assertIn(str(inner), self.message())
        write(inner / "CORE.md", "core")
        self.assertEqual(self.fire(), (0, ""))

    def rules_copy(self, start="start", core="core"):
        """A second rules folder that the global CLAUDE.md imports, written with forward slashes."""
        folder = self.home / ".agents/skills/rule-maker/rules"
        write(folder / "START.md", start)
        if core is not None:
            write(folder / "CORE.md", core)
        write(self.config / "CLAUDE.md",
              "# Global instructions\n\n@" + folder.as_posix() + "/START.md\n@" + folder.as_posix() + "/CORE.md\n")
        return folder

    def test_rules_copy_with_one_changed_byte_gives_a_warning_and_no_pause(self):
        folder = self.rules_copy(core="corE")
        note = self.message()
        self.assertEqual(len(note.splitlines()), 1)
        self.assertIn(str(folder), note)
        self.assertIn("differs from the rules in the workflow-axa plugin", note)
        self.assertIn("reinstall or update", note)
        self.assertIn("does not pause work", note)
        self.assertNotIn("continue with duplicates", note)
        self.assertNotIn("delete", note)
        for banned in (";", "—", "'"):
            self.assertNotIn(banned, note)

    def test_rules_copy_with_a_missing_file_gives_a_warning(self):
        folder = self.rules_copy(core=None)
        self.assertIn(str(folder), self.message())

    def test_identical_rules_copy_prints_nothing(self):
        folder = self.rules_copy()
        write(folder / "EXTRA.md", "only in the copy")  # the plugin's files are the ones compared
        (self.plugin / "skills/rule-maker/rules/subfolder").mkdir()  # only files directly inside count
        self.assertEqual(self.fire(), (0, ""))

    def test_no_import_line_means_no_rules_check(self):
        folder = self.rules_copy(core="different")
        write(self.config / "CLAUDE.md", "# Global instructions\n\nSee " + folder.as_posix() + "/START.md\n")
        self.assertEqual(self.fire(), (0, ""))
        (self.config / "CLAUDE.md").unlink()
        self.assertEqual(self.fire(), (0, ""))

    def test_import_of_the_plugin_rules_folder_itself_prints_nothing(self):
        folder = self.plugin / "skills/rule-maker/rules"
        write(self.config / "CLAUDE.md", "@" + folder.as_posix() + "/START.md\n")
        self.assertEqual(self.fire(), (0, ""))

    def test_duplicate_and_rules_difference_are_both_reported(self):
        folder = self.rules_copy(start="changed")
        write(self.config / "skills/tdd/SKILL.md")
        note = self.message()
        self.assertIn(str(self.config / "skills" / "tdd"), note.splitlines())
        self.assertIn("Nothing is paused", note)
        warnings = [line for line in note.splitlines() if str(folder) in line and "does not pause work" in line]
        self.assertEqual(len(warnings), 1)

    def test_bad_input_is_silent(self):
        write(self.config / "skills/tdd/SKILL.md")
        for raw in ("nope", "", "[1, 2]", '"SessionStart"', "null", "{"):
            with self.subTest(raw=raw):
                self.assertEqual(self.fire(raw=raw), (0, ""))
        for cwd in (7, ["x"], {"a": 1}, "bad\u0000path", "<>:|?*"):
            with self.subTest(cwd=cwd):
                note = self.message(event={"hook_event_name": "SessionStart", "cwd": cwd})
                self.assertEqual([line for line in note.splitlines() if "tdd" in line],
                                 [str(self.config / "skills" / "tdd")])

    def test_other_events_are_silent(self):
        write(self.config / "skills/tdd/SKILL.md")
        self.rules_copy(core="changed")
        for event in ({"hook_event_name": "PostToolUse", "tool_name": "Skill", "tool_input": {"skill": "tdd"}},
                      {"hook_event_name": "Stop"}, {"cwd": str(self.project)}, {"hook_event_name": None}):
            with self.subTest(event=event):
                self.assertEqual(self.fire(event), (0, ""))

    def test_missing_or_broken_plugin_manifest_is_silent(self):
        write(self.config / "skills/tdd/SKILL.md")
        manifest = self.plugin / ".claude-plugin/plugin.json"
        for text in ("not json", "[]", '{"name": "workflow-axa"}', '{"skills": "./skills/tdd"}', '{"skills": [3, null]}'):
            with self.subTest(text=text):
                write(manifest, text)
                self.assertEqual(self.fire(), (0, ""))
        manifest.unlink()
        self.assertEqual(self.fire(), (0, ""))
        self.assertEqual(self.fire(plugin=self.base / "no-such-plugin"), (0, ""))

    def test_unknown_home_folder_is_silent(self):
        env = {key: value for key, value in os.environ.items()
               if key not in ("CLAUDE_CONFIG_DIR", "USERPROFILE", "HOME", "HOMEDRIVE", "HOMEPATH")}
        env["CLAUDE_PLUGIN_ROOT"] = str(self.plugin)
        result = subprocess.run([sys.executable, "-X", "utf8", "-I", str(HOOK)],
                                input=json.dumps({"hook_event_name": "SessionStart", "cwd": str(self.base / "empty")}),
                                capture_output=True, text=True, encoding="utf-8", env=env)
        self.assertEqual(result.returncode, 0, result.stderr)
        if os.name == "nt":  # elsewhere the home folder comes from the user database and may hold real skills
            self.assertEqual(result.stdout, "")

    def snapshot(self):
        return {str(path.relative_to(self.base)): path.read_bytes() if path.is_file() else None
                for path in sorted(self.base.rglob("*"))}

    def test_the_script_changes_no_file(self):
        write(self.config / "skills/tdd/SKILL.md", "plugin tdd")
        write(self.home / ".claude/skills/rule-maker/SKILL.md")
        write(self.project / ".claude/skills/tdd/SKILL.md")
        write(self.project / "src/app.py", "print(1)")
        self.rules_copy(core="changed")
        before = self.snapshot()
        self.assertGreater(len(before), 15)
        self.assertIn("Nothing is paused", self.message())
        self.assertIn("Nothing is paused", self.message(config=False))
        self.fire(raw="nope")
        self.fire({"hook_event_name": "UserPromptSubmit", "prompt": "continue with duplicates", "session_id": "s1"})
        self.fire({"hook_event_name": "PreToolUse", "tool_name": "Skill", "tool_input": {"skill": "tdd"},
                   "session_id": "s1"})
        self.assertEqual(self.snapshot(), before)  # T20: diagnose only, so no marker and no write anywhere
        self.assertNotIn(self.base, self.cache.parents)

    def link(self, target, link):
        """A symbolic link, or a Windows junction where symbolic links need a privilege."""
        link.parent.mkdir(parents=True, exist_ok=True)
        try:
            os.symlink(target, link, target_is_directory=True)
        except (OSError, NotImplementedError) as error:
            try:
                import _winapi
                _winapi.CreateJunction(str(target), str(link))
            except (ImportError, AttributeError, OSError):
                self.skipTest(f"this system refuses to create symbolic links: {error}")

    def test_symbolic_link_duplicate_is_reported_even_when_it_points_at_the_plugin(self):
        self.link(self.plugin / "skills/tdd", self.config / "skills/tdd")
        other = write(self.base / "elsewhere/rule-maker/SKILL.md").parent
        self.link(other, self.project / ".claude/skills/rule-maker")
        lines = self.message().splitlines()
        self.assertIn(str(self.config / "skills" / "tdd"), lines)
        self.assertIn(str(self.project / ".claude" / "skills" / "rule-maker"), lines)

    def test_skills_folder_that_links_to_the_plugin_skills_is_reported(self):
        self.link(self.plugin / "skills", self.config / "skills")
        lines = self.message().splitlines()
        self.assertIn(str(self.config / "skills" / "tdd"), lines)
        self.assertIn(str(self.config / "skills" / "rule-maker"), lines)

    def test_broken_link_is_not_reported(self):
        target = write(self.base / "gone/tdd/SKILL.md").parent
        self.link(target, self.config / "skills/tdd")
        (target / "SKILL.md").unlink()
        target.rmdir()
        self.assertTrue(os.path.lexists(self.config / "skills/tdd"))
        self.assertEqual(self.fire(), (0, ""))

    def skill(self, name, session="s1", **kwargs):
        """Fire a Skill tool call; return the deny reason, or None when the call is allowed."""
        event = {"hook_event_name": "PreToolUse", "session_id": session, "cwd": str(self.project),
                 "tool_name": "Skill", "tool_input": {"skill": name}}
        code, out = self.fire(event, **kwargs)
        self.assertEqual(code, 0)
        if not out:
            return None
        data = json.loads(out)
        self.assertEqual(list(data), ["hookSpecificOutput"])
        self.assertEqual(sorted(data["hookSpecificOutput"]),
                         ["hookEventName", "permissionDecision", "permissionDecisionReason"])
        self.assertEqual(data["hookSpecificOutput"]["hookEventName"], "PreToolUse")
        self.assertEqual(data["hookSpecificOutput"]["permissionDecision"], "deny")
        return data["hookSpecificOutput"]["permissionDecisionReason"]








    def say(self, prompt, session="s1", **kwargs):
        """Fire a user message; it must always be silent."""
        event = {"hook_event_name": "UserPromptSubmit", "cwd": str(self.project), "prompt": prompt}
        if session is not None:
            event["session_id"] = session
        self.assertEqual(self.fire(event, **kwargs), (0, ""))






    def marker(self, session):
        return self.cache / ("duplicates-ok-" + hashlib.sha256(session.encode()).hexdigest()[:32])




    def typed(self, prompt, session="s1"):
        code, out = self.fire({"hook_event_name": "UserPromptSubmit", "cwd": str(self.project), "prompt": prompt,
                               "session_id": session})
        self.assertEqual(code, 0)
        return json.loads(out) if out else None






    def test_hooks_json_wires_it_for_session_start_only(self):
        hooks = json.loads((ROOT / "hooks/hooks.json").read_text(encoding="utf-8"))["hooks"]
        script = "${CLAUDE_PLUGIN_ROOT}/hooks/duplicate_skills.py"

        def commands(entries):
            return [hook["command"] for entry in entries for hook in entry["hooks"]]

        self.assertEqual(sum(script in command for command in commands(hooks["SessionStart"])), 1)
        for event in ("PreToolUse", "UserPromptSubmit"):  # T20: diagnose only, it never blocks a call or a message
            self.assertFalse(any(script in command for command in commands(hooks.get(event, []))))




    # Every registration in hooks/hooks.json that is not the duplicate guard: (event, matcher, script and arguments).
    OTHER_HOOKS = [
        ("PreToolUse", "Edit|Write|MultiEdit|NotebookEdit|Bash|PowerShell|Skill|mcp__.*([Cc]reate|[Ww]rite|[Ee]dit|"
                       "[Dd]elete|[Aa]pply|[Uu]pdate|[Ii]mport|[Ee]xecute|[Mm]anage).*", 'approval.py"'),
        ("PostToolUse", "Bash|PowerShell|Read|Edit|Write|MultiEdit|AskUserQuestion", 'phase_gate.py" --hook-protocol=1'),
        ("UserPromptSubmit", None, 'phase_gate.py" --hook-protocol=1'),
    ]  # T20: truncated_read, phase_reads and the plain_reply Stop hook are gone

    @staticmethod
    def other_hooks(hooks):
        prefix = 'python -X utf8 -I "${CLAUDE_PLUGIN_ROOT}/hooks/'
        events = ("PreToolUse", "PostToolUse", "UserPromptSubmit", "Stop", "SessionStart")
        found = []
        for event in events:
            for entry in hooks.get(event, []):
                for hook in entry["hooks"]:
                    if "duplicate_skills.py" in hook["command"]:
                        continue
                    timeout = 20 if "approval.py" in hook["command"] else 5  # T17: its legacy route runs phase_gate
                    if hook.get("type") != "command" or hook.get("timeout") != timeout or not hook["command"].startswith(prefix):
                        found.append((event, entry.get("matcher"), hook))
                    else:
                        found.append((event, entry.get("matcher"), hook["command"][len(prefix):]))
        return found + [(event, None, "unexpected event") for event in hooks if event not in events]

    def test_registrations_of_the_other_hooks_are_unchanged(self):
        hooks = json.loads((ROOT / "hooks/hooks.json").read_text(encoding="utf-8"))["hooks"]
        self.assertEqual(self.other_hooks(hooks), self.OTHER_HOOKS)
        # The check itself must notice a removed, changed or added registration.
        removed = json.loads(json.dumps(hooks))
        del removed["UserPromptSubmit"]
        changed = json.loads(json.dumps(hooks))
        changed["PostToolUse"][0]["matcher"] = "Bash"
        retimed = json.loads(json.dumps(hooks))
        retimed["PreToolUse"][0]["hooks"][0]["timeout"] = 60
        added = json.loads(json.dumps(hooks))
        added["Notification"] = [{"hooks": [{"type": "command", "command": "x"}]}]
        renamed = json.loads(json.dumps(hooks))
        renamed["PostToolUse"][0]["hooks"][0]["command"] = renamed["PostToolUse"][0]["hooks"][0]["command"].replace("phase_gate", "other")
        for name, copy in (("removed", removed), ("changed", changed), ("retimed", retimed), ("added", added),
                           ("renamed", renamed)):
            with self.subTest(copy=name):
                self.assertNotEqual(self.other_hooks(copy), self.OTHER_HOOKS)





    # Ticket H5: an enabled plugin whose process skills overlap the workflow-axa phases is named at session start.
    def settings(self, place, plugins):
        """Write enabledPlugins into the user, project or project local Claude settings file."""
        path = {"user": self.config / "settings.json", "project": self.project / ".claude/settings.json",
                "local": self.project / ".claude/settings.local.json"}[place]
        write(path, json.dumps({"enabledPlugins": plugins}))
        return path

    def overlap_lines(self, **kwargs):
        code, out = self.fire(**kwargs)
        self.assertEqual(code, 0)
        if not out:
            return []
        return [line for line in json.loads(out)["hookSpecificOutput"]["additionalContext"].splitlines()
                if "superpowers" in line]

    def test_superpowers_enabled_in_user_settings_gets_a_short_note(self):
        # The note is added to every session while superpowers is on, so it stays short.
        self.settings("user", {"superpowers@claude-plugins-official": True})
        note = self.message()
        self.assertEqual(len(note.splitlines()), 1)
        self.assertLess(len(note.split()), 65)  # SP9: room for the skill names, still one short line
        self.assertIn("Your settings enable the superpowers plugin. If loaded here, its skills overlap the "
                      "workflow-axa phases.", note)
        self.assertNotIn("plugin is also enabled", note)  # T26 F1: never claims the plugin is loaded
        self.assertIn("While a workflow-axa task runs, use workflow-clarify instead of brainstorming,", note)
        self.assertIn("Do not change plugin settings yourself.", note)
        self.assertIn("The user can disable superpowers for this project.", note)

    def test_the_overlap_note_names_each_skill_and_the_one_to_use(self):
        """SP9 (R13, A12): the note names the overlapping superpowers skills and the workflow-axa skill to use."""
        self.settings("user", {"superpowers@claude-plugins-official": True})
        note = self.message()
        for pair in ("workflow-clarify instead of brainstorming", "workflow-specify instead of writing-plans",
                     "workflow-execute instead of executing-plans and subagent-driven-development",
                     "tdd instead of test-driven-development", "code-review instead of requesting-code-review",
                     "workflow-deliver instead of verification-before-completion"):
            self.assertIn(pair, note)
        # Every workflow-axa skill the note names is one this package registers.
        registered = {item.rsplit("/", 1)[-1] for item in
                      json.loads((ROOT / ".claude-plugin/plugin.json").read_text(encoding="utf-8-sig"))["skills"]}
        for name in ("workflow-clarify", "workflow-specify", "workflow-execute", "tdd", "code-review",
                     "workflow-deliver"):
            self.assertIn(name, registered)

    def test_an_overlap_note_with_one_pair_reads_as_a_sentence(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("duplicate_skills_under_test", HOOK)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        note = module.overlap_message("other", (("tdd", ("test-driven-development",)),))
        self.assertIn("While a workflow-axa task runs, use tdd instead of test-driven-development. ", note)
        self.assertNotIn(", and", note)
        two = module.overlap_message("other", (("tdd", ("a",)), ("code-review", ("b",))))
        self.assertIn("use tdd instead of a and code-review instead of b. ", two)

    def test_a_more_specific_settings_file_that_disables_the_plugin_wins(self):
        self.settings("user", {"superpowers@claude-plugins-official": True})
        self.settings("project", {"superpowers@claude-plugins-official": False})
        self.assertEqual(self.fire(), (0, ""))
        self.settings("local", {"superpowers@claude-plugins-official": True})  # local is more specific than project
        self.assertEqual(len(self.overlap_lines()), 1)
        self.settings("project", {"superpowers@claude-plugins-official": True})
        self.settings("local", {"superpowers@claude-plugins-official": False})
        self.assertEqual(self.fire(), (0, ""))

    def test_superpowers_enabled_only_in_project_local_settings_is_named(self):
        self.settings("local", {"superpowers@claude-plugins-official": True})
        self.assertEqual(len(self.overlap_lines()), 1)
        # Without a cwd the project files are not known, so only the user file counts.
        self.assertEqual(self.fire({"hook_event_name": "SessionStart", "session_id": "s1"}), (0, ""))

    def test_session_in_a_subfolder_reads_the_project_settings_at_the_repository_root(self):
        (self.project / ".git").mkdir()
        (self.project / "src/deep").mkdir(parents=True)
        event = {"hook_event_name": "SessionStart", "session_id": "s1", "cwd": str(self.project / "src/deep")}
        for place in ("project", "local"):
            with self.subTest(place=place):
                path = self.settings(place, {"superpowers@claude-plugins-official": True})
                self.assertEqual(len(self.overlap_lines(event=event)), 1)
                path.unlink()
        self.settings("user", {"superpowers@claude-plugins-official": True})
        self.settings("local", {"superpowers@claude-plugins-official": False})
        self.assertEqual(self.fire(event), (0, ""))

    def test_superpowers_from_another_marketplace_is_named(self):
        self.settings("user", {"superpowers@my-own-marketplace": True})
        self.assertEqual(len(self.overlap_lines()), 1)

    def test_no_line_when_superpowers_is_absent_or_not_switched_on(self):
        for plugins in ({}, {"postman@claude-plugins-official": True}, {"superpowers-extra@x": True},
                        {"my-superpowers@x": True}, {"superpowers@x": False}, {"superpowers@x": "true"},
                        {"superpowers@x": 1}, {"superpowers@x": None}):
            with self.subTest(plugins=plugins):
                self.settings("user", plugins)
                self.assertEqual(self.fire(), (0, ""))

    def test_malformed_settings_add_nothing(self):
        path = self.config / "settings.json"
        for text in ("{", "not json", "[]", "null", '"superpowers@x"', '{"enabledPlugins": ["superpowers@x"]}',
                     '{"enabledPlugins": "superpowers@x"}', '{"enabledPlugins": null}', '{"other": true}', ""):
            with self.subTest(text=text):
                write(path, text)
                self.assertEqual(self.fire(), (0, ""))
        path.unlink()
        (self.config / "settings.json").mkdir()  # a folder, not a readable file
        self.assertEqual(self.fire(), (0, ""))

    def test_deeply_nested_settings_keep_the_duplicate_note(self):
        write(self.config / "skills/tdd/SKILL.md")
        for place in ("user", "project", "local"):
            with self.subTest(place=place):
                path = self.settings(place, {})
                write(path, '{"enabledPlugins": ' + "[" * 200000)
                note = self.message()
                self.assertIn(str(self.config / "skills" / "tdd"), note.splitlines())
                self.assertNotIn("superpowers", note)
                path.unlink()

    def test_overlap_and_duplicate_are_reported_in_one_output(self):
        write(self.config / "skills/tdd/SKILL.md")
        self.settings("project", {"superpowers@claude-plugins-official": True})
        note = self.message()
        self.assertIn(str(self.config / "skills" / "tdd"), note.splitlines())
        self.assertIn("Nothing is paused", note)
        self.assertEqual(len(self.overlap_lines()), 1)
        self.assertNotIn("superpowers", note.split("Nothing is paused")[0])  # the duplicate note comes first

    def test_overlap_note_wording(self):
        self.settings("user", {"superpowers@claude-plugins-official": True})
        note = self.message()
        for banned in (";", "—", "–", "'", "’", "n't"):
            self.assertNotIn(banned, note)
        self.assertNotIn("continue with duplicates", note)

    def test_overlap_never_pauses_or_blocks(self):
        self.settings("user", {"superpowers@claude-plugins-official": True})
        for name in ("workflow-axa:workflow-clarify", "workflow-execute", "superpowers:brainstorming"):
            with self.subTest(name=name):
                self.assertIsNone(self.skill(name))
        self.assertIsNone(self.typed("/workflow-axa:workflow-clarify fix the bug"))
        self.assertFalse(self.cache.exists())

    def test_reading_settings_changes_no_file(self):
        self.settings("user", {"superpowers@claude-plugins-official": True})
        self.settings("project", {"superpowers@claude-plugins-official": False})
        self.settings("local", {"superpowers@claude-plugins-official": True, "other@x": False})
        write(self.config / "skills/tdd/SKILL.md")
        before = self.snapshot()
        self.assertEqual(len(self.overlap_lines()), 1)
        self.skill("workflow-axa:workflow-clarify")
        self.typed("/workflow-axa:workflow-clarify fix the bug")
        self.assertEqual(self.snapshot(), before)


if __name__ == "__main__":
    unittest.main()
