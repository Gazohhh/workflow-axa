"""The phase gate blocks code edits and git commit/push/merge after /workflow until a phase skill has run."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "hooks/phase_gate.py"
ROUTER = {"type": "user", "message": {"role": "user", "content":
          "<command-message>workflow</command-message>\n<command-name>/workflow</command-name>\n<command-args>bug</command-args>"}}


def skill(name):
    return {"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "Skill", "input": {"skill": name}}]}}


def say(text):
    return {"type": "assistant", "message": {"content": [{"type": "text", "text": text}]}}


class PhaseGateHookTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "session.jsonl"

    def fire(self, rows, tool, tool_input, cwd="D:\\Hooqd"):
        self.path.write_text("\n".join(json.dumps(row) for row in rows), encoding="utf-8")
        event = {"tool_name": tool, "tool_input": tool_input, "transcript_path": str(self.path), "cwd": cwd}
        result = subprocess.run([sys.executable, "-X", "utf8", "-I", str(HOOK)], input=json.dumps(event),
                                capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0)
        return json.loads(result.stdout)["hookSpecificOutput"] if result.stdout.strip() else None

    def test_hooqd_session_is_blocked_before_code_and_push(self):
        # Hooqd retro: investigation, "Let's do that, push when done", then edits and a push with no phase loaded.
        rows = [ROUTER, say("Waiting on you: should I start the fix as a workflow task?"),
                {"type": "user", "message": {"role": "user", "content": "Let's do that, push when done"}}]
        edit = self.fire(rows, "Edit", {"file_path": "D:\\Hooqd\\frontend\\packages\\api\\src\\transport.ts"})
        self.assertEqual(edit["permissionDecision"], "deny")
        self.assertIn("workflow-clarify", edit["permissionDecisionReason"])
        push = self.fire(rows, "Bash", {"command": "cd /d/Hooqd && git fetch -q && git push -q origin master"})
        self.assertIn("git push", push["permissionDecisionReason"])
        # The Hooqd session also edited source from Bash: sed -i and a Python heredoc writing the file.
        for command in ("cd /d/Hooqd/frontend; sed -i 's/a/b/' apps/operator/src/x.tsx",
                        "cd /d/Hooqd/frontend; python - <<'EOF'\np='packages/api/src/transport.ts'\nopen(p,'w').write(s)\nEOF"):
            with self.subTest(command=command):
                self.assertEqual(self.fire(rows, "Bash", {"command": command})["permissionDecision"], "deny")

    def test_a_project_inside_temp_is_still_gated(self):
        # r24 live check: the project lived under AppData/Local/Temp, and `sed -i` there slipped through.
        project = "C:/Users/x/AppData/Local/Temp/claude/s/scratchpad/r22-short"
        sed = {"command": f'cd "{project}" && sed -i "s/Delete/Erase/" index.html app.js'}
        self.assertEqual(self.fire([ROUTER], "Bash", sed, cwd=project)["permissionDecision"], "deny")
        edit = {"file_path": project + "/index.html"}
        self.assertEqual(self.fire([ROUTER], "Edit", edit, cwd=project)["permissionDecision"], "deny")

    def test_allowed_cases(self):
        rows = [ROUTER]
        for tool, data in (("Write", {"file_path": "D:/Hooqd/docs/plans/2026-11-03-upload-timeout/PLAN.md"}),
                           ("Write", {"file_path": "D:/Hooqd/.artifacts/checks/x.log"}),
                           ("Write", {"file_path": "C:/Users/x/AppData/Local/Temp/scratch/note.md"}),
                           ("Bash", {"command": "cd C:/Users/x/AppData/Local/Temp/scratch && sed -i 's/a/b/' n.txt"}),
                           ("Bash", {"command": "sed -i 's/a/b/' docs/plans/t/TODO.md"}),
                           ("Bash", {"command": "git status --short && git diff"}),
                           ("Read", {"file_path": "D:/Hooqd/backend/app.php"})):
            with self.subTest(tool=tool, data=data):
                self.assertIsNone(self.fire(rows, tool, data))
        code = {"file_path": "D:/Hooqd/frontend/src/a.ts"}
        self.assertIsNone(self.fire(rows + [skill("workflow-axa:workflow-clarify")], "Edit", code))
        self.assertIsNone(self.fire(rows + [say("Lightweight edit: a typo in a code comment.")], "Edit", code))
        self.assertIsNone(self.fire([say("plain session")], "Edit", code))  # no /workflow, no gate

    def test_rule_maker_may_write_rule_files_only(self):
        # D20: rule-maker writes the rules-checked line into AGENTS.md during setup or audit, without a phase.
        rows = [ROUTER, skill("workflow-axa:rule-maker")]
        for tool, data in (("Edit", {"file_path": "D:/Hooqd/AGENTS.md"}),
                           ("Edit", {"file_path": "D:/Hooqd/.claude/rules/frontend.md"}),
                           ("Bash", {"command": "cd /d/Hooqd && sed -i 's/1.7.0/1.8.0/' AGENTS.md"})):
            with self.subTest(data=data):
                self.assertIsNone(self.fire(rows, tool, data))
        self.assertEqual(self.fire(rows, "Edit", {"file_path": "D:/Hooqd/src/a.ts"})["permissionDecision"], "deny")
        self.assertEqual(self.fire([ROUTER], "Edit", {"file_path": "D:/Hooqd/AGENTS.md"})["permissionDecision"], "deny")

    def test_report_render_waits_for_the_report_guides(self):
        # Round v3: in all four worktrees the report guides were read only after the Stop hook asked, so reports
        # were rendered (and in r22 went stale) before the rules for writing them were read.
        render = {"command": "python -X utf8 -I D:/workflow-axa/skills/codebase-map/scripts/render_report.py --input p.json --output p.html"}
        rows = [ROUTER, skill("workflow-axa:workflow-specify")]
        denied = self.fire(rows, "Bash", render)
        self.assertEqual(denied["permissionDecision"], "deny")
        self.assertIn("simple-english/SKILL.md", denied["permissionDecisionReason"])
        self.assertIn("codebase-map/TASK-REPORT.md", denied["permissionDecisionReason"])
        read = lambda rel: {"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "Read",
                            "input": {"file_path": f"D:/workflow-axa/skills/{rel}"}}]}}
        rows += [read("simple-english/SKILL.md"), read("codebase-map/TASK-REPORT.md"), read("codebase-map/UI-FLOW.md")]
        self.assertIsNone(self.fire(rows, "Bash", render))
        self.assertIsNone(self.fire([say("plain session")], "Bash", render))

    def test_bad_input_is_ignored(self):
        result = subprocess.run([sys.executable, "-X", "utf8", "-I", str(HOOK)], input="nope", capture_output=True, text=True)
        self.assertEqual((result.returncode, result.stdout), (0, ""))

    def test_hooks_json_wires_it_before_edits_and_bash(self):
        data = json.loads((ROOT / "hooks/hooks.json").read_text(encoding="utf-8"))
        entry = data["hooks"]["PreToolUse"][0]
        self.assertEqual(entry["matcher"], "Edit|Write|MultiEdit|NotebookEdit|Bash")
        self.assertIn("${CLAUDE_PLUGIN_ROOT}/hooks/phase_gate.py", entry["hooks"][0]["command"])


if __name__ == "__main__":
    unittest.main()
