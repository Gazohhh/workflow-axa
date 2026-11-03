"""Small, line-ending-safe edits to workflow task records (PLAN, TODO, FINDINGS, DECISIONS).

usage:
  python -X utf8 -I record.py new      <file> <text-file | ->       create a record that does not exist yet
  python -X utf8 -I record.py append   <file> <text-file | ->       append text (a blank line separates it)
  python -X utf8 -I record.py replace-section <file> "<## Heading>" <text-file | ->
                                                                   replace everything under that heading, up to
                                                                   the next heading of the same or higher level
  python -X utf8 -I record.py set-line <file> <line-prefix> <new-line>  replace the first line starting with the prefix
  python -X utf8 -I record.py tick     <TODO.md> <ticket-id> <evidence>  mark "- [ ] <id> ..." done with its evidence
  python -X utf8 -I record.py batch    <file> <edits.json | ->      several exact replacements in one call:
                                                                   [{"find": "old text", "replace": "new text"}, ...]

Keeps the file's existing line endings (CRLF or LF; `new` follows its input or sibling records) and encoding (UTF-8). Refuses to tick without evidence,
to tick a missing ticket, or to replace a line that does not exist. A batch changes nothing unless every "find"
text occurs exactly once (compare with LF line breaks). Prints what changed.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys


def load(path: pathlib.Path) -> tuple[list[str], str]:
    raw = path.read_bytes().decode('utf-8')
    eol = '\r\n' if '\r\n' in raw else '\n'
    return raw.replace('\r\n', '\n').split('\n'), eol


def save(path: pathlib.Path, lines: list[str], eol: str) -> None:
    path.write_bytes(eol.join(lines).encode('utf-8'))


def read_text(source: str) -> str:
    """Text from a file, or from stdin when the source is '-'. Write that file with the file tool, not a heredoc."""
    raw = sys.stdin.buffer.read() if source == '-' else pathlib.Path(source).read_bytes()
    return raw.decode('utf-8-sig')  # bytes, so CRLF in the input survives


def main(argv: list[str]) -> int:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')  # Windows consoles default to cp1252
    if len(argv) < 4 or argv[1] not in ('new', 'append', 'set-line', 'replace-section', 'tick', 'batch'):
        print(__doc__)
        return 2
    command, path = argv[1], pathlib.Path(argv[2])
    if command == 'new':
        if path.exists():
            print(f'BLOCKED: {path} exists; use append or replace-section')
            return 2
        if not path.parent.is_dir():
            print(f'BLOCKED: folder {path.parent} does not exist')
            return 2
        text = read_text(argv[3])
        # Match the folder: CRLF when the input or a sibling record uses it (round-4 retro: CRLF project got LF).
        siblings = [p for p in path.parent.glob('*.md') if p.is_file()]
        crlf = '\r\n' in text or any(b'\r\n' in p.read_bytes() for p in siblings)
        eol = '\r\n' if crlf else '\n'
        lines = text.replace('\r\n', '\n').rstrip('\n').split('\n')
        path.write_bytes((eol.join(lines) + eol).encode('utf-8'))
        print(f'created {path.name} ({"CRLF" if crlf else "LF"})')
        return 0
    if not path.is_file():
        print(f'BLOCKED: {path} does not exist')
        return 2
    lines, eol = load(path)
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
        text = '\n'.join(lines)
        for number, edit in enumerate(edits, 1):
            find = edit['find'].replace('\r\n', '\n')
            count = text.count(find)
            if count != 1:
                print(f'BLOCKED: edit {number} "find" occurs {count} times in {path.name} (needs exactly 1); nothing changed')
                return 1
            text = text.replace(find, edit['replace'].replace('\r\n', '\n'))
        save(path, text.split('\n'), eol)
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
        save(path, lines, eol)
        print(f'{path.name}: replaced section {heading}')
        return 0
    if command == 'append':
        text = read_text(argv[3])
        while lines and lines[-1] == '':
            lines.pop()
        lines += [''] + text.replace('\r\n', '\n').rstrip('\n').split('\n') + ['']
        save(path, lines, eol)
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
                save(path, lines, eol)
                print(f'{path.name}:{i + 1} replaced')
                return 0
        print(f'BLOCKED: no line starts with {prefix!r} in {path.name}')
        return 1
    if len(argv) != 5 or not argv[4].strip():
        print('BLOCKED: tick needs evidence (a V-ID or FINDINGS pointer)')
        return 1
    ticket, evidence = argv[3], argv[4].strip()
    evidence = re.sub(r'^(?:verified:\s*)+', '', evidence, flags=re.I)  # the tool adds the prefix itself (round 15)
    box = re.compile(r'^(\s*[-*]\s+)\[[ ~!-]\](\s+' + re.escape(ticket) + r'\b.*)$')
    for i, line in enumerate(lines):
        m = box.match(line)
        if m:
            lines[i] = f'{m[1]}[x]{m[2].rstrip()}; verified: {evidence}'
            save(path, lines, eol)
            print(f'{path.name}:{i + 1} {ticket} ticked')
            return 0
    print(f'BLOCKED: no open checkbox for {ticket} in {path.name}')
    return 1


if __name__ == '__main__':
    sys.exit(main(sys.argv))
