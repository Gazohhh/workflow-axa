"""Small, line-ending-safe edits to workflow task records (PLAN, TODO, FINDINGS, DECISIONS).

usage:
  python -X utf8 -I record.py new      <file> <text-file | ->       create a record that does not exist yet
  python -X utf8 -I record.py append   <file> <text-file | ->       append text (a blank line separates it)
  python -X utf8 -I record.py replace-section <file> "<## Heading>" <text-file | ->
                                                                   replace everything under that heading, up to
                                                                   the next heading of the same or higher level
  python -X utf8 -I record.py set-line <file> <line-prefix> <new-line>  replace the first line starting with the prefix
  python -X utf8 -I record.py tick     <TODO.md> <ticket-id> <evidence>  mark a checkbox or labelled ticket verified with evidence
  python -X utf8 -I record.py batch    <file> <edits.json | ->      several exact replacements in one call:
                                                                   [{"find": "old text", "replace": "new text"}, ...]

Keeps each line's ending as found (CRLF, LF or a mix; added lines take the file's main ending; `new` follows its
input or sibling records), a UTF-8 byte order mark, and the encoding (UTF-8; other encodings are refused). A tick
also sets the ticket's row in a TODO overview table to Verified, and refuses while that row disagrees with the
ticket. Refuses to tick without evidence, to tick an ambiguous, missing, blocked, incomplete or cancelled ([-]) ticket (the ID must match exactly: T1 is not T1.2), or to
replace a line that does not exist. A batch changes nothing unless every "find" text occurs exactly once in the
original text (compare with LF line breaks) and no two finds overlap. Prints what changed.

Safe writes: the new text goes to a temp file in the same folder, is flushed to disk and then replaces the record in
one step, so a crash leaves the old or the new file, never a cut-off one. A lock file (<name>.lock, holding a unique
token) is held from the read to the replace; a second writer is refused while it exists. A lock older than 5 minutes
is taken over by renaming it aside, and a writer deletes the lock only while it still holds its own token. If the
file changed since it was read (another tool or an editor), the write is refused and the file is left alone. Not
caught: a change by a tool that ignores the lock, made in the tiny window after the final check and before the
replace; that change is overwritten. A symbolic link is resolved first, so its target is edited and the link stays.
"""
from __future__ import annotations

import contextlib
import difflib
import hashlib
import importlib.util
import json
import os
import pathlib
import re
import secrets
import stat
import sys
import tempfile
import time
from typing import NamedTuple

_ticket_spec = importlib.util.spec_from_file_location('workflow_ticket_records', pathlib.Path(__file__).with_name('ticket_records.py'))
tickets = importlib.util.module_from_spec(_ticket_spec)
_ticket_spec.loader.exec_module(tickets)

BOM = b'\xef\xbb\xbf'
LOCK_STALE_SECONDS = 300


class Blocked(Exception):
    """A refusal: printed as 'BLOCKED: <message>' with its exit code; the record is untouched."""

    def __init__(self, message: str, code: int = 1):
        super().__init__(message)
        self.code = code


class Record(NamedTuple):
    lines: list[str]    # the text split at line breaks; a final '' means the file ends with a line break
    endings: list[str]  # endings[i] is the break after lines[i] ('\r\n' or '\n'); one fewer than lines
    eol: str            # the ending for added lines: the file's main one
    bom: bool
    digest: str         # SHA-256 of the bytes that were read


def decode(raw: bytes, what: object) -> str:
    try:
        return raw.decode('utf-8')
    except UnicodeDecodeError as exc:
        raise Blocked(f'{what} is not UTF-8 text (invalid byte at offset {exc.start}); convert it to UTF-8 first', 2)


def load(path: pathlib.Path) -> Record:
    raw = path.read_bytes()
    bom = raw.startswith(BOM)
    parts = re.split(r'(\r\n|\n)', decode(raw[len(BOM):] if bom else raw, path))
    endings = parts[1::2]
    crlf = endings.count('\r\n')
    eol = '\r\n' if crlf and crlf >= len(endings) - crlf else '\n'
    return Record(parts[0::2], endings, eol, bom, hashlib.sha256(raw).hexdigest())


def render(record: Record, lines: list[str]) -> bytes:
    """Join edited lines. A line kept, or replaced one for one, keeps its old ending; an added line gets the main one."""
    kept: list[str | None] = [None] * len(lines)
    matcher = difflib.SequenceMatcher(None, record.lines, lines, autojunk=False)
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'equal' or (tag == 'replace' and i2 - i1 == j2 - j1):
            for k in range(j2 - j1):
                if i1 + k < len(record.endings):
                    kept[j1 + k] = record.endings[i1 + k]
    out = []
    for k, line in enumerate(lines):
        out.append(line)
        if k < len(lines) - 1:
            out.append(kept[k] or record.eol)
    return (BOM if record.bom else b'') + ''.join(out).encode('utf-8')


