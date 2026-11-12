"""Reference-file word budgets, the repeated-paragraph note and the CONTEXT.md synonym report of tools/validate.py."""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from tools import validate
from tools.validate import ROOT

REPEAT = ("This planted paragraph repeats the same instruction in two reference files so the validator can see that "
          "one rule is stated twice and point the reader at both places.")


def copy_package(destination: Path) -> Path:
    return Path(shutil.copytree(ROOT, destination, ignore=shutil.ignore_patterns(
        ".git", "__pycache__", ".artifacts", ".local-fixtures", "dist")))


def append(path: Path, text: str) -> None:
    with path.open("a", encoding="utf-8", newline="") as stream:
        stream.write("\n" + text + "\n")


class ValidateBudgetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.clean = copy_package(Path(cls.tmp.name) / "clean")

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def candidate(self) -> Path:
        return Path(shutil.copytree(self.clean, Path(tempfile.mkdtemp(dir=self.tmp.name)) / "candidate"))

    # Word budgets for reference files

    def test_every_reference_file_has_a_budget_and_fits_it(self):
        self.assertEqual(sorted(validate.reference_files(ROOT)), sorted(validate.REFERENCE_BUDGETS))
        self.assertEqual(validate.reference_budget_errors(ROOT), [])

    def test_formerly_copied_reference_files_have_budgets(self):
        # D1: these skills are our own text now, so their reference files are budgeted like every other skill's.
        files = validate.reference_files(ROOT)
        for name in ("tdd/tests.md", "simple-english/references/rule-catalog.md", "domain-modeling/GLOSSARY-FORMAT.md"):
            self.assertIn(name, validate.REFERENCE_BUDGETS)
            self.assertIn(name, files)

    def test_a_reference_file_at_its_ceiling_passes_and_one_word_more_fails(self):
        for extra, fails in ((0, False), (1, True)):
            with self.subTest(extra=extra):
                root = self.candidate()
                path = root / "skills/workflow/TASK-FOLDER.md"
                room = validate.REFERENCE_BUDGETS["workflow/TASK-FOLDER.md"] - len(path.read_text(encoding="utf-8").split())
                self.assertGreaterEqual(room, 0)  # an existing overage would make the one-word case pass by accident
                append(path, "extra " * (room + extra))
                errors = [e for e in validate.validate_package(root)
                          if "skills/workflow/TASK-FOLDER.md" in e and "word budget" in e]
                self.assertEqual(bool(errors), fails, errors)

    def test_reference_file_without_a_budget_fails(self):
        root = self.candidate()
        (root / "skills/workflow/NEW-NOTES.md").write_text("A new reference file.\n", encoding="utf-8")
        errors = validate.validate_package(root)
        self.assertTrue(any("skills/workflow/NEW-NOTES.md" in e and "no word budget" in e for e in errors), errors)

    # Repeated paragraphs (advisory)

    def test_planted_repeat_fails_validation(self):
        # A8: the validator enforces the duplication check.
        root = self.candidate()
        self.assertEqual(validate.repeat_notes(root), [])
        append(root / "skills/workflow/RULES.md", REPEAT)
        append(root / "skills/ui-design/KIT.md", REPEAT)
        found = validate.repeat_notes(root)
        planted = [n for n in found if "skills/workflow/RULES.md" in n and "skills/ui-design/KIT.md" in n]
        self.assertEqual(len(planted), 1, found)
        self.assertTrue(planted[0].startswith("repeated paragraph"), planted)
        errors = [e for e in validate.validate_package(root) if e.startswith("repeated paragraph")]
        self.assertEqual(errors, planted)
        self.assertFalse(any(n.startswith("repeated paragraph") for n in validate.package_notes(root)))

    # Synonyms from CONTEXT.md

    def test_context_parses(self):
        vocabulary = validate.read_vocabulary(ROOT)
        self.assertEqual(vocabulary.avoid.get("sub-agent"), "subagent")
        self.assertEqual(vocabulary.avoid.get("gate two"), "implementation approval")
        self.assertIn("behaviour-only", vocabulary.identifiers)
        self.assertIn("agreement", vocabulary.terms)
        owners = dict(vocabulary.owners)
        self.assertGreaterEqual(len(owners), 9)
        self.assertTrue(all((ROOT / path).is_file() for path in owners.values()), owners)
        # A rejected synonym is never also an identifier that keeps its form.
        self.assertFalse(set(vocabulary.avoid) & {i.casefold() for i in vocabulary.identifiers})

    def test_the_synonym_switch_is_on(self):
        self.assertIs(validate.SYNONYMS_FAIL, True)

    def test_planted_synonym_fails_validation(self):
        root = self.candidate()
        append(root / "skills/workflow/RULES.md", "Hand the search to a sub-agent.")
        findings = validate.synonym_findings(root)
        self.assertTrue(any("'sub-agent'" in n and "'subagent'" in n and "skills/workflow/RULES.md:" in n
                            for n in findings), findings)
        errors = validate.validate_package(root)
        self.assertTrue(any("'sub-agent'" in e and "skills/workflow/RULES.md:" in e for e in errors), errors)
        self.assertFalse(any("sub-agent" in n for n in validate.package_notes(root)))  # an error, not also a note

    def test_synonym_fails_only_when_the_switch_is_on(self):
        root = self.candidate()
        append(root / "skills/workflow/RULES.md", "Hand the search to a sub-agent.")
        with mock.patch.object(validate, "SYNONYMS_FAIL", False):
            self.assertFalse(any("sub-agent" in e for e in validate.validate_package(root)))
            self.assertTrue(any("'sub-agent'" in n for n in validate.package_notes(root)))
        with mock.patch.object(validate, "SYNONYMS_FAIL", True):
            errors = validate.validate_package(root)
        self.assertTrue(any("'sub-agent'" in e for e in errors), errors)

    def test_code_spans_and_identifiers_are_skipped(self):
        root = self.candidate()
        append(root / "skills/workflow/RULES.md", "The label `sub-agent` stays. The record line Approval (gate two) stays.")
        self.assertFalse(any("skills/workflow/RULES.md" in n for n in validate.synonym_findings(root)))

    def test_formerly_copied_skills_are_checked_in_full(self):
        # D1: the whole SKILL.md and each reference file of a formerly copied skill is ours, not only a closing section.
        root = self.candidate()
        skill = root / "skills/tdd/SKILL.md"
        lines = skill.read_text(encoding="utf-8").splitlines(keepends=True)
        body = next(i for i, line in enumerate(lines) if line.startswith("# "))
        skill.write_text("".join(lines[:body + 1]) + "\nAsk a sub-agent.\n" + "".join(lines[body + 1:]),
                         encoding="utf-8", newline="")
        append(root / "skills/tdd/tests.md", "Ask a sub-agent.")
        findings = [n.rsplit(":", 1)[0] for n in validate.synonym_findings(root) if "skills/tdd/" in n]
        self.assertEqual(sorted(findings), ["synonym 'sub-agent' (use 'subagent') in skills/tdd/SKILL.md",
                                            "synonym 'sub-agent' (use 'subagent') in skills/tdd/tests.md"])

    def test_command_line_fails_on_a_synonym_and_prints_notes(self):
        root = self.candidate()
        append(root / "skills/workflow/RULES.md", "Hand the search to a sub-agent.\n\n" + REPEAT)
        append(root / "skills/ui-design/KIT.md", REPEAT)
        result = subprocess.run([sys.executable, "-X", "utf8", str(ROOT / "tools/validate.py"), "--root", str(root)],
                                capture_output=True, text=True, encoding="utf-8",
                                env={**os.environ, "PYTHONUTF8": "1"})
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("FAIL: synonym 'sub-agent'", result.stderr)
        self.assertIn("FAIL: repeated paragraph", result.stderr)


if __name__ == "__main__":
    unittest.main()
