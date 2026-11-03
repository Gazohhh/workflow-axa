"""rules_stamp.py compares a project's 'rules checked' line with the installed rules library (D20)."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/rule-maker/scripts/rules_stamp.py"
INSTALLED = json.loads((ROOT / "skills/rule-maker/rules/version.json").read_text(encoding="utf-8"))["rules_version"]


class RulesStampTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def run_on(self, agents=None, claude=None):
        if agents is not None:
            (self.root / "AGENTS.md").write_text(agents, encoding="utf-8")
        if claude is not None:
            (self.root / "CLAUDE.md").write_text(claude, encoding="utf-8")
        result = subprocess.run([sys.executable, "-X", "utf8", "-I", str(SCRIPT), str(self.root)],
                                capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout

    def test_no_line_runs_the_normal_check_and_offers_the_line(self):
        out = self.run_on(agents="# Rules\n")
        self.assertIn("STATE: NONE", out)
        self.assertIn(f"workflow-axa rules checked: {INSTALLED} (YYYY-MM-DD)", out)

    def test_current_line_says_nothing(self):
        out = self.run_on(agents=f"# Rules\n\nworkflow-axa rules checked: {INSTALLED} (2026-11-03)\n")
        self.assertIn(f"STATE: CURRENT {INSTALLED}", out)
        self.assertNotIn("## ", out)

    def test_behind_lists_only_newer_changes_and_never_blocks(self):
        out = self.run_on(claude="@AGENTS.md\nworkflow-axa rules checked: 1.5.0 (2026-10-30)\n")
        self.assertIn("STATE: BEHIND project 1.5.0 (CLAUDE.md", out)
        self.assertIn("## 1.7.0", out)
        self.assertIn("never write CSS", out)
        self.assertNotIn("## 1.5.0", out)
        self.assertNotIn("## 1.3.0", out)
        self.assertIn("Never block", out)

    def test_ahead_points_to_the_install(self):
        self.assertIn("STATE: AHEAD", self.run_on(agents="workflow-axa rules checked: 99.0.0 (2030-01-01)\n"))

    def test_every_version_has_a_changes_entry(self):
        text = (ROOT / "skills/rule-maker/rules/CHANGES.md").read_text(encoding="utf-8")
        self.assertIn(f"## {INSTALLED} ", text)
        self.assertIn("CHANGES.md", json.loads((ROOT / "skills/rule-maker/rules/version.json").read_text(encoding="utf-8"))["files"])

    def test_bad_usage(self):
        result = subprocess.run([sys.executable, "-X", "utf8", "-I", str(SCRIPT)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)


if __name__ == "__main__":
    unittest.main()
