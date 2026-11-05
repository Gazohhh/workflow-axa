"""The truncated-read hook warns on partial reads of package instruction files and stays silent otherwise (D13)."""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "hooks/truncated_read.py"
PACKAGE = ROOT.as_posix()  # actual package root, including marketplace names and spaces


def bash_path(path):
    """D:/x -> /d/x, the Git Bash form; POSIX paths are unchanged."""
    return re.sub(r"^([A-Za-z]):", lambda m: "/" + m.group(1).lower(), path)


def fire(event, plugin_root=None):
    env = dict(os.environ, CLAUDE_PLUGIN_ROOT=plugin_root or PACKAGE)
    result = subprocess.run([sys.executable, "-X", "utf8", "-I", str(HOOK)], input=json.dumps(event),
                            capture_output=True, text=True, encoding="utf-8", env=env)
    return result.returncode, result.stdout.strip()


class TruncatedReadHookTests(unittest.TestCase):
    def test_partial_bash_read_of_package_file_warns(self):
        workflow = f"{PACKAGE}/skills/workflow"
        code, out = fire({"tool_name": "Bash", "tool_input": {"command": f'cd "{workflow}" && cat RULES.md TASK-FOLDER.md | head -150; sed -n 1,80p "{workflow}/TASK-FOLDER.md"'}})
        self.assertEqual(code, 0)
        note = json.loads(out)["hookSpecificOutput"]
        self.assertEqual(note["hookEventName"], "PostToolUse")
        self.assertIn("TASK-FOLDER.md", note["additionalContext"])

    @unittest.skipUnless(re.match(r"^[A-Za-z]:", PACKAGE), "Windows paths only")
    def test_windows_paths_match_in_any_case_and_show_as_typed(self):
        # rc3 trial: the warning named "task-folder.md" because Windows paths were case-folded for display too.
        typed = PACKAGE.upper() + "/skills/workflow/TASK-FOLDER.md"
        out = fire({"tool_name": "Bash", "tool_input": {"command": f'head -20 "{typed}"'}})[1]
        context = json.loads(out)["hookSpecificOutput"]["additionalContext"]
        self.assertIn("TASK-FOLDER.md", context)
        self.assertNotIn("task-folder.md", context)
        out = fire({"tool_name": "Bash", "tool_input": {"command": f'cd "{PACKAGE}/skills" && head -5 workflow/TASK-FOLDER.md'}})[1]
        self.assertIn(f"{PACKAGE}/skills/workflow/TASK-FOLDER.md", json.loads(out)["hookSpecificOutput"]["additionalContext"])

    def test_relative_path_after_cd_into_package_warns(self):
        # Design-loop run: `cd /d/workflow-axa/skills && cat rule-maker/rules/READINESS.md | head -80` slipped through.
        code, out = fire({"tool_name": "Bash", "tool_input": {"command": f'cd "{bash_path(PACKAGE)}/skills" && ls; cat rule-maker/rules/READINESS.md 2>/dev/null | head -20'}})
        self.assertIn("READINESS.md", json.loads(out)["hookSpecificOutput"]["additionalContext"])

    def test_partial_read_tool_warns_and_whole_read_is_silent(self):
        path = PACKAGE.replace("/", "\\") + "\\skills\\workflow-execute\\SKILL.md"  # Windows separators
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
        skills = f"{PACKAGE}/skills"
        lines = len(Path(skills, "workflow/RULES.md").read_text(encoding="utf-8").splitlines())
        for command in (f'cd "{skills}" && grep -n gate workflow/RULES.md | head -5' ,
                        f'python "{skills}/codebase-map/scripts/render_report.py" --help | head -30' ,
                        f'cat "{skills}/workflow/RULES.md" | head -{lines}' ,
                        f'sed -n 1,{lines}p "{skills}/workflow/RULES.md"' ,
                        f'cd "{skills}" && cat workflow/RULES.md; cd D:/proj && sed -n 1,20p docs/plans/t/PLAN.md' ):
            with self.subTest(command=command):
                self.assertEqual(fire({"tool_name": "Bash", "tool_input": {"command": command}}), (0, ""))
        out = fire({"tool_name": "Bash", "tool_input": {"command": f'cat "{skills}/workflow/RULES.md" | head -{lines - 1}'}})[1]
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
        out = fire({"tool_name": "Bash", "tool_input": {"command": f'cd "{PACKAGE}/skills/workflow" && grep -n "" VISUAL-REVIEW.md | sed -n 1,20p'}})[1]
        self.assertIn("VISUAL-REVIEW.md", out)

    def test_hooks_json_wires_the_script_for_bash_and_read(self):
        data = json.loads((ROOT / "hooks/hooks.json").read_text(encoding="utf-8"))
        entry = data["hooks"]["PostToolUse"][0]
        self.assertEqual(entry["matcher"], "Bash|Read")
        self.assertIn("${CLAUDE_PLUGIN_ROOT}/hooks/truncated_read.py", entry["hooks"][0]["command"])


if __name__ == "__main__":
    unittest.main()
