"""The truncated-read hook warns on partial reads of package instruction files and stays silent otherwise (D13)."""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "hooks/truncated_read.py"


def fire(event, plugin_root="D:/workflow-axa"):
    env = dict(os.environ, CLAUDE_PLUGIN_ROOT=plugin_root)
    result = subprocess.run([sys.executable, "-X", "utf8", "-I", str(HOOK)], input=json.dumps(event),
                            capture_output=True, text=True, encoding="utf-8", env=env)
    return result.returncode, result.stdout.strip()


class TruncatedReadHookTests(unittest.TestCase):
    def test_partial_bash_read_of_package_file_warns(self):
        code, out = fire({"tool_name": "Bash", "tool_input": {"command": "cd D:/workflow-axa/skills/workflow && cat RULES.md TASK-FOLDER.md | head -150; sed -n 1,80p D:/workflow-axa/skills/workflow/TASK-FOLDER.md"}})
        self.assertEqual(code, 0)
        note = json.loads(out)["hookSpecificOutput"]
        self.assertEqual(note["hookEventName"], "PostToolUse")
        self.assertIn("TASK-FOLDER.md", note["additionalContext"])

    def test_relative_path_after_cd_into_package_warns(self):
        # Design-loop run: `cd /d/workflow-axa/skills && cat rule-maker/rules/READINESS.md | head -80` slipped through.
        code, out = fire({"tool_name": "Bash", "tool_input": {"command": "cd /d/workflow-axa/skills && ls; cat rule-maker/rules/READINESS.md 2>/dev/null | head -20"}})
        self.assertIn("READINESS.md", json.loads(out)["hookSpecificOutput"]["additionalContext"])

    def test_partial_read_tool_warns_and_whole_read_is_silent(self):
        path = "D:\\workflow-axa\\skills\\workflow-execute\\SKILL.md"
        self.assertIn("read only part", fire({"tool_name": "Read", "tool_input": {"file_path": path, "limit": 40}})[1])
        self.assertEqual(fire({"tool_name": "Read", "tool_input": {"file_path": path}}), (0, ""))
        self.assertEqual(fire({"tool_name": "Read", "tool_input": {"file_path": path, "offset": 40}}), (0, ""))

    def test_other_files_and_bad_input_are_ignored(self):
        self.assertEqual(fire({"tool_name": "Bash", "tool_input": {"command": "git log | head -5; sed -n 1,9p src/app/README.md"}}), (0, ""))
        self.assertEqual(fire({"tool_name": "Read", "tool_input": {"file_path": "D:/proj/docs/plan.md", "limit": 10}}), (0, ""))
        result = subprocess.run([sys.executable, "-X", "utf8", "-I", str(HOOK)], input="not json", capture_output=True, text=True)
        self.assertEqual((result.returncode, result.stdout), (0, ""))

    def test_no_false_warnings_from_round_six(self):
        # Round-6 retro: five warnings, all false; agents learned to ignore the hook.
        skills = "D:/workflow-axa/skills"
        lines = len((ROOT / "skills/workflow/RULES.md").read_text(encoding="utf-8").splitlines())
        for command in (f"cd {skills} && grep -n gate workflow/RULES.md | head -5",
                        f"python {skills}/codebase-map/scripts/render_report.py --help | head -30",
                        f"cat {skills}/workflow/RULES.md | head -{lines}",
                        f"sed -n 1,{lines}p {skills}/workflow/RULES.md",
                        f"cd {skills} && cat workflow/RULES.md; cd D:/proj && sed -n 1,20p docs/plans/t/PLAN.md"):
            with self.subTest(command=command):
                self.assertEqual(fire({"tool_name": "Bash", "tool_input": {"command": command}}), (0, ""))
        out = fire({"tool_name": "Bash", "tool_input": {"command": f"cat {skills}/workflow/RULES.md | head -{lines - 1}"}})[1]
        self.assertIn("read only part of", out)

    def test_in_place_record_edits_point_to_record_py(self):
        for command in ("sed -i 's/old/new/' docs/plans/t/PLAN.md", "cat note.txt >> docs/plans/t/FINDINGS.md",
                        "python - <<'E'\np='TODO.md';t=open(p).read().replace('a','b')\nE"):
            with self.subTest(command=command):
                out = fire({"tool_name": "Bash", "tool_input": {"command": command}})[1]
                self.assertIn("record.py", out)
        self.assertEqual(fire({"tool_name": "Bash", "tool_input": {"command": "sed -i 's/a/b/' src/app.ts"}}), (0, ""))
        # Round 17: the record name hidden in a shell variable, and grep "" printing a whole package file.
        self.assertIn("record.py", fire({"tool_name": "Bash", "tool_input": {"command": "F=docs/plans/t/PLAN.md; sed -i 's/a/b/' $F"}})[1])
        out = fire({"tool_name": "Bash", "tool_input": {"command": 'cd D:/workflow-axa/skills/workflow && grep -n "" VISUAL-REVIEW.md | sed -n 1,20p'}})[1]
        self.assertIn("VISUAL-REVIEW.md", out)

    def test_hooks_json_wires_the_script_for_bash_and_read(self):
        data = json.loads((ROOT / "hooks/hooks.json").read_text(encoding="utf-8"))
        entry = data["hooks"]["PostToolUse"][0]
        self.assertEqual(entry["matcher"], "Bash|Read")
        self.assertIn("${CLAUDE_PLUGIN_ROOT}/hooks/truncated_read.py", entry["hooks"][0]["command"])


if __name__ == "__main__":
    unittest.main()
