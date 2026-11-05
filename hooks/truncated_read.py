"""PostToolUse hook: warn (never block) about two habits that broke real runs.

1. A workflow-axa instruction file read only in part (runs read TASK-FOLDER.md 80 of 110 lines and missed
   the rules at the end).
2. A task record (PLAN/TODO/FINDINGS/DECISIONS.md) edited in place with sed -i, >> or a str.replace script,
   which fails silently when the text does not match; scripts/record.py fails loudly instead.

It reads the tool call as JSON on stdin and always exits 0. Each pipeline segment is checked on its own, so a
`| head` on a grep does not flag a cat earlier in the command, and `head -N` that covers the whole file is fine.
"""
from __future__ import annotations

import json
import os
import posixpath
from pathlib import Path
import re
import sys

PARTIAL = re.compile(r'\|\s*(head|tail)\b|\bsed\s+-n\b|\bhead\s+-|\btail\s+-|\bawk\s+.NR')
LIMIT = re.compile(r'\bhead\s+-n?\s*(\d+)|\bsed\s+-n\s+["\']?1,(\d+)p')
RECORD_EDIT = re.compile(r'\bsed\s+-i\b|>>|\.replace\(|\bperl\s+-pi\b')
RECORD = re.compile(r'(?:^|[\s"\'/\\])(PLAN|TODO|FINDINGS|DECISIONS)\.md\b')
SEGMENTS = re.compile(r'&&|\|\||;|\n')
SEARCH = re.compile(r'\s*(grep|rg|ls|find|wc|git|python\S*|node|npm|npx)\b')  # searches and tools, not reads


def local(path: str) -> str:
    """Git Bash /d/x -> d:/x; no filesystem access or guessed install location."""
    return re.sub(r'^/([a-zA-Z])(?=/|$)', r'\1:', path.replace('\\', '/'))


def norm(path: str, base: str = '', fold: bool = True) -> str:
    """Normalised path; Windows paths are case-folded for comparing only (fold=False keeps the spelling to show)."""
    p = local(path.strip())
    if not re.match(r'^(?:[a-zA-Z]:|/|~)', p) and base:
        p = local(base).rstrip('/') + '/' + p
    p = posixpath.normpath(p).rstrip('/')
    return p.casefold() if fold and (re.match(r'^[a-zA-Z]:', p) or p.startswith('//')) else p


def in_package(path: str, root: str) -> bool:
    candidate, package = norm(path), norm(root)
    if not root:
        return False
    return candidate.startswith(package + '/skills/')


def lines(path: str, base: str | None) -> int | None:
    file = Path(local(path)) if base is None else Path(local(base), path)
    try:
        return len(file.read_text(encoding='utf-8', errors='replace').splitlines())
    except OSError:
        return None


def covered(paths: list[tuple[str, str | None]], segment: str) -> bool:
    """True when head/sed includes all lines; unreadable files cannot prove full coverage."""
    match = LIMIT.search(segment)
    if not match:
        return False
    counts = [lines(path, base) for path, base in paths]
    return None not in counts and sum(counts) <= int(match.group(1) or match.group(2))


def partial_reads(command: str, root: str, cwd: str = '') -> list[str]:
    found, current = [], norm(cwd or root, fold=False)  # kept as typed for the message; matching folds
    # Best-effort literal commands, not a full shell interpreter. Variables/dynamic cd
    # remain unknown; this warning hook never grants permissions or blocks execution.
    for segment in SEGMENTS.split(command):
        cd = re.match(r"\s*(?:\(\s*)?cd\s+(?:--\s+)?(?:\"([^\"]+)\"|'([^']+)'|([^\s;&|]+))", segment)
        if cd:
            target = next(value for value in cd.groups() if value is not None)
            current = norm(target, current, fold=False) if '$' not in target and '`' not in target else ''
            continue
        whole_file_grep = re.match(r"\s*grep\s+(?:-\w+\s+)*(?:\"\"|''|'\^'|\"\^\")\s", segment)
        if not PARTIAL.search(segment) or (SEARCH.match(segment) and not whole_file_grep):
            continue
        paths = []
        for match in re.finditer(r"\"([^\"]+\.md)\"|'([^']+\.md)'|([\w:./\\~-]+\.md)\b", segment):
            path = next(value for value in match.groups() if value is not None)
            absolute = bool(re.match(r'^(?:[a-zA-Z]:|/|~)', path))
            resolved = norm(path, '' if absolute else current)
            if (absolute or current) and in_package(resolved, root):
                paths.append((norm(path, '' if absolute else current, fold=False), None))  # shown as typed
        if paths and not covered(paths, segment):
            found += [path for path, _ in paths]
    return found


def record_edits(command: str) -> list[str]:
    hits = []
    # Round 17: `F=.../PLAN.md; sed -i ... $F` hid the record name behind a shell variable.
    for name, _, value in re.findall(r'\b([A-Za-z_]\w*)=(["\']?)([^\s;&|"\']+)\2', command):
        command = re.sub(r'\$\{?' + name + r'\}?\b', value, command)
    for segment in [command] if '<<' in command else SEGMENTS.split(command):  # a heredoc script is one unit
        if RECORD_EDIT.search(segment):
            hits += [m.group(1) + '.md' for m in RECORD.finditer(segment)]
    return hits


def main() -> int:
    try:
        event = json.load(sys.stdin)
    except ValueError:
        return 0
    tool, data = event.get('tool_name'), event.get('tool_input') or {}
    root = norm(os.environ.get('CLAUDE_PLUGIN_ROOT') or str(Path(__file__).resolve().parents[1]))
    notes: list[str] = []
    files: list[str] = []
    if tool == 'Read' and data.get('limit'):  # an offset alone reads to the end (round-6b: false warning)
        path = str(data.get('file_path', ''))
        if path.lower().endswith('.md') and in_package(norm(path, str(event.get('cwd') or root)), root):
            files = [path]
    elif tool == 'Bash':
        command = str(data.get('command', ''))
        files = partial_reads(command, root, str(event.get('cwd') or ''))
        edits = record_edits(command)
        if edits:
            notes.append(f"workflow-axa: {', '.join(sorted(set(edits)))} edited in place with sed -i, >> or a script. "
                         "These change nothing when the text differs, and in shell heredocs a backslash (a Windows path, "
                         "\\a, \\n) can become a control character inside the record. Write the new text to a file with "
                         "the file tool, then run e.g. `python -X utf8 -I <workflow>/scripts/record.py append PLAN.md "
                         "note.md` (also replace-section, set-line, tick, batch); it fails loudly and keeps line endings.")
    if files:
        notes.insert(0, f"workflow-axa: you read only part of {', '.join(sorted(set(files)))}. Package instruction "
                        "files must be read whole; rules at the end (revisions, gates, done-when) get missed "
                        "otherwise. Read the whole file before acting on it.")
    if notes:
        print(json.dumps({'hookSpecificOutput': {'hookEventName': 'PostToolUse', 'additionalContext': ' '.join(notes)}}))
    return 0


if __name__ == '__main__':
    sys.exit(main())
