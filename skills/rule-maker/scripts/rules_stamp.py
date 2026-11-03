#!/usr/bin/env python3
"""Compare a project's `workflow-axa rules checked` line with the installed rules library. Read-only.

usage: python -X utf8 -I rules_stamp.py <project-root>

Prints one state and what to do. CURRENT: say nothing. BEHIND: tell the owner in one line which changes are
newer (printed from rules/CHANGES.md) and offer the rules audit; never block. NONE: run the normal readiness
check; after a passed audit, offer the printed line. AHEAD: the installed library is older than the project's
line, so the install needs updating. Always exits 0 except on bad usage, because the line is information only.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

RULES = Path(__file__).resolve().parents[1] / 'rules'
STAMP = re.compile(r'workflow-axa rules checked:\s*(\d+\.\d+\.\d+)\s*\((\d{4}-\d{2}-\d{2})\)', re.I)
HEADING = re.compile(r'^## (\d+\.\d+\.\d+)\b.*$', re.M)
FILES = ('AGENTS.md', 'CLAUDE.md')


def version(text: str) -> tuple[int, ...]:
    return tuple(int(part) for part in text.split('.'))


def project_stamp(root: Path) -> tuple[str, str, str] | None:
    """(version, date, file) of the first line found in the root rule files."""
    for name in FILES:
        path = root / name
        if path.is_file():
            found = STAMP.search(path.read_text(encoding='utf-8', errors='replace'))
            if found:
                return found[1], found[2], name
    return None


def changes_since(stamp: str) -> str:
    """The CHANGES.md sections newer than the stamp, as written."""
    text = (RULES / 'CHANGES.md').read_text(encoding='utf-8')
    heads = list(HEADING.finditer(text))
    parts = []
    for i, head in enumerate(heads):
        if version(head[1]) > version(stamp):
            end = heads[i + 1].start() if i + 1 < len(heads) else len(text)
            parts.append(text[head.start():end].strip())
    return '\n\n'.join(parts)


def main(argv: list[str]) -> int:
    if len(argv) != 2 or not Path(argv[1]).is_dir():
        print(__doc__)
        return 2
    root = Path(argv[1]).resolve()
    installed = json.loads((RULES / 'version.json').read_text(encoding='utf-8'))['rules_version']
    line = f'workflow-axa rules checked: {installed} (YYYY-MM-DD)'
    stamp = project_stamp(root)
    if stamp is None:
        print(f'STATE: NONE (installed rules {installed})')
        print('No line in AGENTS.md or CLAUDE.md. Run the normal readiness check. After a passed setup or audit, '
              f'offer the owner this line for the root AGENTS.md, with today\'s date: {line}')
        return 0
    found, date, name = stamp
    if version(found) == version(installed):
        print(f'STATE: CURRENT {found} ({name}, checked {date})')
        print('Say nothing about versions; continue with the normal readiness check.')
    elif version(found) > version(installed):
        print(f'STATE: AHEAD project {found} ({name}) > installed {installed}')
        print('The installed rules library is older than the one this project was checked with. Tell the owner '
              'to update the install (workflow-doctor); keep using the project rules meanwhile.')
    else:
        newer = changes_since(found)
        versions = ', '.join(HEADING.findall(newer))
        print(f'STATE: BEHIND project {found} ({name}, checked {date}) < installed {installed}')
        print('Put the SAY sentence in your next reply to the owner, once. Never block the task on it; continue '
              'with the normal readiness check.')
        print(f'SAY: This project\'s rules were last checked against shared rules {found}. Newer changes: {versions}. '
              'Do you want the rules audit for just those changes? It does not hold up this task.\n')
        print(newer)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
