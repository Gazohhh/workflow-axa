"""A9: a baseline is reused only while its command, commit, diff and environment still match."""
from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "skills/workflow/scripts/baseline_state.py"


def run(*args, cwd):
    return subprocess.run([sys.executable, "-X", "utf8", "-I", str(SCRIPT), *map(str, args)], cwd=cwd,
                          capture_output=True, text=True, encoding="utf-8")


class BaselineStateTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.repo = Path(tmp.name)
        git = lambda *a: subprocess.run(["git", *a], cwd=self.repo, capture_output=True, check=True)
        git("init", "-q")
        (self.repo / "a.txt").write_text("one\n", encoding="utf-8")
        git("add", "a.txt")
        git("-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "base")
        self.record = self.repo / "baseline.txt"

    def test_unchanged_inputs_allow_reuse(self):
        self.assertEqual(run("record", "npm test", self.record, cwd=self.repo).returncode, 0)
        result = run("check", "npm test", self.record, cwd=self.repo)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("REUSE", result.stdout)

    def test_a_changed_diff_or_command_invalidates_the_baseline(self):
        run("record", "npm test", self.record, cwd=self.repo)
        (self.repo / "a.txt").write_text("two\n", encoding="utf-8")
        changed = run("check", "npm test", self.record, cwd=self.repo)
        self.assertEqual(changed.returncode, 1)
        self.assertIn("diff", changed.stdout)
        (self.repo / "a.txt").write_text("one\n", encoding="utf-8")
        other = run("check", "npm run test:all", self.record, cwd=self.repo)
        self.assertEqual(other.returncode, 1)
        self.assertIn("command", other.stdout)

    def test_untracked_content_and_other_folders_count(self):
        # Review of V10: untracked content was ignored, and a check from a subfolder saw only that subfolder.
        (self.repo / "u.txt").write_text("x\n", encoding="utf-8")
        (self.repo / "sub").mkdir()
        (self.repo / "other").mkdir()
        (self.repo / "other" / "b.txt").write_text("1\n", encoding="utf-8")
        run("record", "npm test", self.record, cwd=self.repo)
        (self.repo / "u.txt").write_text("y\n", encoding="utf-8")
        self.assertEqual(run("check", "npm test", self.record, cwd=self.repo).returncode, 1)
        (self.repo / "u.txt").write_text("x\n", encoding="utf-8")
        run("record", "npm test", self.record, cwd=self.repo / "sub")
        (self.repo / "other" / "b.txt").write_text("2\n", encoding="utf-8")
        self.assertEqual(run("check", "npm test", self.record, cwd=self.repo / "sub").returncode, 1)

    def test_records_and_artifacts_are_ignored(self):
        run("record", "npm test", self.record, cwd=self.repo)
        (self.repo / "docs" / "plans" / "t").mkdir(parents=True)
        (self.repo / "docs" / "plans" / "t" / "PLAN.md").write_text("x\n", encoding="utf-8")
        (self.repo / ".artifacts").mkdir()
        (self.repo / ".artifacts" / "log.txt").write_text("x\n", encoding="utf-8")
        self.assertEqual(run("check", "npm test", self.record, cwd=self.repo).returncode, 0)

    def test_outside_git_is_blocked_not_reused(self):
        with tempfile.TemporaryDirectory() as plain:
            record = Path(plain) / "b.txt"
            self.assertEqual(run("record", "npm test", record, cwd=plain).returncode, 2)
            self.assertEqual(run("record", "npm test", Path(plain) / "no" / "b.txt", cwd=self.repo).returncode, 2)

    def test_missing_record_is_refused(self):
        self.assertEqual(run("check", "npm test", self.repo / "none.txt", cwd=self.repo).returncode, 2)


if __name__ == "__main__":
    unittest.main()