@contextlib.contextmanager
def locked(path: pathlib.Path):
    """Hold <name>.lock, created exclusively, from the read to the replace. Take over one older than 5 minutes."""
    lock = path.with_name(path.name + '.lock')
    token = f'pid {os.getpid()} {secrets.token_hex(8)}\n'.encode()
    busy = f'{path} is being changed by another writer ({lock.name}); retry when it is done'
    for attempt in (1, 2):
        try:
            fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY | getattr(os, 'O_BINARY', 0))
            break
        except FileExistsError:
            try:
                seen, age = lock.read_bytes(), time.time() - lock.stat().st_mtime
            except FileNotFoundError:
                continue  # released meanwhile
            if attempt == 2 or age < LOCK_STALE_SECONDS:
                raise Blocked(f'{path} is being changed by another writer ({lock.name}, {age:.0f}s old); '
                              'retry when it is done') from None
            take_over_stale(lock, seen, token, busy)
            leftovers = sorted(p.name for p in path.parent.glob(f'.{path.name}.*.tmp'))
            print(f'taking over stale lock {lock.name} ({age:.0f}s old; its writer probably crashed)'
                  + (f'; leftover temp files you may delete: {", ".join(leftovers)}' if leftovers else ''))
    else:
        raise Blocked(busy)
    try:
        os.write(fd, token)
        os.close(fd)
        yield
    finally:
        with contextlib.suppress(OSError):
            if lock.read_bytes() == token:  # never delete a lock another writer took over
                lock.unlink()


def take_over_stale(lock: pathlib.Path, seen: bytes, token: bytes, busy: str) -> None:
    """Move a stale lock aside in one step (a rename), then check that it was the stale one we inspected."""
    aside = lock.with_name(f'{lock.name}.stale-{token.split()[-1].decode()}')
    try:
        os.rename(lock, aside)
    except FileNotFoundError:
        return  # someone released or moved it; just try to create ours
    if aside.read_bytes() == seen:
        aside.unlink(missing_ok=True)
        return
    # A rival replaced the stale lock after our check: we moved a live lock. Put it back and give way.
    try:
        os.link(aside, lock)  # exclusive: never overwrites a newer lock
    except FileExistsError:
        pass
    except OSError:  # no hard links on this file system
        with contextlib.suppress(OSError):
            os.rename(aside, lock)
    aside.unlink(missing_ok=True)
    raise Blocked(busy)


def write_safely(path: pathlib.Path, data: bytes, digest: str | None = None) -> None:
    """Write a temp file in the same folder, flush it to disk, then move it onto the record in one step.

    With a digest, refuse when the record's bytes no longer match the bytes that were read. Without one, create
    the record exclusively: refuse when it exists by then."""
    fd, name = tempfile.mkstemp(dir=path.parent, prefix=f'.{path.name}.', suffix='.tmp')
    tmp = pathlib.Path(name)
    try:
        try:
            view = memoryview(data)
            while view:
                view = view[os.write(fd, view):]
            os.fsync(fd)
        finally:
            os.close(fd)
        if os.name != 'nt':  # mkstemp makes the file 0600: give it the record's mode, or the default for a new one
            if digest is None:
                umask = os.umask(0)
                os.umask(umask)
                os.chmod(tmp, 0o666 & ~umask)
            else:
                os.chmod(tmp, stat.S_IMODE(path.stat().st_mode))
        if digest is None:
            try:
                os.link(tmp, path)  # atomic and exclusive
            except FileExistsError:
                raise Blocked(f'{path} exists; use append or replace-section', 2) from None
            except OSError:  # no hard links on this file system: create exclusively, then write
                with open(path, 'xb') as handle:
                    handle.write(data)
                    handle.flush()
                    os.fsync(handle.fileno())
        else:
            if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
                raise Blocked(f'{path} changed since it was read; reload and retry')
            try:
                os.replace(tmp, path)
            except OSError as exc:
                raise Blocked(f'could not replace {path} ({exc}); the record is unchanged') from None
        if os.name != 'nt':  # make the rename itself durable
            with contextlib.suppress(OSError):
                dir_fd = os.open(path.parent, os.O_RDONLY)
                try:
                    os.fsync(dir_fd)
                finally:
                    os.close(dir_fd)
    finally:
        tmp.unlink(missing_ok=True)


def save(path: pathlib.Path, record: Record, lines: list[str]) -> None:
    write_safely(path, render(record, lines), record.digest)


