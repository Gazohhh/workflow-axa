"""The writing rules: WRITING.md owns every common rule and the Unslop check; SIMPLE-ENGLISH.md (formerly the
simple-english skill) keeps only its Strict and CHECK modes, references, licence and credit
(docs/plans/2026-11-17-plain-owner-questions R1, R6, T1)."""
from __future__ import annotations

import json
import re
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
TEXT = ROOT / "skills/workflow/SIMPLE-ENGLISH.md"
WRITING = ROOT / "skills/workflow/WRITING.md"
MODE_SECTIONS = ("## Modes", "## Limits", "## References")


def section(text: str, heading: str) -> str:
    return text.split(heading, 1)[1].split("\n## ", 1)[0]


def numbered_rules_outside_modes(text: str) -> list[str]:
    """Numbered writing rules in a SIMPLE-ENGLISH.md text outside the sections it keeps (its modes)."""
    found = []
    for part in ("\n" + text).split("\n## ")[1:]:
        if ("## " + part).startswith(MODE_SECTIONS):
            continue
        found += re.findall(r"(?m)^\d+\. .+$", part)
    return found


def rule_openings(writing: str) -> list[str]:
    """The first sentence of each numbered rule in "Documents and reports" and "Chat replies"."""
    found = []
    for heading in ("## Documents and reports", "## Chat replies"):
        for line in re.findall(r"(?m)^\d+\. (.+)$", section(writing, heading)):
            found.append(re.split(r"(?<=[.:])\s", line, maxsplit=1)[0])
    return found


def copies(texts: dict[str, str], openings: list[str]) -> list[tuple[str, str]]:
    return [(rel, opening) for rel, text in sorted(texts.items()) for opening in openings
            if len(opening.split()) >= 5 and opening in text]


