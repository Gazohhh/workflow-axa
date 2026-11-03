"""Screenshot a rendered report with an already-installed Chromium browser (Edge or Chrome). No installs.

usage: python -X utf8 -I screenshot_report.py <report.html> <out-folder> [--browser PATH] [--height PX]

Writes <name>-desktop.png (1280 wide) and <name>-narrow.png (500 wide, the narrowest window headless
Chromium allows; exact phone widths need Playwright) into <out-folder> (created if its parent exists;
use the task's output folder under ARTIFACTS.md). Never overwrites an existing file. The image is
--height pixels tall (default 6000), enough for most reports; long reports are cut at that height, so look
at the bottom too. A screenshot shows layout; it does not prove the report is correct or that anyone saw it.
Exit 0: both images written; 1: browser failed; 2: bad input or no browser found.
"""
from __future__ import annotations

import pathlib
import shutil
import subprocess
import sys
import tempfile
import time

CANDIDATES = (
    r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
    r'C:\Program Files\Microsoft\Edge\Application\msedge.exe',
    r'C:\Program Files\Google\Chrome\Application\chrome.exe',
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge',
)
NAMES = ('msedge', 'microsoft-edge', 'google-chrome', 'chromium', 'chromium-browser', 'chrome')


def find_browser(explicit: str | None) -> str | None:
    if explicit:
        return explicit if pathlib.Path(explicit).is_file() else None
    for path in CANDIDATES:
        if pathlib.Path(path).is_file():
            return path
    for name in NAMES:
        found = shutil.which(name)
        if found:
            return found
    return None


def command(browser: str, url: str, out: pathlib.Path, width: int, height: int, profile: str) -> list[str]:
    return [browser, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--no-first-run',
            f'--user-data-dir={profile}', f'--window-size={width},{height}', f'--screenshot={out}', url]


def main(argv: list[str]) -> int:
    args = argv[1:]
    browser_arg = height = None
    if '--browser' in args:
        i = args.index('--browser'); browser_arg = args[i + 1]; del args[i:i + 2]
    if '--height' in args:
        i = args.index('--height'); height = int(args[i + 1]); del args[i:i + 2]
    if len(args) != 2:
        print(__doc__)
        return 2
    report, folder = pathlib.Path(args[0]).resolve(), pathlib.Path(args[1]).resolve()
    if not report.is_file() or report.suffix.lower() != '.html':
        print(f'BLOCKED: {report} is not an HTML file')
        return 2
    fresh_artifacts = folder.parent.name == '.artifacts' and folder.parent.parent.is_dir()  # first output in a repo
    if not folder.parent.is_dir() and not fresh_artifacts:
        print(f'BLOCKED: parent of the output folder {folder} does not exist')
        return 2
    folder.mkdir(parents=fresh_artifacts, exist_ok=True)
    browser = find_browser(browser_arg)
    if not browser:
        print('BLOCKED: no installed Edge or Chrome found; pass --browser PATH. Nothing is installed by this tool.')
        return 2
    targets = [(folder / f'{report.stem}-desktop.png', 1280), (folder / f'{report.stem}-narrow.png', 500)]
    for out, _ in targets:
        if out.exists():
            print(f'BLOCKED: {out} exists; never overwritten')
            return 2
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as profile:  # Edge holds files briefly on Windows
        for out, width in targets:
            result = subprocess.run(command(browser, report.as_uri(), out, width, height or 6000, profile),
                                    capture_output=True, text=True, timeout=120)
            # On Windows the launcher can return before its child process has written the file.
            for _ in range(60):
                if result.returncode != 0 or out.is_file():
                    break
                time.sleep(0.5)
            if result.returncode != 0 or not out.is_file():
                print(f'FAILED: {browser} exit {result.returncode}: {result.stderr.strip()[:300]}')
                return 1
            print(f'WROTE: {out}')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
