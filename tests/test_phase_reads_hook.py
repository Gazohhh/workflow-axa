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
                files = note.split("live there): ")[1].split(". The ui-design")[0].split("; ")
                for path in files:
                    self.assertTrue(Path(path).is_file(), path)
        self.assertIn("class_rules.py", fire({"tool_name": "Skill", "tool_input": {"skill": "workflow-clarify"}})[1])
        # Round 9: a bold-heading copy was still recommended, without the exact question.
        self.assertIn("recommend none", fire({"tool_name": "Skill", "tool_input": {"skill": "workflow-clarify"}})[1])
        # Round 10: deliver fixed a check after reconciliation and did not reconcile again.
        self.assertIn("reconciliation again in a fresh subagent", fire({"tool_name": "Skill", "tool_input": {"skill": "workflow-deliver"}})[1])
        self.assertIn("never offer or recommend skipping it", fire({"tool_name": "Skill", "tool_input": {"skill": "workflow-specify"}})[1])
        self.assertIn("-narrow.png", fire({"tool_name": "Skill", "tool_input": {"skill": "workflow-deliver"}})[1])  # tiny desktop captures
        self.assertIn("--match", fire({"tool_name": "Skill", "tool_input": {"skill": "workflow-execute"}})[1])  # round 15

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
