"""open_items.py: what is still open across task records (retro finding: status questions)."""
from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "skills/workflow/scripts/open_items.py"


def run(root, *extra):
    return subprocess.run([sys.executable, "-X", "utf8", "-I", str(SCRIPT), str(root), *extra],
                          capture_output=True, text=True, encoding="utf-8")


class OpenItemsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def task(self, name, todo, plan=""):
        folder = self.root / name
        folder.mkdir()
        (folder / "TODO.md").write_text(todo, encoding="utf-8")
        if plan:
            (folder / "PLAN.md").write_text(plan, encoding="utf-8")

    def test_classifies_open_unbacked_blocked_and_backed(self):
        self.task("2026-11-01-a", "- [ ] T1 — open work\n- [x] T2 — done; verified: FINDINGS V2\n"
                  "- [x] T3 — ticked with nothing behind it\n- [~] T4 — halfway\n- [ ] T5 — waiting; blocked on Q3\n"
                  "- [x] T6 — legacy; proof: spec passes\n",
                  "## Current checkpoint\n- Updated / phase: 2026-11-01, implementing\n- Last result / next safe action: run T4 check\n")
        out = run(self.root).stdout
        self.assertIn("OPEN: T1", out)
        self.assertIn("TICKED, NO EVIDENCE: T3", out)
        self.assertIn("IN PROGRESS: T4", out)
        self.assertIn("BLOCKED: T5", out)
        self.assertNotIn("T2", out)
        self.assertNotIn("T6", out)
        self.assertIn("phase: 2026-11-01, implementing", out)
        self.assertIn("next: run T4 check", out)

    def test_finished_task_is_counted_but_not_listed(self):
        self.task("done", "- [x] T1 — finished V1\n")
        out = run(self.root).stdout
        self.assertIn("1 tasks with TODO.md; 0 with open", out)
        self.assertNotIn("## done", out)

    def test_task_view_shows_checkpoint_outcome_and_record_problems(self):
        self.task("t", "- [ ] T1 — open\n- [x] T2 — done V1\n",
                  "# T\n\n## Current checkpoint\n- Next safe action: run T1\n\n## Outcome r2\nDelivered partial.\n")
        folder = self.root / "t"
        (folder / "FINDINGS.md").write_bytes(b"# F\r\nline\n\x97 bad\r\n")
        out = run("--task", folder).stdout
        self.assertIn("- Next safe action: run T1", out)
        self.assertIn("## Latest Outcome r2\nDelivered partial.", out)
        self.assertIn("- OPEN: T1", out)
        self.assertIn("FINDINGS.md: not valid UTF-8", out)
        self.assertIn("FINDINGS.md: mixed line endings", out)
        self.assertEqual(run("--task", self.root / "missing").returncode, 2)

    def test_non_ascii_output_survives_a_cp1252_console(self):
        # Design loop: open_items crashed on a Windows console because an Outcome contained "−".
        self.task("t", "- [ ] T1 — open\n", "# T\n\n## Current checkpoint\n- Next safe action: x − y\n")
        env = dict(os.environ, PYTHONIOENCODING="cp1252", PYTHONUTF8="0")
        result = subprocess.run([sys.executable, "-I", str(SCRIPT), "--task", self.root / "t"],
                                capture_output=True, env=env)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_folders_without_todo_are_ignored_and_bad_root_blocks(self):
        (self.root / "notes").mkdir()
        self.assertIn("0 tasks", run(self.root).stdout)
        result = run(self.root / "missing")
        self.assertEqual(result.returncode, 2)
        self.assertIn("BLOCKED", result.stdout)


if __name__ == "__main__":
    unittest.main()
