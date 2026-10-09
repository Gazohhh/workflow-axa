from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.create_fixture import ROOT, SCENARIOS, TASK, create_fixture, git


@unittest.skipUnless(shutil.which("git"), "Git is required for disposable fixture tests.")
class FixtureTests(unittest.TestCase):
    def test_existing_destination_is_untouched(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "existing"
            path.mkdir()
            sentinel = path / "user-data.txt"
            sentinel.write_text("preserve", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                create_fixture(path, "clean")
            self.assertEqual(sentinel.read_text(encoding="utf-8"), "preserve")
            self.assertEqual(list(path.iterdir()), [sentinel])

    def test_repository_ancestor_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp)
            (parent / ".git").mkdir()
            with self.assertRaises(ValueError):
                create_fixture(parent / "new-fixture", "clean")
            self.assertFalse((parent / "new-fixture").exists())

    def test_worktree_git_file_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp)
            (parent / ".git").write_text("gitdir: synthetic", encoding="utf-8")
            with self.assertRaises(ValueError):
                create_fixture(parent / "new-fixture", "clean")

    def test_package_destination_is_refused(self):
        path = ROOT / ".never-create-this-fixture"
        with self.assertRaises(ValueError):
            create_fixture(path, "clean")
        self.assertFalse(path.exists())

    def test_missing_git_does_not_create_destination(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "missing-git"
            with patch("tools.create_fixture.shutil.which", return_value=None):
                with self.assertRaises(FileNotFoundError):
                    create_fixture(path, "clean")
            self.assertFalse(path.exists())

    def test_all_scenarios_have_local_baselines_and_no_remotes(self):
        with tempfile.TemporaryDirectory() as tmp:
            for scenario in SCENARIOS:
                with self.subTest(scenario=scenario):
                    repo = create_fixture(Path(tmp) / scenario, scenario)
                    self.assertEqual(git(repo, "remote"), "")
                    state = json.loads((repo / ".fixture-state.json").read_text(encoding="utf-8"))
                    self.assertEqual(state["scenario"], scenario)
                    self.assertEqual(git(repo, "rev-list", "--count", "HEAD").strip(), "1")
                    if scenario in {"approved", "interrupted", "owned"}:
                        self.assertTrue((repo / TASK / "PLAN.md").is_file())

    def test_clean_baseline_tests_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = create_fixture(Path(tmp) / "baseline", "clean")
            result = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
                                    cwd=repo, capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("Ran 3 tests", result.stderr)

    def test_mixed_staged_and_unstaged_edits_share_a_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = create_fixture(Path(tmp) / "mixed", "mixed")
            staged = git(repo, "diff", "--cached", "--", "src/labels.py")
            unstaged = git(repo, "diff", "--", "src/labels.py")
            self.assertIn("wording owned by the user", staged)
            self.assertNotIn("display translations", staged)
            self.assertIn("display translations", unstaged)

    def test_interrupted_scenario_really_is_partial(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = create_fixture(Path(tmp) / "interrupted", "interrupted")
            code = (repo / "src/labels.py").read_text(encoding="utf-8")
            self.assertIn("if home < 0", code)
            self.assertNotIn("away < 0", code)
            self.assertIn("_legacy_score", (repo / "src/player.py").read_text(encoding="utf-8"))

    def test_baseline_failure_is_explicit(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = create_fixture(Path(tmp) / "failing", "baseline-failure")
            result = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
                                    cwd=repo, capture_output=True, text=True, timeout=30)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Synthetic unrelated baseline failure", result.stderr)

    def test_fake_sensitive_log_is_ignored(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = create_fixture(Path(tmp) / "secret", "secret")
            self.assertIn("FAKE_WORKFLOW_TEST_SECRET", (repo / "private-evidence.log").read_text(encoding="utf-8"))
            self.assertIn("private-evidence.log", git(repo, "check-ignore", "private-evidence.log"))


if __name__ == "__main__":
    unittest.main()
