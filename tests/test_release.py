from __future__ import annotations

import json
import shutil
import tempfile
import unittest
import zipfile
from pathlib import Path

from tools.validate import ROOT
from tools import build_release as br

EXCLUDED_PREFIXES = (".git/", ".artifacts/", "docs/plans/", "evals/", ".local-fixtures/", "tests/", "tools/", "dist/")


class ReleaseFromCheckoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.result = br.build_release(ROOT, Path(cls.tmp.name) / "out")
        with zipfile.ZipFile(cls.result.path) as archive:
            cls.names = archive.namelist()
            cls.infos = archive.infolist()
            cls.bad = archive.testzip()

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_zip_is_named_after_the_plugin_version(self):
        version = json.loads((ROOT / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))["version"]
        self.assertEqual(self.result.path.name, f"workflow-axa-{version}.zip")
        self.assertIsNone(self.bad)

    def test_contains_every_registered_skill_and_the_licence(self):
        plugin = json.loads((ROOT / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
        for entry in plugin["skills"]:
            folder = entry.removeprefix("./")
            self.assertIn(f"{folder}/SKILL.md", self.names)
            on_disk = {p.relative_to(ROOT).as_posix() for p in (ROOT / folder).rglob("*")
                       if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc"}
            self.assertEqual({n for n in self.names if n.startswith(folder + "/")}, on_disk, folder)
        for name in ("LICENSE", "README.md", "CHANGELOG.md", "UPGRADE.md", "VALIDATION.md", "VENDORED-SKILLS.md",
                     "docs/DESIGN.md", "docs/ARCHITECTURE.md", "docs/EVALUATION.md", ".claude-plugin/plugin.json", ".claude-plugin/marketplace.json", "hooks/hooks.json"):
            self.assertIn(name, self.names)
        self.assertIn("MIT License", (ROOT / "LICENSE").read_text(encoding="utf-8"))
        # D1: each formerly copied skill ships with its own MIT LICENSE.
        for name in ("grilling", "tdd", "code-review", "writing-for-agents", "codebase-design", "domain-modeling",
                     "implement-spec", "retro", "simple-english"):
            self.assertIn(f"skills/{name}/LICENSE", self.names)

    def test_archived_evaluation_records_are_not_shipped(self):
        for name in ("CANDIDATE-REVIEW.md", "RC3-CASES.md", "CLAUDE-TEST-PROMPT.txt"):
            self.assertTrue((ROOT / "docs/archive" / name).is_file(), name)
            self.assertFalse((ROOT / name).exists(), name)
            self.assertFalse(any(entry.rsplit("/", 1)[-1] == name for entry in self.names), name)

    def test_contains_no_excluded_path(self):
        for name in self.names:
            self.assertFalse(name.startswith(EXCLUDED_PREFIXES), name)
            self.assertNotIn("__pycache__", name)
            self.assertFalse(name.endswith((".pyc", ".pyo")), name)

    def test_order_and_timestamps_are_fixed(self):
        self.assertEqual(self.names, sorted(self.names))
        self.assertEqual({info.date_time for info in self.infos}, {br.FIXED_TIME})
        again = br.build_release(ROOT, Path(self.tmp.name) / "again")
        self.assertEqual(again.sha256, self.result.sha256)
        self.assertEqual(again.files, self.result.files)


class ReleaseRefusalTests(unittest.TestCase):
    def tree(self, tmp: str) -> Path:
        root = Path(tmp) / "pkg"
        (root / ".claude-plugin").mkdir(parents=True)
        (root / ".claude-plugin/plugin.json").write_text(json.dumps({"version": "1.0.0", "skills": ["./skills/one"]}),
                                                          encoding="utf-8")
        for folder in ("skills/one/scripts", "skills/unregistered", "hooks/__pycache__", "docs/plans/x", "tests"):
            (root / folder).mkdir(parents=True)
        for name in ("skills/one/SKILL.md", "skills/one/scripts/a.py", "skills/unregistered/SKILL.md",
                     "hooks/hooks.json", "hooks/__pycache__/a.cpython-314.pyc", "docs/DESIGN.md",
                     "docs/plans/x/PLAN.md", "tests/test_a.py", *br.ROOT_FILES):
            (root / name).write_text("x", encoding="utf-8")
        return root

    def test_minimal_tree_builds_from_the_include_list_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = br.build_release(self.tree(tmp), Path(tmp) / "out")
            self.assertIn("skills/one/scripts/a.py", result.files)
            for name in result.files:
                self.assertFalse(name.startswith(("skills/unregistered", "docs/plans", "tests/")), name)
                self.assertNotIn("__pycache__", name)

    def test_secret_like_files_are_refused(self):
        for planted in ("skills/one/.env", "hooks/.env.local", "skills/one/deploy.pem", "hooks/signing.key",
                        "skills/one/api_token.txt", "skills/one/scripts/Client_Secret.json", "hooks/credentials.json"):
            with self.subTest(planted), tempfile.TemporaryDirectory() as tmp:
                root = self.tree(tmp)
                (root / planted).write_text("x", encoding="utf-8")
                with self.assertRaises(br.ReleaseError) as caught:
                    br.build_release(root, Path(tmp) / "out")
                self.assertIn(planted, str(caught.exception))
                self.assertFalse((Path(tmp) / "out").exists())

    def test_missing_included_file_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.tree(tmp)
            (root / "LICENSE").unlink()
            with self.assertRaises(br.ReleaseError):
                br.build_release(root, Path(tmp) / "out")

    def test_output_inside_an_included_folder_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.tree(tmp)
            with self.assertRaises(br.ReleaseError):
                br.build_release(root, root / "skills/one")

    def test_default_output_falls_back_when_dist_is_not_ignored(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(br.default_output_dir(root, ignored=lambda path: False), root / ".artifacts/release")
            self.assertEqual(br.default_output_dir(root, ignored=lambda path: True), root / "dist")


if __name__ == "__main__":
    unittest.main()
