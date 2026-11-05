"""Audit hardening T3, T4 and T6: stop routes, baselines by test identity, and the small-change route."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
COMPARE = SKILLS / "workflow/scripts/compare_failures.py"


def text(rel: str) -> str:
    return " ".join((SKILLS / rel).read_text(encoding="utf-8").split())


class StopRouteTests(unittest.TestCase):
    """E21: a stop could bounce deliver -> execute and send the agent back into building."""

    def test_task_folder_defines_stop_pause_cancel_and_their_route(self):
        folder = text("workflow/TASK-FOLDER.md")
        self.assertIn("## Stop, pause and cancel", folder)
        for state in ("paused", "stopped", "cancelled"):
            self.assertIn(state, folder)
        self.assertIn("never goes back to `workflow-execute`", folder)
        self.assertIn("- Changed files:", folder)
        self.assertIn("reviewer fails twice", folder)

    def test_deliver_records_a_stop_instead_of_handing_back(self):
        deliver = text("workflow-deliver/SKILL.md")
        self.assertIn("unless the task is stopped, paused, cancelled or lightweight", deliver)
        self.assertIn("delivered as partial", deliver)

    def test_execute_stops_building_when_the_owner_says_stop(self):
        execute = text("workflow-execute/SKILL.md")
        self.assertIn("the owner has not said stop, pause or cancel", execute)
        self.assertIn("never comes back here unless the owner asks to continue", execute)

    def test_handoff_message_names_partial_states_and_changed_files(self):
        prompts = text("workflow/CHATGPT-PROMPTS.md")
        self.assertIn("paused / stopped / cancelled / partial", prompts)
        self.assertIn("Changed files:", prompts)
        self.assertIn("Not tested:", prompts)


class BaselineIdentityTests(unittest.TestCase):
    """E11-E13: failures were attributed by count, and baselines were reused without checking their inputs."""

    def run_compare(self, before, after):
        with tempfile.TemporaryDirectory() as tmp:
            b, a = Path(tmp, "before.txt"), Path(tmp, "after.txt")
            b.write_text("\n".join(before) + "\n", encoding="utf-8")
            a.write_text("\n".join(after) + "\n", encoding="utf-8")
            return subprocess.run([sys.executable, "-X", "utf8", "-I", str(COMPARE), str(b), str(a)],
                                  capture_output=True, text=True, encoding="utf-8")

    def test_five_existing_becoming_four_plus_one_new_is_not_unchanged(self):
        before = [f"t{i}\tAssertionError: old {i}" for i in range(1, 6)]
        after = before[:4] + ["t9\tTypeError: new"]
        result = self.run_compare(before, after)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("NEW t9", result.stdout)
        self.assertIn("FIXED t5", result.stdout)
        self.assertIn("EXISTING 4", result.stdout)

    def test_same_test_failing_differently_is_changed_not_existing(self):
        result = self.run_compare(["t1\tAssertionError: a"], ["t1\tKeyError: b"])
        self.assertEqual(result.returncode, 1)
        self.assertIn("CHANGED t1", result.stdout)

    def test_identical_failures_pass(self):
        result = self.run_compare(["t1\tAssertionError: a"], ["t1\tAssertionError: a"])
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_bad_input_is_refused_instead_of_guessed(self):
        # T3/T4/T6 review: a BOM gave a false NEW, duplicates and tab-less lines were silently accepted.
        with tempfile.TemporaryDirectory() as tmp:
            bom = Path(tmp, "bom.txt")
            bom.write_bytes("﻿t1\tAssertionError: a\n".encode("utf-8"))
            plain = Path(tmp, "plain.txt")
            plain.write_text("t1\tAssertionError: a\n", encoding="utf-8")
            run = lambda *files: subprocess.run([sys.executable, "-X", "utf8", "-I", str(COMPARE), *map(str, files)],
                                                capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(run(bom, plain).returncode, 0)
            dup = Path(tmp, "dup.txt")
            dup.write_text("t1\tA\nt1\tB\n", encoding="utf-8")
            self.assertEqual(run(dup, plain).returncode, 2)
            notab = Path(tmp, "notab.txt")
            notab.write_text("t1 AssertionError\n", encoding="utf-8")
            self.assertIn("line 1", run(notab, plain).stdout)
            self.assertEqual(run(Path(tmp, "missing.txt"), plain).returncode, 2)

    def test_execute_and_task_folder_require_identity_and_valid_inputs(self):
        execute = text("workflow-execute/SKILL.md")
        self.assertNotIn("attributed by number", execute)
        self.assertIn("compare_failures.py", execute)
        self.assertIn("after the last repair", execute)
        folder = text("workflow/TASK-FOLDER.md")
        for field in ("command", "commit", "diff", "environment"):
            self.assertIn(field, folder.split("## Baseline before this change", 1)[1][:900])


class SmallRouteTests(unittest.TestCase):
    """E9, E10: a fresh worker for every ticket and a second review of an unchanged diff."""

    def test_small_route_and_escalation_are_defined(self):
        execute = text("workflow-execute/SKILL.md")
        self.assertIn("Small route", execute)
        self.assertIn("leaves the small route", execute)
        self.assertIn("Never review a diff again that has not changed", execute)
        self.assertNotIn("even a single one", execute)

    def test_phase_note_no_longer_demands_a_worker_for_a_two_line_edit(self):
        reads = (ROOT / "hooks/phase_reads.py").read_text(encoding="utf-8")
        self.assertNotIn("even a two-line edit", reads)
        self.assertNotIn("Re-review every repair", reads)
        self.assertIn("small route", reads)


if __name__ == "__main__":
    unittest.main()
