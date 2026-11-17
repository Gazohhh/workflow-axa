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

    def test_unslop_tells_are_numbered_and_24_is_not_adopted(self):
        """Agreement 1 R7: namespaced ids, overlaps name their rule and add nothing, Unslop 24 refused, figurative use only."""
        import re
        text = TEXT.read_text(encoding="utf-8")
        self.assertIn("## Unslop tells", text)
        section = text.split("## Unslop tells", 1)[1].split("\n## ", 1)[0]
        ids = {int(n) for n in re.findall(r"Unslop (\d+)", section)}
        self.assertLessEqual({3, 5, 8, 12, 13, 14, 17, 19, 24, 26, 27, 30, 32, 33}, ids)
        row = next(l for l in section.splitlines() if l.startswith("| Unslop 24 "))
        self.assertIn("Not adopted", row)
        self.assertIn("literal technical sense stays", " ".join(section.split()))
        for overlap in ("| Unslop 3 | Rule 4. |", "| Unslop 11 | Rule 8. |", "| Unslop 28 | Rule 1. |",
                        "| Unslop 29 | Rule 4. |", "| Unslop 9, 10, 23, 25 | Rule 10. |"):
            self.assertIn(overlap, section.splitlines())
        document = text.split("## The Document", 1)[1].split("\n## ", 1)[0]
        for rule in range(1, 13):
            self.assertRegex(document, rf"(?m)^{rule}\. ", f"rule {rule} of The Document must keep its number")

    def test_writing_runs_unslop_before_the_cold_reader_check(self):
        writing = (ROOT / "skills/workflow/WRITING.md").read_text(encoding="utf-8")
        self.assertLess(writing.index("## Unslop"), writing.index("## Cold-reader check"))
        section = " ".join(writing.split("## Unslop", 1)[1].split("\n## ", 1)[0].split())
        for phrase in ("[SIMPLE-ENGLISH.md](SIMPLE-ENGLISH.md)", "before `record.py offer create`",
                       "The presented offer text is never edited", "The delivery chat report",
                       "Changed prose in a code review", "Commit and PR text", "\"Keep the meaning\" wins over every tell",
                       "never changes application UI copy, error messages or translations",
                       "A README or a guide is a doc, not application text"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, section)

    def test_vocabulary_tells_are_in_word_swaps_once(self):
        swaps = (ROOT / "skills/workflow/simple-english/word-swaps.md").read_text(encoding="utf-8")
        rows = [l.split("|")[1].strip() for l in swaps.splitlines() if l.startswith("| ") and not l.startswith("| Slop")]
        words = [w.strip() for row in rows for w in row.split(",")]
        for word in ("additionally", "serves as", "substrate", "flywheel"):
            with self.subTest(word=word):
                self.assertTrue(any(w.startswith(word) for w in words), word)
        self.assertEqual(len(words), len(set(words)), "a word appears in two rows")

    def test_writing_steps_point_to_the_check(self):
        import sys
        sys.path.insert(0, str(ROOT / "tests"))
        from test_new_skills import assert_mit_licence, pointer_targets
        writing = (ROOT / "skills/workflow/WRITING.md").resolve()
        simple = TEXT.resolve()
        for relative, target, phrase in (
                ("skills/workflow-deliver/SKILL.md", writing, "Unslop check"),
                ("skills/workflow-specify/SKILL.md", writing, "Unslop check"),
                ("skills/code-review/SKILL.md", writing, "Unslop check"),
                ("skills/workflow/flows/docs-tests.md", writing, "Unslop check"),
                ("skills/writing-for-agents/SKILL.md", simple, "Unslop tells")):
            with self.subTest(file=relative):
                self.assertIn(phrase, (ROOT / relative).read_text(encoding="utf-8"))
                self.assertIn(target, pointer_targets(relative, target.name))
        agents = " ".join((ROOT / "skills/writing-for-agents/SKILL.md").read_text(encoding="utf-8").split())
        self.assertIn("leading words", agents.split("Unslop tells", 1)[1][:400])
        assert_mit_licence(self, "skills/workflow/UNSLOP.LICENSE", "Lauren Tan")

    def test_unslop_has_an_observed_run_case(self):
        cases = json.loads((ROOT / "tests/behavioral/cases.json").read_text(encoding="utf-8"))["cases"]
        case = next(c for c in cases if c["id"] == "B30")
        self.assertEqual((case["mode"], case["result"]), ("live-host", "NOT_RUN"))
        expect = " ".join(case["expect"])
        for part in ("'may' stays", "`export --dry-run` stays unchanged", "'vector' stays",
                     "\"Export failed: 3 rows rejected\" stays unchanged"):
            self.assertIn(part, expect)
        self.assertIn("Export failed: 3 rows rejected", case["prompt"])

    def test_report_steps_load_it(self):
        for path in ("skills/codebase-map/TASK-REPORT.md", "skills/workflow/VISUAL-REVIEW.md", "skills/workflow-deliver/SKILL.md"):
            self.assertIn("SIMPLE-ENGLISH.md", (ROOT / path).read_text(encoding="utf-8"), path)


if __name__ == "__main__":
    unittest.main()