class SimpleEnglishTests(unittest.TestCase):
    def test_registered_with_license_and_protected_text(self):
        plugin = json.loads((ROOT / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
        self.assertNotIn("./skills/simple-english", plugin["skills"])
        self.assertIn("MIT License", (ROOT / "skills/workflow/SIMPLE-ENGLISH.LICENSE").read_text(encoding="utf-8"))
        self.assertIn("DESIGN.md rule 4's question, which is quoted word for word", WRITING.read_text(encoding="utf-8"))

    def test_its_reference_files_ship_beside_it(self):
        # Opus T22 review: the CHECK and Strict modes pointed at files left only in the archive.
        names = re.findall(r"`(simple-english/[a-z-]+\.md)`", TEXT.read_text(encoding="utf-8"))
        self.assertEqual(sorted(set(names)), ["simple-english/rule-catalog.md", "simple-english/strict-vocabulary.md",
                                              "simple-english/use-cases.md", "simple-english/word-swaps.md"])
        for name in names:
            self.assertTrue((TEXT.parent / name).is_file(), name)
        self.assertNotIn("`references/", TEXT.read_text(encoding="utf-8"))

    def test_only_writing_md_defines_the_common_rules(self):
        """R1: one owner. SIMPLE-ENGLISH.md keeps its modes and points to WRITING.md; a numbered rule anywhere else
        in it fails (the fixture below proves the check bites)."""
        simple = TEXT.read_text(encoding="utf-8")
        self.assertEqual(numbered_rules_outside_modes(simple), [])
        for heading in ("## The Document", "## The Reply", "## Self-Check", "## Unslop tells"):
            self.assertNotIn(heading, simple)
        self.assertIn("[WRITING.md](WRITING.md)", simple)
        planted = simple.replace("## Modes", "## Extra\n\n1. Use short sentences.\n\n## Modes", 1)
        self.assertEqual(numbered_rules_outside_modes(planted), ["1. Use short sentences."])

    def test_no_other_skill_copies_a_writing_rule(self):
        """R1 and R9: a rule of "Documents and reports" or "Chat replies" copied into another skill file fails."""
        rules = rule_openings(WRITING.read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(rules), 14)
        texts = {p.relative_to(ROOT).as_posix(): p.read_text(encoding="utf-8") for p in (ROOT / "skills").rglob("*.md")
                 if p != WRITING}
        self.assertEqual(copies(texts, rules), [])
        texts["skills/tdd/SKILL.md"] += "\n7. No semicolons and no em-dashes. Write two sentences, or name the relation.\n"
        self.assertEqual(copies(texts, rules), [("skills/tdd/SKILL.md", "No semicolons and no em-dashes.")])

    def test_check_mode_names_real_catalog_rules(self):
        """R2: the Plain-mode CHECK instruction points at catalog rules that exist and say what it claims, so a
        renumbered or reworded catalog fails here. The CHECK itself is done by the model (live check, R10)."""
        catalog = (ROOT / "skills/workflow/simple-english/rule-catalog.md").read_text(encoding="utf-8")
        rule = next(l for l in catalog.splitlines() if re.search(r"(^|\W)4\.2(\W|$)", l))
        self.assertIn("contraction", rule.lower())
        self.assertIn("never config, settings, or options", catalog)
        self.assertIn("never check, verify, confirm, validate, or ensure as verbs", catalog)

    def test_unslop_tells_are_numbered_and_24_is_not_adopted(self):
        """Agreement 1 R7 of the pstack task, now in WRITING.md: namespaced ids, overlaps name their rule and add
        nothing, Unslop 24 refused, figurative use only; the twelve document rules keep their numbers."""
        text = WRITING.read_text(encoding="utf-8")
        self.assertIn("## Unslop tells", text)
        tells = section(text, "## Unslop tells")
        ids = {int(n) for n in re.findall(r"Unslop (\d+)", tells)}
        self.assertLessEqual({3, 5, 8, 12, 13, 14, 17, 19, 24, 26, 27, 30, 32, 33}, ids)
        row = next(l for l in tells.splitlines() if l.startswith("| Unslop 24 "))
        self.assertIn("Not adopted", row)
        self.assertIn("literal technical sense stays", " ".join(tells.split()))
        for overlap in ("| Unslop 3 | Rule 4. |", "| Unslop 11 | Rule 8. |", "| Unslop 28 | Rule 1. |",
                        "| Unslop 29 | Rule 4. |", "| Unslop 9, 10, 23, 25 | Rule 10. |"):
            self.assertIn(overlap, tells.splitlines())
        document = section(text, "## Documents and reports")
        for rule in range(1, 13):
            self.assertRegex(document, rf"(?m)^{rule}\. ", f"rule {rule} of the document rules must keep its number")
        self.assertIn("## Chat replies", text)
        self.assertIn("## Self-check", text)

    def test_writing_runs_unslop_before_the_cold_reader_check(self):
        writing = WRITING.read_text(encoding="utf-8")
        self.assertLess(writing.index("## Unslop"), writing.index("## Cold-reader check"))
        unslop = " ".join(section(writing, "## Unslop\n").split())
        for phrase in ("before `record.py offer create`", "The presented offer text is never edited",
                       "The delivery chat report", "Changed prose in a code review", "Commit and PR text",
                       "\"Keep the meaning\" wins over every tell",
                       "never changes application UI copy, error messages or translations",
                       "A README or a guide is a doc, not application text"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, unslop)

    def test_unslop_runs_on_every_new_or_changed_text_and_keeps_history(self):
        """R6: the full scope, and what the check never changes."""
        unslop = " ".join(section(WRITING.read_text(encoding="utf-8"), "## Unslop\n").split()).lower()
        for kind in ("tickets", "plan", "findings", "decisions", "offer", "reports", "spar.md", "docs", "chat"):
            with self.subTest(kind=kind):
                self.assertIn(kind, unslop)
        for kept in ("history", "quoted owner answers", "already-presented approvals"):
            with self.subTest(kept=kept):
                self.assertIn(kept, unslop)
        self.assertIn("new or changed", unslop)

    def test_word_swaps_and_contractions_are_suggestions(self):
        """R2, owner Q3: fixed swaps and the contraction ban are suggestions wherever the rules state them; Strict
        mode keeps them as rules."""
        writing = WRITING.read_text(encoding="utf-8")
        self.assertNotIn("No contractions", writing)
        self.assertNotIn("Use `make sure that` for check", writing)
        rules = section(writing, "## Documents and reports")
        self.assertIn("Writing out contractions is a suggestion, not a rule.", rules)
        self.assertIn("Plainer swaps are suggestions", rules)
        self.assertIn("unless the swap changes the meaning", rules)
        check = " ".join(section(writing, "## Self-check").split())
        self.assertIn("Consider each `'`, `check`, `verify` and `config` against rules 6 and 8: they are suggestions.", check)
        self.assertNotIn("`'`, `has been`", check)
        replies = section(writing, "## Chat replies")
        self.assertIn("Writing out contractions is a suggestion.", replies)
        catalog = " ".join(TEXT.read_text(encoding="utf-8").split())
        self.assertIn("report the catalog's contraction rule (4.2) and its Word Choice swaps as suggestions, not "
                      "violations; Strict mode keeps them as rules", catalog)

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
        writing = WRITING.resolve()
        for relative, phrase in (
                ("skills/workflow-deliver/SKILL.md", "Unslop check"),
                ("skills/workflow-specify/SKILL.md", "Unslop check"),
                ("skills/code-review/SKILL.md", "Unslop check"),
                ("skills/workflow/flows/docs-tests.md", "Unslop check"),
                ("skills/writing-for-agents/SKILL.md", "Unslop tells")):
            with self.subTest(file=relative):
                self.assertIn(phrase, (ROOT / relative).read_text(encoding="utf-8"))
                self.assertIn(writing, pointer_targets(relative, writing.name))
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
            self.assertIn("WRITING.md", (ROOT / path).read_text(encoding="utf-8"), path)


if __name__ == "__main__":
    unittest.main()
