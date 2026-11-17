"""Formerly copied skills are owned single texts: no source mentions under skills/, licences kept."""
from __future__ import annotations

import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
FORMERLY_COPIED = ("grilling", "tdd", "code-review", "writing-for-agents", "codebase-design",
                   "domain-modeling")
# T22 (2.9.0): implement-spec and retro are archived with their licences; simple-english is reference text
# inside the workflow skill, with its licence beside it.
ARCHIVED = ("implement-spec", "retro", "simple-english")
USER_ONLY: set[str] = set()
# The owner asked (2026-11-12) for no reference to where these skills came from anywhere under skills/.
# LICENSE files are exempt: the MIT licence requires its copyright notice to stay with the copied text.
SOURCE_MENTIONS = re.compile(
    r"mattpocock|matt-pocock|Matt Pocock|\bMatt's\b|\bMatt\b|AminBlg|SimpleEnglish|Bundled with workflow-axa"
    r"|workflow-axa adaptation|\bupstream\b|cathrynlavery|\bLavery\b|pstack|Lauren Tan|cursor/plugins",
    re.IGNORECASE,
)
# Lower-case only: the compatibility file DIAGRAM-DESIGN.md keeps its name.
SOURCE_NAMES_EXACT = re.compile(r"diagram-design")
TEXT_SUFFIXES = {".md", ".json", ".py", ".txt", ".html", ".css", ".js", ".yaml", ".yml"}