def read_text(source: str) -> str:
    """Text from a file, or from stdin when the source is '-'. Write that file with the file tool, not a heredoc."""
    raw = sys.stdin.buffer.read() if source == '-' else pathlib.Path(source).read_bytes()
    if raw.startswith(BOM):
        raw = raw[len(BOM):]
    return decode(raw, 'the standard input' if source == '-' else source)  # bytes, so CRLF in the input survives


def main(argv: list[str]) -> int:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')  # Windows consoles default to cp1252
    if len(argv) < 4 or argv[1] not in ('new', 'append', 'set-line', 'replace-section', 'tick', 'batch'):
        print(__doc__)
        return 2
    command, path = argv[1], pathlib.Path(argv[2])
    if path.is_symlink():  # edit the target once: replacing the link itself would turn it into a plain file
        path = path.resolve()
    try:
        if command == 'new':
            if path.exists():
                print(f'BLOCKED: {path} exists; use append or replace-section')
                return 2
            if not path.parent.is_dir():
                print(f'BLOCKED: folder {path.parent} does not exist')
                return 2
            with locked(path):
                return create(path, read_text(argv[3]))
        if not path.is_file():
            print(f'BLOCKED: {path} does not exist')
            return 2
        with locked(path):
            return edit(command, path, load(path), argv)
    except Blocked as exc:
        print(f'BLOCKED: {exc}')
        return exc.code


def create(path: pathlib.Path, text: str) -> int:
    # Match the folder: CRLF when the input or a sibling record uses it (round-4 retro: CRLF project got LF).
    siblings = [p for p in path.parent.glob('*.md') if p.is_file()]
    crlf = '\r\n' in text or any(b'\r\n' in p.read_bytes() for p in siblings)
    eol = '\r\n' if crlf else '\n'
    lines = text.replace('\r\n', '\n').rstrip('\n').split('\n')
    write_safely(path, (eol.join(lines) + eol).encode('utf-8'))
    print(f'created {path.name} ({"CRLF" if crlf else "LF"})')
    return 0


