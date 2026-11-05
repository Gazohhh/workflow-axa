"""phase_reads hook: when a phase skill loads, the agent is told exactly which files to read (design retros E36-E41)."""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "hooks/phase_reads.py"


def fire(event):
    env = dict(os.environ, CLAUDE_PLUGIN_ROOT=str(ROOT))
    result = subprocess.run([sys.executable, "-X", "utf8", "-I", str(HOOK)], input=json.dumps(event),
                            capture_output=True, text=True, encoding="utf-8", env=env)
    return result.returncode, result.stdout.strip()


class PhaseReadsHookTests(unittest.TestCase):
    def test_each_phase_names_existing_files_with_full_paths(self):
        for skill, expected in (("workflow-axa:workflow-clarify", "grilling"), ("workflow-specify", "UI-FLOW.md"),
                                ("workflow-axa:workflow-execute", "VERIFY.md"), ("workflow-deliver", "simple-english")):
            with self.subTest(skill=skill):
                code, out = fire({"tool_name": "Skill", "tool_input": {"skill": skill}})
                self.assertEqual(code, 0)
                note = json.loads(out)["hookSpecificOutput"]["additionalContext"]
                self.assertIn(expected, note)
                self.assertIn("Read once", note)
                self.assertIn("Only when applicable", note)
                import re
                files = re.findall(re.escape(str(ROOT / "skills")) + r"[/\\][^;\n]+?\.md", note)
                self.assertTrue(files, note)
                for path in files:
                    self.assertTrue(Path(path.strip()).is_file(), path)
        note = json.loads(fire({"tool_name": "Skill", "tool_input": {"skill": "workflow-execute"}})[1])["hookSpecificOutput"]["additionalContext"]
        self.assertIn("phase skill.md owns", note.lower())
        self.assertIn("small route", note.lower())
        # Specific UI, question and capture procedures have one authoritative home,
        # rather than being duplicated into every phase-loading hook.
        clarify = (ROOT / "skills/workflow-clarify/SKILL.md").read_text(encoding="utf-8")
        specify = (ROOT / "skills/workflow-specify/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("grilling", clarify)
        self.assertIn("report", specify)

    def test_router_load_points_to_the_phase_skill(self):
        note = json.loads(fire({"tool_name": "Skill", "tool_input": {"skill": "workflow-axa:workflow"}})[1])
        self.assertIn("Ask no behavior or design question from the router", note["hookSpecificOutput"]["additionalContext"])

    def test_typed_slash_command_gets_the_same_note(self):
        # A typed /workflow-axa:workflow expands without a Skill tool call.
        out = json.loads(fire({"hook_event_name": "UserPromptSubmit", "prompt": "/workflow-axa:workflow add a badge"})[1])
        self.assertEqual(out["hookSpecificOutput"]["hookEventName"], "UserPromptSubmit")
        self.assertIn("Ask no behavior or design question", out["hookSpecificOutput"]["additionalContext"])
        out = json.loads(fire({"hook_event_name": "UserPromptSubmit", "prompt": "/workflow-clarify"})[1])
        self.assertIn("grilling", out["hookSpecificOutput"]["additionalContext"])
        self.assertEqual(fire({"hook_event_name": "UserPromptSubmit", "prompt": "fix the login bug"}), (0, ""))
        # Round 8: in plan mode the prompt arrived in the <command-name> form and the note never fired.
        out = fire({"hook_event_name": "UserPromptSubmit",
                    "prompt": "<command-message>workflow</command-message>\n<command-name>/workflow-axa:workflow</command-name>\n<command-args>continue x</command-args>"})[1]
        self.assertIn("Ask no behavior or design question", out)

    def test_other_skills_and_bad_input_are_silent(self):
        self.assertEqual(fire({"tool_name": "Skill", "tool_input": {"skill": "tdd"}}), (0, ""))
        self.assertEqual(fire({"tool_name": "Bash", "tool_input": {"command": "ls"}}), (0, ""))
        result = subprocess.run([sys.executable, "-X", "utf8", "-I", str(HOOK)], input="nope", capture_output=True, text=True)
        self.assertEqual((result.returncode, result.stdout), (0, ""))

    def test_hooks_json_wires_it_for_skill(self):
        entries = json.loads((ROOT / "hooks/hooks.json").read_text(encoding="utf-8"))["hooks"]["PostToolUse"]
        skill = [e for e in entries if e["matcher"] == "Skill"]
        self.assertEqual(len(skill), 1)
        self.assertIn("${CLAUDE_PLUGIN_ROOT}/hooks/phase_reads.py", skill[0]["hooks"][0]["command"])


if __name__ == "__main__":
    unittest.main()
