from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from tools.validate import ROOT, validate_package


class PackageTests(unittest.TestCase):
    def test_current_package(self):
        self.assertEqual(validate_package(ROOT), [])

    def copy_package(self, destination: Path) -> Path:
        return Path(shutil.copytree(ROOT, destination,
                    ignore=shutil.ignore_patterns(".git", "__pycache__", ".artifacts", ".local-fixtures")))

    def test_missing_reference_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.copy_package(Path(tmp) / "candidate")
            (root / "skills/workflow/QUESTIONS.md").unlink()
            self.assertTrue(any("QUESTIONS.md" in error for error in validate_package(root)))

    def test_unregistered_second_skill_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.copy_package(Path(tmp) / "candidate")
            second = root / "skills/duplicate/SKILL.md"
            second.parent.mkdir()
            second.write_text("---\nname: duplicate\n---\n", encoding="utf-8")
            self.assertIn("Exactly one installable SKILL.md is required.", validate_package(root))

    def test_version_without_changelog_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.copy_package(Path(tmp) / "candidate")
            path = root / ".claude-plugin/plugin.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            data["version"] = "99.0.0"
            path.write_text(json.dumps(data), encoding="utf-8")
            self.assertIn("Plugin version has no matching changelog entry.", validate_package(root))

    def test_broken_relative_link_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.copy_package(Path(tmp) / "candidate")
            with (root / "README.md").open("a", encoding="utf-8") as stream:
                stream.write("\n[Missing reference](missing-reference.md)\n")
            self.assertTrue(any("missing-reference.md" in error for error in validate_package(root)))

    def test_link_outside_package_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.copy_package(Path(tmp) / "candidate")
            (Path(tmp) / "outside.md").write_text("exists but is not bundled", encoding="utf-8")
            with (root / "README.md").open("a", encoding="utf-8") as stream:
                stream.write("\n[Outside](../outside.md)\n")
            self.assertTrue(any("outside.md" in error for error in validate_package(root)))

    def test_skill_references_are_self_contained(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.copy_package(Path(tmp) / "candidate")
            with (root / "skills/workflow/SKILL.md").open("a", encoding="utf-8") as stream:
                stream.write("\n[Not bundled with a direct skill copy](../../README.md)\n")
            self.assertTrue(any("escapes the separately installable" in error for error in validate_package(root)))


if __name__ == "__main__":
    unittest.main()
