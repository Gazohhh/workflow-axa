"""skills/interrogate/scripts/snapshot.py: one reproducible snapshot id, an exact isolated copy, a stale check.
Opus T22+T23 review: the prose recipe gave two agents two ids, and a fresh checkout under core.autocrlf=true wrote
CRLF where the target had LF, so the copy never matched."""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/interrogate/scripts/snapshot.py"


def run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-X", "utf8", "-I", str(SCRIPT), *args], capture_output=True, text=True)


def git(repo: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@example.invalid", *args],
                   check=True, capture_output=True)


def make_link(target: Path, link: Path) -> bool:
    """A symbolic link where the OS allows one, else a Windows junction (no privilege needed)."""
    try:
        os.symlink(target, link, target_is_directory=True)
        return True
    except OSError:
        pass
    try:
        import _winapi
        _winapi.CreateJunction(str(target), str(link))
        return True
    except (ImportError, OSError):
        return False


class SnapshotTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name) / "repo"
        self.repo.mkdir()
        git(self.repo, "init", "--quiet")
        git(self.repo, "config", "core.autocrlf", "true")
        (self.repo / ".gitignore").write_bytes(b"build/\n")
        (self.repo / "keep.py").write_bytes(b"def f(x):\n    return x\n")
        (self.repo / "gone.py").write_bytes(b"x = 1\n")
        (self.repo / "staged.py").write_bytes(b"a = 1\n")
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "--quiet", "-m", "base")
        # The working tree as an interrogation finds it: an unstaged edit, a staged edit changed again, a deletion,
        # an untracked file, an ignored file, and LF bytes although core.autocrlf would check out CRLF.
        (self.repo / "keep.py").write_bytes(b"def f(x):\n    return x + 1\n")
        (self.repo / "staged.py").write_bytes(b"a = 2\n")
        git(self.repo, "add", "staged.py")
        (self.repo / "staged.py").write_bytes(b"a = 3\n")
        (self.repo / "gone.py").unlink()
        (self.repo / "new.py").write_bytes(b"b = 1\n")
        (self.repo / "build").mkdir()
        (self.repo / "build/out.txt").write_bytes(b"ignored\n")

    def snapshot(self) -> str:
        done = run("id", str(self.repo))
        self.assertEqual(done.returncode, 0, done.stderr)
        return done.stdout.strip()

    def test_the_id_is_stable_and_covers_edits_deletions_and_untracked_files(self):
        first = self.snapshot()
        self.assertEqual(first, self.snapshot())
        self.assertRegex(first, r"^[0-9a-f]{40}:[0-9a-f]{64}$")
        for change in (lambda: (self.repo / "new.py").write_bytes(b"b = 2\n"),
                       lambda: (self.repo / "keep.py").unlink(),
                       lambda: (self.repo / "other.py").write_bytes(b"c = 1\n")):
            before = self.snapshot()
            change()
            self.assertNotEqual(before, self.snapshot())

    def test_an_ignored_file_does_not_change_the_id(self):
        before = self.snapshot()
        (self.repo / "build/out.txt").write_bytes(b"changed\n")
        self.assertEqual(before, self.snapshot())

    def test_the_copy_has_the_same_id_and_bytes_and_the_target_git_is_untouched(self):
        expected = self.snapshot()
        refs = sorted(p.relative_to(self.repo / ".git").as_posix() for p in (self.repo / ".git").rglob("*"))
        dest = Path(self.tmp.name) / "copy"
        done = run("copy", str(self.repo), str(dest), expected)
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertEqual(done.stdout.strip(), expected)
        self.assertEqual((dest / "keep.py").read_bytes(), b"def f(x):\n    return x + 1\n")
        self.assertEqual((dest / "staged.py").read_bytes(), b"a = 3\n")
        self.assertFalse((dest / "gone.py").exists())
        self.assertFalse((dest / "build").exists())
        self.assertEqual(refs, sorted(p.relative_to(self.repo / ".git").as_posix()
                                      for p in (self.repo / ".git").rglob("*")))

    def test_a_copy_with_the_wrong_id_fails_and_an_existing_destination_is_refused(self):
        dest = Path(self.tmp.name) / "copy"
        self.assertEqual(run("copy", str(self.repo), str(dest), "0" * 40 + ":" + "0" * 64).returncode, 3)
        again = run("copy", str(self.repo), str(dest), self.snapshot())
        self.assertNotEqual(again.returncode, 0)
        self.assertIn("already exists", again.stderr)

    def host_checkout(self) -> Path:
        """A checkout like the one a host gives an isolated agent: same HEAD, with leftovers of its own."""
        dest = Path(self.tmp.name) / "host"
        subprocess.run(["git", "clone", "--quiet", str(self.repo), str(dest)], check=True, capture_output=True)
        git(dest, "config", "core.autocrlf", "true")
        (dest / "leftover.py").write_bytes(b"stale = True\n")
        (dest / "keep.py").write_bytes(b"something else\n")
        return dest

    def test_fill_brings_the_snapshot_into_an_existing_host_checkout(self):
        # Astra and Opus round 2: a host-made worktree already exists, so `copy` alone couldn't fill it.
        expected = self.snapshot()
        dest = self.host_checkout()
        done = run("fill", str(self.repo), str(dest), expected)
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertEqual(done.stdout.strip(), expected)
        self.assertFalse((dest / "leftover.py").exists())
        self.assertFalse((dest / "gone.py").exists())
        self.assertEqual((dest / "new.py").read_bytes(), b"b = 1\n")
        self.assertEqual((dest / "staged.py").read_bytes(), b"a = 3\n")

    def test_fill_refuses_the_target_a_folder_above_it_and_another_head(self):
        expected = self.snapshot()
        self.assertNotEqual(run("fill", str(self.repo), str(self.repo), expected).returncode, 0)
        self.assertNotEqual(run("fill", str(self.repo), str(self.repo.parent), expected).returncode, 0)
        dest = self.host_checkout()
        git(dest, "commit", "--quiet", "--allow-empty", "-m", "elsewhere")
        refused = run("fill", str(self.repo), str(dest), expected)
        self.assertNotEqual(refused.returncode, 0)
        self.assertIn("HEAD differs", refused.stderr)
        self.assertTrue((dest / "leftover.py").exists())

    def test_fill_refuses_a_checkout_inside_the_target_unless_git_ignores_it(self):
        # Opus round 3: a nested, unignored checkout is part of the target's own listing.
        expected = self.snapshot()
        nested = self.repo / "wt"
        subprocess.run(["git", "clone", "--quiet", str(self.repo), str(nested)], check=True, capture_output=True)
        refused = run("fill", str(self.repo), str(nested), expected)
        self.assertNotEqual(refused.returncode, 0)
        self.assertIn("Git doesn't ignore it", refused.stderr)
        (self.repo / ".git/info/exclude").write_text("wt/\n", encoding="utf-8")
        allowed = run("fill", str(self.repo), str(nested), self.snapshot())
        self.assertEqual(allowed.returncode, 0, allowed.stderr)

    def test_a_link_in_the_checkout_is_replaced_not_followed(self):
        # Astra round 2: a link where the snapshot needs a folder must not lead writes outside the copy.
        (self.repo / "lib").mkdir()
        (self.repo / "lib/a.py").write_bytes(b"a = 1\n")
        expected = self.snapshot()
        outside = Path(self.tmp.name) / "outside"
        outside.mkdir()
        (outside / "sentinel.txt").write_bytes(b"untouched\n")
        dest = self.host_checkout()
        if not make_link(outside, dest / "lib"):
            self.skipTest("this machine can make neither a symbolic link nor a junction")
        done = run("fill", str(self.repo), str(dest), expected)
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertEqual(sorted(p.name for p in outside.iterdir()), ["sentinel.txt"])
        self.assertEqual((outside / "sentinel.txt").read_bytes(), b"untouched\n")
        self.assertTrue((dest / "lib").is_dir() and not (dest / "lib").is_symlink())
        self.assertEqual((dest / "lib/a.py").read_bytes(), b"a = 1\n")

    def test_the_executable_bit_is_copied(self):
        if sys.platform == "win32":
            self.skipTest("Windows has no executable bit")
        script = self.repo / "run.sh"
        script.write_bytes(b"#!/bin/sh\n")
        script.chmod(0o755)
        dest = Path(self.tmp.name) / "copy"
        self.assertEqual(run("copy", str(self.repo), str(dest), self.snapshot()).returncode, 0)
        self.assertTrue((dest / "run.sh").stat().st_mode & 0o100)

    def test_check_reports_a_changed_target(self):
        pinned = self.snapshot()
        self.assertEqual(run("check", str(self.repo), pinned).returncode, 0)
        (self.repo / "keep.py").write_bytes(b"changed\n")
        self.assertEqual(run("check", str(self.repo), pinned).returncode, 3)


if __name__ == "__main__":
    unittest.main()