def edit(command: str, path: pathlib.Path, record: Record, argv: list[str]) -> int:
    lines = list(record.lines)
    if command == 'batch':
        try:
            edits = json.loads(read_text(argv[3]))
        except ValueError as exc:
            print(f'BLOCKED: edits are not valid JSON: {exc}')
            return 2
        if (not isinstance(edits, list) or not edits or
                not all(isinstance(e, dict) and set(e) == {'find', 'replace'} and isinstance(e['find'], str)
                        and e['find'] and isinstance(e['replace'], str) for e in edits)):
            print('BLOCKED: edits must be a non-empty list of {"find": ..., "replace": ...} objects')
            return 2
        # Every find is matched against the original text, so one edit cannot create the match for the next.
        text = '\n'.join(lines)
        spans = []
        for number, change in enumerate(edits, 1):
            find = change['find'].replace('\r\n', '\n')
            count = len(re.findall('(?=' + re.escape(find) + ')', text))
            if count != 1:
                print(f'BLOCKED: edit {number} "find" occurs {count} times in {path.name} before any edit '
                      '(needs exactly 1; every find is matched against the original text); nothing changed')
                return 1
            start = text.index(find)
            spans.append((start, start + len(find), change['replace'].replace('\r\n', '\n'), number))
        spans.sort()
        for (_, end, _, first), (start, _, _, second) in zip(spans, spans[1:]):
            if start < end:
                print(f'BLOCKED: edits {first} and {second} overlap in {path.name}; merge them; nothing changed')
                return 1
        out, position = [], 0
        for start, end, replacement, _ in spans:
            out += [text[position:start], replacement]
            position = end
        out.append(text[position:])
        save(path, record, ''.join(out).split('\n'))
        print(f'{path.name}: {len(edits)} edits applied')
        return 0
    if command == 'replace-section':
        if len(argv) != 5:
            print(__doc__)
            return 2
        heading, body = argv[3].rstrip(), read_text(argv[4]).replace('\r\n', '\n').strip('\n').split('\n')
        level = len(heading) - len(heading.lstrip('#'))
        if level == 0 or heading not in lines:
            print(f'BLOCKED: heading {heading!r} not found in {path.name} (give it exactly, with its #)')
            return 1
        if lines.count(heading) > 1 or heading in body:  # round 7: a body repeating its heading duplicated it
            print(f'BLOCKED: {heading!r} would appear twice in {path.name}; give only the text under the heading '
                  'and remove any duplicate first')
            return 1
        start = lines.index(heading) + 1
        end = next((i for i in range(start, len(lines))
                    if lines[i].startswith('#') and len(lines[i]) - len(lines[i].lstrip('#')) <= level), len(lines))
        tail = lines[end:]
        lines[start:] = [''] + body + ([''] if tail else []) + tail
        save(path, record, lines)
        print(f'{path.name}: replaced section {heading}')
        return 0
    if command == 'append':
        text = read_text(argv[3])
        while lines and lines[-1] == '':
            lines.pop()
        lines += [''] + text.replace('\r\n', '\n').rstrip('\n').split('\n') + ['']
        save(path, record, lines)
        print(f'appended {len(text.splitlines())} lines to {path.name}')
        return 0
    if command == 'set-line':
        if len(argv) != 5:
            print(__doc__)
            return 2
        prefix, new = argv[3], argv[4]
        for i, line in enumerate(lines):
            if line.startswith(prefix):
                lines[i] = new
                save(path, record, lines)
                print(f'{path.name}:{i + 1} replaced')
                return 0
        print(f'BLOCKED: no line starts with {prefix!r} in {path.name}')
        return 1
    if len(argv) != 5 or not argv[4].strip():
        print('BLOCKED: tick needs evidence (a V-ID or FINDINGS pointer)')
        return 1
    ticket, evidence = argv[3], argv[4].strip()
    evidence = re.sub(r'^(?:verified:\s*)+', '', evidence, flags=re.I)  # the tool adds the prefix itself (round 15)
    if evidence.casefold() in tickets.NONE or tickets.INCOMPLETE.search(evidence):
        print('BLOCKED: the supplied evidence is empty, a placeholder or explicitly incomplete; nothing changed')
        return 1
    parsed = tickets.parse(lines)
    matches = tickets.select(parsed, ticket)
    if len(matches) > 1:
        names = ', '.join(f'{item.qualified} at line {item.start + 1}' for item in matches)
        print(f'BLOCKED: {ticket} is ambiguous ({names}); use its existing revision-qualified ID. Nothing changed')
        return 1
    if not matches:
        print(f'BLOCKED: no open ticket for {ticket} in {path.name}')
        return 1
    item = matches[0]
    if item.closed:
        print(f'BLOCKED: {ticket} is cancelled or otherwise closed without a test pass; reopen only with authority')
        return 1
    if item.unclear:
        print(f'BLOCKED: {ticket} has an unreadable status ({item.unclear}); reconcile it with a listed state first. '
              'Nothing changed')
        return 1
    if item.complete_claim:
        print(f'BLOCKED: {ticket} is already checked or marked verified; reconcile its evidence rather than ticking twice')
        return 1
    if item.incomplete or item.blocked:
        print(f'BLOCKED: {ticket} records incomplete verification or a blocker (or a human check with no Owner '
              'acceptance result); record the actual results and resolve or explicitly rescope outstanding '
              'acceptance before marking verified. Nothing changed')
        return 1
    rows, problems = tickets.overview(lines, parsed)
    ours = [p.message for p in problems if item.qualified in p.tickets]
    if ours:
        print(f'BLOCKED: the TODO overview table disagrees with {ticket} ({"; ".join(ours)}); correct the table '
              'from the ticket first. Nothing changed')
        return 1
    row = next((r for r in rows if r.ticket is not None and r.ticket.qualified == item.qualified), None)
    if row is not None:  # the row agrees with the ticket (checked above), so both change together
        a, b = row.cells[row.status]
        cell = lines[row.line][a:b]
        word = 'verified' if cell.strip().lstrip('*`')[:1].islower() else 'Verified'
        lines[row.line] = lines[row.line][:a] + cell.replace(cell.strip(), word, 1) + lines[row.line][b:]
    if item.mark is not None:
        box = tickets.BOX.match(lines[item.start])
        prefix = lines[item.start][:box.start('mark')]
        suffix = lines[item.start][box.end('mark'):].rstrip()
        lines[item.start] = f'{prefix}x{suffix}; verified: {evidence}'
    else:
        statuses = item.fields.get('status', [])
        refs = item.fields.get('evidence', [])
        if len(statuses) != 1 or len(refs) > 1:
            print(f'BLOCKED: {ticket} needs one unambiguous Status field and at most one Evidence field')
            return 1
        line, value = statuses[0]
        label = tickets.FIELD.match(lines[line])  # keep the label as written: `- Status:`, `**Status**:`
        lines[line] = lines[line][:label.start(2)] + ('Verified' if value[:1].isupper() else 'verified')
        if refs:
            index, previous = refs[0]
            prefix = lines[index][:tickets.FIELD.match(lines[index]).start(2)]
            if previous.casefold() in tickets.NONE:
                previous = ''
            lines[index] = prefix + (previous + '; ' if previous and evidence not in previous.split('; ') else '') + evidence
        else:
            lines.insert(statuses[0][0] + 1, 'Evidence: ' + evidence)
    save(path, record, lines)
    print(f'{path.name}:{item.start + 1} {item.qualified} verified with recorded evidence')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
