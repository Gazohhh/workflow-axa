"""List what is still open across a project's workflow task records.

usage: python -X utf8 -I open_items.py <tasks-root> [--json]
       python -X utf8 -I open_items.py --task <task-folder>   one task at session start: checkpoint, latest
                                                              outcome, ticket states and record problems
                                                              (read this instead of every record file)
<tasks-root> is the folder holding task folders (usually docs/plans). Read-only.

Per task it reports the checkpoint phase line and, from TODO.md checkboxes:
open items, in-progress items, ticked items with no evidence pointer (unbacked) and blocked items.
Evidence pointer: a V-ID, or in older records `proof:`, `evidence:`, `verified:` or a FINDINGS reference.
An unbacked tick is reported, not trusted: the workflow treats it as unverified.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

BOX = re.compile(r'^\s*[-*]\s+\[(?P<mark>[ xX~!-])\]\s+(?P<text>.+)$')
EVIDENCE = re.compile(r'\bV\d+\b|\b(proof|evidence|verified)\s*:|FINDINGS', re.I)
BLOCKED = re.compile(r'\bblocked\b', re.I)
PHASE = re.compile(r'^-\s*(Updated\s*/\s*phase|Phase)\s*:\s*(?P<v>.+)$', re.I | re.M)
NEXT = re.compile(r'^-\s*(Last result\s*/\s*)?next safe action\s*:\s*(?P<v>.+)$', re.I | re.M)


def scan(task: pathlib.Path) -> dict | None:
    todo = task / 'TODO.md'
    if not todo.is_file():
        return None
    row = {'task': task.name, 'open': [], 'in_progress': [], 'unbacked': [], 'blocked': [], 'done': 0}
    for line in todo.read_text(encoding='utf-8', errors='replace').splitlines():
        m = BOX.match(line)
        if not m:
            continue
        mark, text = m['mark'], m['text'].strip()
        short = text[:140]
        if BLOCKED.search(text) and mark.lower() != 'x':
            row['blocked'].append(short)
        elif mark == ' ':
            row['open'].append(short)
        elif mark in '~-!':
            row['in_progress'].append(short)
        elif EVIDENCE.search(text):
            row['done'] += 1
        else:
            row['unbacked'].append(short)
    plan = task / 'PLAN.md'
    text = plan.read_text(encoding='utf-8', errors='replace') if plan.is_file() else ''
    row['phase'] = (PHASE.search(text)['v'].strip() if PHASE.search(text) else 'unknown')[:160]
    row['next'] = (NEXT.search(text)['v'].strip() if NEXT.search(text) else '')[:160]
    return row


def record_problems(task: pathlib.Path) -> list[str]:
    """Mechanical damage seen in real runs: non-UTF-8 bytes and mixed line endings."""
    problems = []
    for path in sorted(task.glob('*.md')):
        raw = path.read_bytes()
        try:
            raw.decode('utf-8')
        except UnicodeDecodeError as exc:
            problems.append(f'{path.name}: not valid UTF-8 at byte {exc.start}')
        crlf, lf = raw.count(b'\r\n'), raw.count(b'\n')
        if crlf and lf != crlf:
            problems.append(f'{path.name}: mixed line endings ({crlf} CRLF, {lf - crlf} LF)')
    return problems


def section(text: str, heading: str) -> str:
    m = re.search(r'^## ' + re.escape(heading) + r'[^\n]*\n(.*?)(?=^## |\Z)', text, re.M | re.S)
    return m[1].strip() if m else ''


def task_view(task: pathlib.Path) -> int:
    """One task at session start: checkpoint, ticket states, latest outcome, record problems."""
    if not task.is_dir():
        print(f'BLOCKED: {task} is not a folder')
        return 2
    plan = task / 'PLAN.md'
    text = plan.read_text(encoding='utf-8', errors='replace') if plan.is_file() else ''
    print(f'# {task.name}\n\n## Current checkpoint\n{section(text, "Current checkpoint") or "(none)"}')
    outcomes = re.findall(r'^## (Outcome[^\n]*)', text, re.M)
    if outcomes:
        print(f'\n## Latest {outcomes[-1]}\n{section(text, outcomes[-1])[:1500]}')
    row = scan(task)
    if row:
        print(f"\n## Tickets: {row['done']} done with evidence")
        for key, label in (('blocked', 'BLOCKED'), ('unbacked', 'TICKED, NO EVIDENCE'), ('in_progress', 'IN PROGRESS'), ('open', 'OPEN')):
            for item in row[key]:
                print(f'- {label}: {item}')
    problems = record_problems(task)
    print('\n## Record problems\n' + ('\n'.join(f'- {p}' for p in problems) if problems else '- none'))
    return 0


def main(argv: list[str]) -> int:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')  # Windows consoles default to cp1252
    if len(argv) >= 3 and argv[1] == '--task':
        return task_view(pathlib.Path(argv[2]))
    if len(argv) < 2:
        print(__doc__)
        return 2
    root = pathlib.Path(argv[1])
    if not root.is_dir():
        print(f'BLOCKED: {root} is not a folder')
        return 2
    rows = [r for r in (scan(p) for p in sorted(root.iterdir()) if p.is_dir()) if r]
    if '--json' in argv:
        print(json.dumps(rows, indent=1))
        return 0
    pending = [r for r in rows if r['open'] or r['in_progress'] or r['unbacked'] or r['blocked']]
    print(f'{len(rows)} tasks with TODO.md; {len(pending)} with open, unbacked or blocked items.')
    for r in pending:
        print(f"\n## {r['task']}\n   phase: {r['phase']}")
        if r['next']:
            print(f"   next: {r['next']}")
        for key, label in (('blocked', 'BLOCKED'), ('unbacked', 'TICKED, NO EVIDENCE'), ('in_progress', 'IN PROGRESS'), ('open', 'OPEN')):
            for item in r[key]:
                print(f'   {label}: {item}')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