class OwnedSkillTests(unittest.TestCase):
    def test_each_formerly_copied_skill_is_registered_and_keeps_its_licence(self):
        plugin = json.loads((ROOT / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
        for name in FORMERLY_COPIED:
            folder = ROOT / "skills" / name
            self.assertIn(f"./skills/{name}", plugin["skills"])
            self.assertIn("MIT License", (folder / "LICENSE").read_text(encoding="utf-8"), name)
            text = (folder / "SKILL.md").read_text(encoding="utf-8")
            self.assertTrue(text.startswith(f"---\nname: {name}\n"), name)
            self.assertEqual("disable-model-invocation: true" in text.split("---", 2)[1], name in USER_ONLY, name)
        for name in ARCHIVED:
            self.assertNotIn(f"./skills/{name}", plugin["skills"])
            self.assertFalse((ROOT / "skills" / name).exists(), name)
            self.assertIn("MIT License", (ROOT / "docs/archive/skills" / name / "LICENSE").read_text(encoding="utf-8"), name)
        self.assertIn("MIT License", (ROOT / "skills/workflow/SIMPLE-ENGLISH.LICENSE").read_text(encoding="utf-8"))
        self.assertFalse((ROOT / "skills/workflow/specialists").exists(), "old bundled folder must be gone")
        self.assertFalse((ROOT / "skills/workflow/specialists.json").exists(), "D17: no catalogue of external providers")

    def test_phase_skills_load_their_sibling_skills(self):
        uses = {"workflow-clarify": ["../grilling/SKILL.md"],
                "workflow-execute": ["../tdd/SKILL.md", "../code-review/SKILL.md"],
                "workflow-specify": ["../codebase-design/SKILL.md"]}
        for skill, paths in uses.items():
            text = (ROOT / f"skills/{skill}/SKILL.md").read_text(encoding="utf-8")
            for path in paths:
                self.assertIn(path, text, skill)
            self.assertNotRegex(text, r"installed `(grilling|tdd|code-review)`", skill)

    def test_the_pattern_covers_every_credited_source(self):
        """The blast-radius method and the Unslop tells (VENDORED-SKILLS.md) are covered by the same rule."""
        for line in ("adapted from pstack", "by Lauren Tan", "see github.com/cursor/plugins"):
            with self.subTest(line=line):
                self.assertTrue(SOURCE_MENTIONS.search(line), line)

    def test_credits_name_both_new_licences_without_new_skills(self):
        sys.path.insert(0, str(ROOT / "tools"))
        from validate import licence_files, licensed_skills
        files = licence_files(ROOT)
        for path in ("skills/code-review/BLAST-RADIUS.LICENSE", "skills/workflow/UNSLOP.LICENSE"):
            with self.subTest(path=path):
                self.assertIn(path, files)
                self.assertTrue((ROOT / path).is_file())
        self.assertEqual(["code-review", "codebase-design", "domain-modeling", "grilling", "implement-spec", "retro",
                          "simple-english", "tdd", "writing-for-agents"], licensed_skills(ROOT))

    def test_no_file_under_skills_names_where_a_skill_came_from(self):
        hits = []
        for path in sorted((ROOT / "skills").rglob("*")):
            if not path.is_file() or path.name == "LICENSE" or path.suffix.lower() not in TEXT_SUFFIXES:
                continue
            if "__pycache__" in path.parts:
                continue
            for number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
                match = SOURCE_MENTIONS.search(line) or SOURCE_NAMES_EXACT.search(line)
                if match:
                    hits.append(f"{path.relative_to(ROOT).as_posix()}:{number}: {match.group(0)}")
        self.assertEqual([], hits)


class SessionDigestTests(unittest.TestCase):
    """tools/digest_sessions.py (formerly retro's script)."""

    def test_session_digest_lists_human_messages_and_skills(self):
        with tempfile.TemporaryDirectory() as tmp:
            logs = Path(tmp) / "logs"
            logs.mkdir()
            lines = [
                {"type": "user", "timestamp": "2026-11-02T10:00:00Z", "message": {"content": "/workflow add a filter"}},
                {"type": "assistant", "timestamp": "2026-11-02T10:01:00Z", "message": {"content": [
                    {"type": "tool_use", "name": "Skill", "input": {"skill": "workflow"}},
                    {"type": "tool_use", "name": "AskUserQuestion", "input": {"questions": [{"question": "Remember it?"}]}}]}},
                {"type": "user", "timestamp": "2026-11-02T10:02:00Z", "message": {"content": [
                    {"type": "tool_result", "is_error": True, "content": "Permission denied"}]}},
                {"type": "user", "timestamp": "2026-11-02T10:03:00Z", "message": {"content": "<task-notification>done</task-notification>"}},
                {"type": "user", "timestamp": "2026-11-02T10:04:00Z", "message": {"content": "is it done?"}},
            ]
            (logs / "s1.jsonl").write_text("\n".join(json.dumps(l) for l in lines) + "\nnot json\n", encoding="utf-8")
            out = Path(tmp) / "digest.md"
            subprocess.run([sys.executable, "-X", "utf8", "-I", str(ROOT / "tools/digest_sessions.py"), str(logs), str(out)],
                           check=True, capture_output=True)
            text = out.read_text(encoding="utf-8")
        self.assertIn("human messages: 2", text)
        self.assertIn("is it done?", text)
        self.assertNotIn("task-notification", text)
        self.assertIn("skills: ['workflow']", text)
        self.assertIn("Q: Remember it?", text)
        self.assertIn("tool errors: 1 (denied 1); hook denials: 0", text)

    def test_session_digest_counts_hook_denials(self):
        # P1-P3 digest: seven phase-gate denials showed as "denied 0".
        with tempfile.TemporaryDirectory() as tmp:
            logs = Path(tmp) / "logs"
            logs.mkdir()
            block = {"type": "tool_result", "is_error": True,
                     "content": "PreToolUse:Edit hook error: workflow-axa: editing src/a.py needs implementation approval"}
            (logs / "s1.jsonl").write_text(json.dumps({"type": "user", "message": {"content": [block]}}), encoding="utf-8")
            out = Path(tmp) / "digest.md"
            subprocess.run([sys.executable, "-X", "utf8", "-I", str(ROOT / "tools/digest_sessions.py"), str(logs), str(out)],
                           check=True, capture_output=True)
            self.assertIn("tool errors: 1 (denied 0); hook denials: 1", out.read_text(encoding="utf-8"))

    def test_session_digest_accepts_stream_system_messages(self):
        # Native CLI stream-json has string messages for permission denials.
        with tempfile.TemporaryDirectory() as tmp:
            logs = Path(tmp) / "logs"
            logs.mkdir()
            rows = [
                {"type": "system", "subtype": "permission_denied", "message": "Permission denied"},
                {"type": "system", "message": "status"},
                {"type": "user", "message": {"content": "Continue the approved task"}},
                None,
            ]
            (logs / "s1.jsonl").write_text("\n".join(json.dumps(row) for row in rows), encoding="utf-8")
            out = Path(tmp) / "digest.md"
            result = subprocess.run([sys.executable, "-X", "utf8", "-I",
                                     str(ROOT / "tools/digest_sessions.py"), str(logs), str(out)],
                                    capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(result.returncode, 0, result.stderr)
            text = out.read_text(encoding="utf-8")
            self.assertIn("human messages: 1", text)
            self.assertIn("Continue the approved task", text)
            self.assertIn("host permission denials: 1", text)
            self.assertIn("tool errors: 0", text)

    def run_digest(self, rows, *flags):
        with tempfile.TemporaryDirectory() as tmp:
            logs = Path(tmp) / "logs"
            logs.mkdir()
            (logs / "s1.jsonl").write_text("\n".join(json.dumps(row) for row in rows), encoding="utf-8")
            out = Path(tmp) / "digest.md"
            subprocess.run([sys.executable, "-X", "utf8", "-I", str(ROOT / "tools/digest_sessions.py"),
                            str(logs), str(out), *flags], check=True, capture_output=True)
            return out.read_text(encoding="utf-8")

    def session_rows(self):
        """T2 of 2026-11-15-workflow-redesign: approvals repeated after gate refusals, as in the owner's session."""
        deny = lambda reason: {"type": "user", "message": {"content": [{"type": "tool_result", "is_error": True,
                               "content": f"PreToolUse:Bash hook error: workflow-axa: `cp` into a.sh {reason}"}]}}
        human = lambda text: {"type": "user", "timestamp": "2026-11-14T00:00:00Z", "message": {"content": text}}
        return [human("Agree no need for report just docs and agents.md"), human("Approve"),
                deny("needs implementation approval, but the task has no plan report (no .html file)"),
                human("approve r1, no report"), deny("was stopped because the current task changed to b"),
                human("ok"), human("Base directory for this skill: D:\\x\\skills\\workflow"),
                human("Find out why the document has not been created and then fix it")]

    def test_session_digest_counts_approvals_process_turns_and_denial_reasons(self):
        text = self.run_digest(self.session_rows())
        self.assertIn("approval messages: 3; process-only turns: 3;", text)
        self.assertIn("'no plan report': 1", text)
        self.assertIn("'task switch': 1", text)
        self.assertNotIn("Base directory for this skill", text)

    def test_a_request_after_an_assent_is_not_counted_as_approval_or_process(self):
        human = lambda text: {"type": "user", "message": {"content": text}}
        rows = [human(t) for t in ("go investigate the bug", "yes, change the database schema", "ok but only src/",
                                   "Approve both", "approve r4, no report", "done.")]
        self.assertIn("approval messages: 2; process-only turns: 3;", self.run_digest(rows))

    def test_session_digest_counts_mode_has_no_message_text(self):
        text = self.run_digest(self.session_rows(), "--counts")
        self.assertIn("heuristics", text)
        self.assertIn("workflow-axa hook refusals only", text)
        self.assertIn("| s1 | 2026-11-14 | 5 | 3 | 3 | 2 | no plan report 1, task switch 1 |", text)
        self.assertNotIn("Approve", text)
        self.assertNotIn("document", text)

    def test_session_digest_hides_secrets_and_counts_typed_commands(self):
        # Hooqd retro: a pasted server password reached the digest, and a typed /workflow showed as "skills: []".
        with tempfile.TemporaryDirectory() as tmp:
            logs = Path(tmp) / "logs"
            logs.mkdir()
            typed = ("<command-message>workflow</command-message>\n<command-name>/workflow</command-name>\n"
                     "<command-args>bug, ssh credentials sqoore EXAMPLEnotArealSecret9, token: abc123</command-args>")
            lines = [{"type": "user", "timestamp": "2026-11-03T14:11:00Z", "message": {"content": typed}},
                     {"type": "user", "timestamp": "2026-11-03T14:12:00Z", "message": {"content": "password=hunter2 please"}}]
            (logs / "s1.jsonl").write_text("\n".join(json.dumps(l) for l in lines), encoding="utf-8")
            out = Path(tmp) / "digest.md"
            subprocess.run([sys.executable, "-X", "utf8", "-I", str(ROOT / "tools/digest_sessions.py"), str(logs), str(out)],
                           check=True, capture_output=True)
            text = out.read_text(encoding="utf-8")
        for secret in ("EXAMPLEnotArealSecret9", "abc123", "hunter2"):
            self.assertNotIn(secret, text)
        self.assertIn("<redacted>", text)
        self.assertIn("skills: ['/workflow']", text)


if __name__ == "__main__":
    unittest.main()
