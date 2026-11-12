"""simple-english: registered with its licence; the report steps load it (owner request 2026-11-03)."""
from __future__ import annotations

import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/simple-english"


class SimpleEnglishTests(unittest.TestCase):
    def test_registered_with_license_and_protected_text(self):
        plugin = json.loads((ROOT / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
        self.assertIn("./skills/simple-english", plugin["skills"])
        self.assertIn("MIT License", (SKILL / "LICENSE").read_text(encoding="utf-8"))
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("DESIGN.md rule 4's question, which is quoted word for word", text)

    def test_report_steps_load_it(self):
        for path in ("skills/codebase-map/TASK-REPORT.md", "skills/workflow/VISUAL-REVIEW.md", "skills/workflow-deliver/SKILL.md"):
            self.assertIn("simple-english", (ROOT / path).read_text(encoding="utf-8"), path)


if __name__ == "__main__":
    unittest.main()
