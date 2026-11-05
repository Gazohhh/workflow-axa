"""screenshot_report.py with a fake browser: no real browser, no installs (retro E23 follow-up)."""
from __future__ import annotations

import os
import contextlib
import importlib.util
import io
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

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

    def test_browser_timeout_reports_failure_and_preserves_completed_capture(self):
        spec = importlib.util.spec_from_file_location('screenshot_timeout_case', SCRIPT)
        tool = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(tool)
        for timeout_at in (1, 2):
            with self.subTest(timeout_at=timeout_at):
                destination = self.dir / f'timeout-{timeout_at}'
                calls = []
                def run(command, **kwargs):
                    calls.append(command)
                    if len(calls) == timeout_at:
                        raise subprocess.TimeoutExpired(command, kwargs['timeout'])
                    target = next(arg.split('=', 1)[1] for arg in command if arg.startswith('--screenshot='))
                    Path(target).write_bytes(b'completed capture')
                    return subprocess.CompletedProcess(command, 0, '', '')
                output = io.StringIO()
                with mock.patch.object(tool.subprocess, 'run', side_effect=run), contextlib.redirect_stdout(output):
                    result = tool.main(['screenshot_report.py', str(self.report), str(destination), '--browser', str(self.browser)])
                self.assertEqual(result, 1)
                self.assertIn('timed out', output.getvalue())
                self.assertEqual(len(calls), timeout_at)
                self.assertFalse((destination / 'review-narrow.png').exists())
                if timeout_at == 2:
                    self.assertEqual((destination / 'review-desktop.png').read_bytes(), b'completed capture')


if __name__ == "__main__":
    unittest.main()
