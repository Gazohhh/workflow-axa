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

    def test_vendored_upstream_files_have_no_budget(self):
        for name in ("tdd/tests.md", "simple-english/references/rule-catalog.md", "domain-modeling/GLOSSARY-FORMAT.md"):
            self.assertNotIn(name, validate.REFERENCE_BUDGETS)

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

    def test_code_spans_identifiers_and_vendored_text_are_skipped(self):
        root = self.candidate()
        before = validate.synonym_findings(root)
        append(root / "skills/workflow/RULES.md", "The label `sub-agent` stays. The record line Approval (gate two) stays.")
        append(root / "skills/tdd/tests.md", "Upstream text may say sub-agent.")
        skill = root / "skills/tdd/SKILL.md"
        text = skill.read_text(encoding="utf-8")
        head, tail = text.split("## workflow-axa adaptation", 1)
        skill.write_text(head + "Upstream sub-agent.\n\n## workflow-axa adaptation" + tail + "\n- Ask a sub-agent.\n",
                         encoding="utf-8")
        def planted(notes):  # line numbers shift, so compare the 'sub-agent' findings per file
            return sorted(n.rsplit(":", 1)[0] for n in notes if "'sub-agent'" in n
                          and ("skills/workflow/RULES.md" in n or "skills/tdd/" in n))
        added = planted(validate.synonym_findings(root))
        for note in planted(before):
            added.remove(note)
        self.assertEqual(added, ["synonym 'sub-agent' (use 'subagent') in skills/tdd/SKILL.md"])

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
