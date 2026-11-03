"""screenshot_report.py with a fake browser: no real browser, no installs (retro E23 follow-up)."""
from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "skills/codebase-map/scripts/screenshot_report.py"
FAKE = '''import sys
arg = next(a for a in sys.argv if a.startswith("--screenshot="))
open(arg.split("=", 1)[1], "wb").write(b"PNG")
'''


class ScreenshotReportTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)
        self.report = self.dir / "review.html"
        self.report.write_text("<!doctype html><title>x</title>", encoding="utf-8")
        self.out = self.dir / "out"
        self.out.mkdir()
        (self.dir / "fake.py").write_text(FAKE, encoding="utf-8")
        if os.name == "nt":
            self.browser = self.dir / "fake.bat"
            self.browser.write_text(f'@"{sys.executable}" "{self.dir / "fake.py"}" %*\n', encoding="utf-8")
        else:
            self.browser = self.dir / "fake.sh"
            self.browser.write_text(f'#!/bin/sh\nexec "{sys.executable}" "{self.dir / "fake.py"}" "$@"\n', encoding="utf-8")
            self.browser.chmod(0o755)

    def run_tool(self, *extra):
        return subprocess.run([sys.executable, "-X", "utf8", "-I", str(SCRIPT), *map(str, extra)],
                              capture_output=True, text=True, encoding="utf-8", timeout=120)

    def test_writes_desktop_and_narrow_then_refuses_overwrite(self):
        first = self.run_tool(self.report, self.out, "--browser", self.browser)
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        self.assertTrue((self.out / "review-desktop.png").is_file())
        self.assertTrue((self.out / "review-narrow.png").is_file())
        second = self.run_tool(self.report, self.out, "--browser", self.browser)
        self.assertEqual(second.returncode, 2)
        self.assertIn("never overwritten", second.stdout)

    def test_bad_inputs_block_without_writing(self):
        self.assertEqual(self.run_tool(self.dir / "missing.html", self.out, "--browser", self.browser).returncode, 2)
        self.assertEqual(self.run_tool(self.report, self.dir / "no" / "parent", "--browser", self.browser).returncode, 2)
        missing_browser = self.run_tool(self.report, self.out, "--browser", self.dir / "nobrowser.exe")
        self.assertEqual(missing_browser.returncode, 2)
        self.assertIn("Nothing is installed", missing_browser.stdout)
        self.assertEqual(list(self.out.iterdir()), [])

    def test_first_capture_in_a_fresh_repo_creates_artifacts(self):
        # Round 22: both runs were blocked because `.artifacts/` did not exist yet in a fresh repo.
        out = self.dir / ".artifacts" / "2026-11-03-task"
        result = self.run_tool(self.report, out, "--browser", self.browser)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue((out / "review-desktop.png").is_file())
        typo = self.run_tool(self.report, self.dir / "artifacts-typo" / "t", "--browser", self.browser)
        self.assertEqual(typo.returncode, 2)
        self.assertFalse((self.dir / "artifacts-typo").exists())


if __name__ == "__main__":
    unittest.main()
