"""List what is still open across a project's workflow task records.

usage: python -X utf8 -I open_items.py <tasks-root> [--json]
       python -X utf8 -I open_items.py --task <task-folder>   one task at session start: checkpoint, latest
                                                              outcome, ticket states and record problems
                                                              (read this instead of every record file)
<tasks-root> is the folder holding task folders (usually docs/plans). Read-only.

Per task it reports the checkpoint phase line and, from TODO.md checkboxes or labelled ticket blocks:
open items, in-progress items, ticked items with no evidence pointer (unbacked), blocked items and
statuses it cannot read (unclear: an unlisted state or conflicting Status lines; neither open nor verified),
and overview-table rows that disagree with the tickets (the tickets' Status lines are the source; the table
is a summary that is reported, never used to decide a state).
Evidence pointer: a V-ID, or in older records `proof:`, `evidence:`, `verified:` or a FINDINGS reference.
An unbacked tick is reported, not trusted: the workflow treats it as unverified.
"""
from __future__ import annotations

import json
import importlib.util
import pathlib
import re
import sys

_spec = importlib.util.spec_from_file_location('workflow_ticket_records', pathlib.Path(__file__).with_name('ticket_records.py'))
tickets = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(tickets)

PHASE = re.compile(r'^-\s*(Updated\s*/\s*phase|Phase)\s*:\s*(?P<v>.+)$', re.I | re.M)
LABELS = (('overview', 'OVERVIEW TABLE DISAGREES WITH THE TICKETS (tickets are the source; correct the table)'),
          ('unclear', 'STATUS NOT RECOGNISED, RECONCILE (not counted as open or verified)'), ('blocked', 'BLOCKED'),
          ('unbacked', 'TICKED, NO EVIDENCE OR INCOMPLETE VERIFICATION'), ('in_progress', 'IN PROGRESS'),
          ('open', 'OPEN'), ('paused', 'PAUSED'), ('closed', 'CLOSED WITHOUT TEST PASS'))
NEXT = re.compile(r'^-\s*(Last result\s*/\s*)?next safe action\s*:\s*(?P<v>.+)$', re.I | re.M)


def scan(task: pathlib.Path) -> dict | None:
    todo = task / 'TODO.md'
    if not todo.is_file():
        return None
    row = {'task': task.name, 'open': [], 'in_progress': [], 'unbacked': [], 'blocked': [],
           'paused': [], 'closed': [], 'unclear': [], 'overview': [], 'done': 0}
    lines = todo.read_text(encoding='utf-8', errors='replace').splitlines()
    parsed = tickets.parse(lines)
    row['overview'] = [problem.message for problem in tickets.overview(lines, parsed)[1]]
    for item in parsed:
        if item.category == 'done':
            row['done'] += 1
        elif item.category == 'unclear':
            row['unclear'].append(f'{item.display} ({item.unclear})')
        else:
            row[item.category].append(item.display)
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
        print(f"\n## Tickets: {row['done']} recorded verified with evidence (not re-run)")
        for key, label in LABELS:
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
    pending = [r for r in rows if r['open'] or r['in_progress'] or r['unbacked'] or r['blocked'] or r['paused'] or r['unclear'] or r['overview']]
    print(f'{len(rows)} tasks with TODO.md; {len(pending)} with open, unbacked or blocked items.')
    for r in pending:
        print(f"\n## {r['task']}\n   phase: {r['phase']}")
        if r['next']:
            print(f"   next: {r['next']}")
        for key, label in LABELS:
            for item in r[key]:
                print(f'   {label}: {item}')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
