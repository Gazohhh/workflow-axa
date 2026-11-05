from __future__ import annotations

import json
import re
import shutil
import tempfile
import unittest
from pathlib import Path

from tools.validate import ROOT, validate_package
from tools import verification_summary as vs


def copy_package(destination: Path) -> Path:
    return Path(shutil.copytree(ROOT, destination, ignore=shutil.ignore_patterns(
        ".git", "__pycache__", ".artifacts", ".local-fixtures", "dist")))


def edit(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    assert old in text, (path, old)
    path.write_text(text.replace(old, new, 1), encoding="utf-8", newline="")


class DocFactsTests(unittest.TestCase):
    """validate.py rejects hand-kept counts and versions that drift from the manifests."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.clean = copy_package(Path(cls.tmp.name) / "clean")

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def candidate(self) -> Path:
        target = Path(tempfile.mkdtemp(dir=self.tmp.name))
        return Path(shutil.copytree(self.clean, target / "candidate"))

    def test_current_docs_agree_with_manifests(self):
        self.assertEqual([e for e in validate_package(ROOT) if "states" in e or "Current verification" in e], [])

    def test_readme_skill_count_mismatch_fails(self):
        root = self.candidate()
        with (root / "README.md").open("a", encoding="utf-8") as stream:
            stream.write("\nThe package ships twenty skills.\n")
        self.assertTrue(any("README.md states 20 skills" in e for e in validate_package(root)), validate_package(root))

    def test_digit_count_mismatch_fails(self):
        root = self.candidate()
        with (root / "UPGRADE.md").open("a", encoding="utf-8") as stream:
            stream.write("\n## Current installation checks\n\nReplace all 20 skill folders.\n")
        self.assertTrue(any("UPGRADE.md states 20 skills" in e for e in validate_package(root)))

    def test_current_changelog_heading_is_checked_but_history_is_not(self):
        root = self.candidate()
        path = root / "CHANGELOG.md"
        text = path.read_text(encoding="utf-8")
        current_end = text.index("\n## ", text.index("\n## ") + 1)
        path.write_text(text[:current_end] + "\n- Shared rules library 1.6.0.\n" + text[current_end:], encoding="utf-8", newline="")
        self.assertTrue(any("CHANGELOG.md states rules 1.6.0" in e for e in validate_package(root)))
        # Older entries legitimately name older counts and versions ("eight skills", rules 1.4.0).
        self.assertIn("rules library 1.4.0", text)
        self.assertEqual([e for e in validate_package(self.clean) if "CHANGELOG.md states" in e], [])

    def test_upgrade_rules_version_mismatch_fails(self):
        root = self.candidate()
        with (root / "UPGRADE.md").open("a", encoding="utf-8") as stream:
            stream.write("\n## Current installation checks\n\nThe shared rules library (1.6.0) is carried over.\n")
        self.assertTrue(any("UPGRADE.md states rules 1.6.0" in e for e in validate_package(root)))

    def test_package_version_mismatch_fails(self):
        root = self.candidate()
        path = root / "README.md"
        text = path.read_text(encoding="utf-8")
        title = text.splitlines()[0]
        path.write_text(text.replace(title, "# Workflow AXA — 2.7.0-rc.8", 1), encoding="utf-8", newline="")
        self.assertTrue(any("README.md states package 2.7.0-rc.8" in e for e in validate_package(root)))

    def test_vendored_count_must_match_the_list(self):
        root = self.candidate()
        edit(root / "VENDORED-SKILLS.md", "Nine skills", "Eight skills")
        self.assertTrue(any("VENDORED-SKILLS.md states 8 skills" in e and "9" in e for e in validate_package(root)))

    def test_vendored_count_in_readme_must_match(self):
        root = self.candidate()
        with (root / "README.md").open("a", encoding="utf-8") as stream:
            stream.write("\nIt bundles eight vendored skills.\n")
        self.assertTrue(any("README.md states 8 vendored" in e for e in validate_package(root)))

    def test_validation_needs_a_current_section_first(self):
        root = self.candidate()
        edit(root / "VALIDATION.md", "## Current verification", "## Some verification")
        self.assertTrue(any("Current verification" in e for e in validate_package(root)))

    def test_existing_output_line_is_kept(self):
        source = (ROOT / "tools/validate.py").read_text(encoding="utf-8")
        self.assertIn("PASS: package structure, manifest consistency, minimal metadata,", source)


UNITTEST_V = """\
test_a (test_x.A.test_a) ... ok
test_b (test_x.A.test_b) ... skipped 'file symlinks unavailable'
test_c (test_x.A.test_c) ... skipped 'file symlinks unavailable'
test_d (test_x.A.test_d) ... skipped 'no FIFO here'
test_e (test_x.A.test_e) ... FAIL
test_f (test_x.A.test_f)
Multi-line docstring ... ok

----------------------------------------------------------------------
Ran 6 tests in 0.010s

FAILED (failures=1, skipped=3)
"""


class VerificationSummaryTests(unittest.TestCase):
    def test_parses_unittest_totals_and_skip_reasons(self):
        result = vs.parse_unittest(UNITTEST_V)
        self.assertEqual((result.ran, result.passed, result.skipped, result.failed), (6, 2, 3, 1))
        self.assertEqual(result.skip_reasons, {"file symlinks unavailable": 2, "no FIFO here": 1})

    def test_reason_quoted_with_double_quotes_is_counted_without_error_detail(self):
        output = "t (m.C.t) ... skipped \"symlinks unavailable: [WinError 1314] 'a' -> 'b'\"\n\nRan 1 test in 0s\n\nOK (skipped=1)\n"
        self.assertEqual(vs.parse_unittest(output).skip_reasons, {"symlinks unavailable": 1})

    def test_parses_ok_line(self):
        result = vs.parse_unittest("Ran 708 tests in 71.5s\n\nOK (skipped=13)\n")
        self.assertEqual((result.ran, result.passed, result.skipped, result.failed), (708, 695, 13, 0))

    def test_no_test_output_is_not_a_pass(self):
        self.assertIsNone(vs.parse_unittest("Traceback: ImportError"))

    def facts(self, **extra):
        base = dict(commit="abc123", dirty=True, date="2026-11-03", os="Windows-11", python="3.14.2",
                    git="git version 2.38.0", package="2.8.0-rc.1", rules="1.8.0")
        base.update(extra)
        return base

    def test_block_states_commit_environment_and_not_run_checks(self):
        block = vs.render_block(self.facts(),
                                tests=vs.CommandResult("python -m unittest", 1, UNITTEST_V),
                                validate=vs.CommandResult("python tools/validate.py", 0, "PASS: package structure\nNOT RUN: hosts\n"),
                                extra={"Browser suites": "PASS"})
        self.assertTrue(block.startswith("## Current verification\n"))
        for needle in ("abc123", "uncommitted changes", "2026-11-03", "Windows-11", "3.14.2", "git version 2.38.0",
                       "workflow-axa 2.8.0-rc.1", "rules 1.8.0", "exit 1", "6 ran, 2 passed, 3 skipped, 1 failed",
                       "file symlinks unavailable (2)", "PASS: package structure", "| Browser suites | | PASS |",
                       "| Visual regression | | NOT_RUN |", "| Host discovery | | NOT_RUN |"):
            self.assertIn(needle, block)

    def test_missing_command_output_is_not_run(self):
        block = vs.render_block(self.facts(dirty=False), tests=None, validate=None, extra={})
        self.assertIn("clean", block)
        self.assertEqual(block.count("NOT_RUN"), 5)

    def test_write_replaces_only_the_current_section(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "VALIDATION.md"
            path.write_text("# Validation\n\n## Current verification\n\nold\n\n## History — not current evidence\n\nkept\n",
                            encoding="utf-8")
            vs.write_section(path, "## Current verification\n\nnew\n")
            text = path.read_text(encoding="utf-8")
            self.assertEqual(text, "# Validation\n\n## Current verification\n\nnew\n\n## History — not current evidence\n\nkept\n")

    def test_write_refuses_without_history_heading(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "VALIDATION.md"
            path.write_text("# Validation\n\n## Old results\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                vs.write_section(path, "## Current verification\n\nnew\n")
            self.assertEqual(path.read_text(encoding="utf-8"), "# Validation\n\n## Old results\n")

    def test_current_validation_section_names_this_package(self):
        text = (ROOT / "VALIDATION.md").read_text(encoding="utf-8")
        plugin = json.loads((ROOT / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
        self.assertRegex(text, r"\A# Validation\n\n## Current verification\n")
        current = text.split("\n## History", 1)[0]
        self.assertIn(f"workflow-axa {plugin['version']}", current)
        self.assertRegex(current, r"Source commit \| `[0-9a-f]{40}`")
        self.assertRegex(text, r"\n## History — [^\n]*not current evidence")


if __name__ == "__main__":
    unittest.main()
