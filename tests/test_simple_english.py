"""SIMPLE-ENGLISH.md (formerly the simple-english skill): ships with its licence; the report steps load it (owner request 2026-11-03, moved in T22)."""
from __future__ import annotations

import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
TEXT = ROOT / "skills/workflow/SIMPLE-ENGLISH.md"


class SimpleEnglishTests(unittest.TestCase):
    def test_registered_with_license_and_protected_text(self):
        plugin = json.loads((ROOT / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
        self.assertNotIn("./skills/simple-english", plugin["skills"])
        self.assertIn("MIT License", (ROOT / "skills/workflow/SIMPLE-ENGLISH.LICENSE").read_text(encoding="utf-8"))
        text = TEXT.read_text(encoding="utf-8")
        self.assertIn("DESIGN.md rule 4's question, which is quoted word for word", text)

    def test_its_reference_files_ship_beside_it(self):
        # Opus T22 review: the CHECK and Strict modes pointed at files left only in the archive.
        import re
        names = re.findall(r"`(simple-english/[a-z-]+\.md)`", TEXT.read_text(encoding="utf-8"))
        self.assertEqual(sorted(set(names)), ["simple-english/rule-catalog.md", "simple-english/strict-vocabulary.md",
                                              "simple-english/use-cases.md", "simple-english/word-swaps.md"])
        for name in names:
            self.assertTrue((TEXT.parent / name).is_file(), name)
        self.assertNotIn("`references/", TEXT.read_text(encoding="utf-8"))

    def test_report_steps_load_it(self):
        for path in ("skills/codebase-map/TASK-REPORT.md", "skills/workflow/VISUAL-REVIEW.md", "skills/workflow-deliver/SKILL.md"):
            self.assertIn("SIMPLE-ENGLISH.md", (ROOT / path).read_text(encoding="utf-8"), path)


if __name__ == "__main__":
    unittest.main()
