"""The one parser for `workflow-axa:required-read` declarations (G3 of the 2026-11-15 redesign).

Used by docs_check.py (reports malformed declarations as notes) and by hooks/phase_gate.py (enforces them). Grammar,
one declaration per HTML comment that starts its own line (at most three spaces in), outside code:

    <!-- workflow-axa:required-read phases=specify,execute,deliver path="tests/README.md" -->
    <!-- workflow-axa:required-read phases=specify path="docs/finance.md" paths="src/finance/**,app/Billing/*" -->

`path` is a literal root-relative file. The optional `paths` lists comma-separated root-relative globs (`*` stays in
one folder, `**` crosses folders, `?` is one character): the read is then required only for a task whose scope names a
matching file. Without `paths` the read applies to every task, as before.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

PHASES = ('specify', 'execute', 'deliver')
START = re.compile(r'^ {0,3}<!--\s*workflow-axa:required-read', re.M)
WHOLE = re.compile(r'<!--\s*workflow-axa:required-read(.*?)-->', re.S)
BODY = re.compile(r'\s+phases=([a-z]+(?:,[a-z]+)*)\s+path="([^"\r\n]+)"(?:\s+paths="([^"\r\n]+)")?\s*')
EXAMPLE = ('<!-- workflow-axa:required-read phases=specify,execute,deliver path="relative/file.md" -->, optionally '
           'with paths="src/area/**" after path')


@dataclass(frozen=True)
class Declaration:
    line: int  # 1-based line of the comment's start in the given text
    text: str  # the whole comment, whitespace collapsed (for messages)
    phases: tuple[str, ...] = ()
    path: str = ''
    paths: tuple[str, ...] = ()  # applicability globs; empty means every task
    error: str = ''  # why the declaration is malformed; empty when it is well formed


def literal(path: str) -> bool:
    """A literal root-relative path: no globs, URLs, absolute, backslash, empty or dot parts."""
    return bool(path) and path == path.strip() and '\\' not in path and not re.search(r'[*?\[\]{}]', path) \
        and not re.match(r'^[A-Za-z][\w+.-]*:', path) and not path.startswith(('/', '~')) \
        and all(part not in ('', '.', '..') for part in path.split('/'))


def glob_ok(pattern: str) -> bool:
    """A root-relative glob using only `*`, `**` and `?`: no absolute, URL, backslash, dot parts or brackets."""
    return bool(pattern) and pattern == pattern.strip() and '\\' not in pattern \
        and not re.search(r'[\[\]{}]', pattern) and not re.match(r'^[A-Za-z][\w+.-]*:', pattern) \
        and not pattern.startswith(('/', '~')) and all(part not in ('', '.', '..') for part in pattern.split('/'))


def parse(text: str) -> list[Declaration]:
    """Every declaration in text, which the caller has already stripped of code (fenced blocks, inline code).
    A malformed one carries its error; the caller decides whether that blocks or is a note."""
    found = []
    for start in START.finditer(text):
        line = text.count('\n', 0, start.start()) + 1
        whole = WHOLE.match(text, text.index('<!--', start.start()))
        shown = ' '.join((whole.group(0) if whole else text[start.start():start.start() + 120]).split())[:160]
        body = BODY.fullmatch(whole.group(1)) if whole else None
        if not body:
            found.append(Declaration(line, shown, error=f'malformed required-read declaration ({shown}); use {EXAMPLE}'))
            continue
        phases = tuple(body.group(1).split(','))
        globs = tuple(part.strip() for part in body.group(3).split(',')) if body.group(3) else ()
        if any(phase not in PHASES for phase in phases):
            error = f'malformed required-read declaration ({shown}); phases come from {", ".join(PHASES)}'
        elif not literal(body.group(2)):
            error = f'required-read declaration names path="{body.group(2)}", which is not a literal root-relative path'
        elif body.group(3) is not None and (not globs or not all(glob_ok(g) for g in globs)):
            error = f'required-read declaration has paths="{body.group(3)}", which is not a list of root-relative globs'
        else:
            error = ''
        found.append(Declaration(line, shown, phases, body.group(2), globs, error))
    return found


def _glob_regex(pattern: str) -> re.Pattern:
    out, i = [], 0
    while i < len(pattern):
        if pattern.startswith('**/', i):
            out.append('(?:.*/)?')
            i += 3
        elif pattern.startswith('**', i):
            out.append('.*')
            i += 2
        elif pattern[i] == '*':
            out.append('[^/]*')
            i += 1
        elif pattern[i] == '?':
            out.append('[^/]')
            i += 1
        else:
            out.append(re.escape(pattern[i]))
            i += 1
    return re.compile(''.join(out) + r'\Z', re.I)


def _overlaps(entry: str, pattern: str) -> bool:
    """Whether a scope entry could touch a file the glob matches. A folder entry (ending in `/`) or a glob entry
    overlaps when one literal prefix contains the other, so `src/` overlaps `src/finance/**` (conservative)."""
    if not entry.endswith('/') and not re.search(r'[*?]', entry):
        return bool(_glob_regex(pattern).match(entry))
    mine = re.split(r'[*?]', entry, maxsplit=1)[0]
    theirs = re.split(r'[*?]', pattern, maxsplit=1)[0]
    return mine.lower().startswith(theirs.lower()) or theirs.lower().startswith(mine.lower())


def applies(declaration: Declaration, scope: list[str] | None) -> bool:
    """Whether this read is required for a task with these root-relative scope entries (files, folders ending in
    `/`, or globs). A declaration without `paths` applies to every task. With `paths`: an unknown scope (None) means
    required (fail safe); a known scope requires it when any entry overlaps any glob."""
    if not declaration.paths or scope is None:
        return True
    return any(_overlaps(entry, pattern) for entry in scope for pattern in declaration.paths)
