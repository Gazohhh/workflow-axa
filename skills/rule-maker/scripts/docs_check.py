#!/usr/bin/env python3
"""Check the structure of a repository's instruction files and documentation index. Read-only.

usage: python -X utf8 -I docs_check.py <repo-root> [--json] [--changed PATH ... | --changed-from-git]

Starts at AGENTS.md (and CLAUDE.md) and follows relative Markdown links into the documents and subordinate
indexes they reach. An index document is a file named AGENTS.md, CLAUDE.md, README.md or index.md, or a
document that links at least two different .md documents with a .md link on at least half of its non-empty
lines (headings, code and comments aside). Only index documents add a level and only they form an index cycle.
Each finding has a severity: blocking, warning or note. Exits 1 when any finding is blocking, 2 on bad usage,
otherwise 0. Never writes a file; dependency, build and output folders and nested repositories (a folder with
its own .git) are not searched. Without an AGENTS.md, the root CLAUDE.md is the entry point. The plain run also
asks Git, read-only, which reached documents it does not track (a note each); without Git that check is skipped.

With --changed (or --changed-from-git, which asks Git read-only), it also lists the documents related to each
changed file and why: a changed document relates to itself; a reached document links the file or its folder, names
it in backticks, sits in the nearest folder above it with a README.md or docs/, or an index entry's `Covers:` hint
matches it. For those documents it
checks named facts (backticked paths, package/composer/make commands, version claims via version_facts.py) as
matched, contradicted (also a warning) or not-checkable. It never judges what a document means.
"""
from __future__ import annotations

import argparse
from collections import deque
from dataclasses import asdict, dataclass
import importlib.util
import json
import os
from pathlib import Path
import posixpath
import re
import subprocess
import sys
from urllib.parse import unquote


@dataclass(frozen=True)
class Finding:
    code: str
    severity: str  # blocking, warning or note
    path: str
    line: int
    message: str


@dataclass(frozen=True)
class Link:
    target: str  # as written, without the #fragment
    line: int


@dataclass(frozen=True)
class Repeat:
    text: str  # the normalized paragraph
    places: tuple[tuple[Path, int], ...]  # (file, first line) in the order the files were given


# A reference definition `[label]: path "title"`; footnotes (`[^1]:`) and prose after a colon are not definitions.
REFERENCE = re.compile(r'^ {0,3}\[([^\]^][^\]]*)\]:\s*(<[^>\n]*>|\S+)(?:\s+("[^"]*"|\'[^\']*\'|\([^)]*\)))?\s*$')
EXTERNAL = re.compile(r'^[A-Za-z][A-Za-z0-9+.-]+:')  # http:, https:, mailto: and other schemes
FENCE = re.compile(r'^\s*(`{3,}|~{3,})')
CODE_SPAN = re.compile(r'`[^`\n]*`')
# The required-read marker, matched like hooks/phase_gate.py (DECLARATION_START, DECLARATION, declared_path).
MARKER_START = re.compile(r'^ {0,3}<!--\s*workflow-axa:required-read', re.M)
MARKER = re.compile(r'<!--\s*workflow-axa:required-read(.*?)-->', re.S)
MARKER_BODY = re.compile(r'\s+phases=([a-z]+(?:,[a-z]+)*)\s+path="([^"\r\n]+)"\s*')
MARKER_PHASES = {'specify', 'execute', 'deliver'}
COMMENT = re.compile(r'<!--.*?-->', re.S)
HEADING = re.compile(r'^ {0,3}(#{1,6}(\s|$)|=+\s*$|-+\s*$)')  # ATX headings and setext underlines
SEVERITIES = ('blocking', 'warning', 'note')
AGENTS_WORDS = 1200
PARAGRAPH_WORDS = 25
INSTRUCTION_FILES = ('AGENTS.md', 'CLAUDE.md')
CLAUDE_FILES = ('CLAUDE.md', 'CLAUDE.local.md', '.claude/CLAUDE.md')  # Claude Code project rules, as readiness.py
INDEX_NAMES = {'agents.md', 'claude.md', 'readme.md', 'index.md'}  # always index documents, at any level
IGNORED_FOLDERS = {'.git', 'node_modules', 'vendor', '.artifacts', '.venv', '__pycache__'}  # pruned anywhere
OUTPUT_FOLDERS = {'dist', 'build', 'storage'}  # pruned outside a docs folder; docs/build is documentation
EXEMPT_OUTSIDE_DOCS = {'fixtures', 'examples'}  # test data, unless the folder sits inside a docs folder
MAX_DEPTH = 2  # AGENTS.md is level 0; only index documents add a level; level 3 or deeper is advisory


def fenced(text: str) -> list[tuple[str, bool]]:
    """(line, inside or on a code fence) for each line. A fence closes only on the same character at least as
    long, as in the phase gate hook."""
    marked, fence = [], ''
    for line in text.splitlines():
        found = FENCE.match(line)
        if fence:
            if found and found[1][0] == fence[0] and len(found[1]) >= len(fence) \
                    and not line.strip()[len(found[1]):].strip():
                fence = ''
            marked.append((line, True))
        elif found:
            fence = found[1]
            marked.append((line, True))
        else:
            marked.append((line, False))
    return marked


def outside_code(text: str) -> list[str]:
    """The text's lines with fenced code blocks and inline code blanked, so line numbers stay true."""
    return ['' if code else CODE_SPAN.sub('', line) for line, code in fenced(text)]


def code_spans(text: str) -> list[tuple[int, str]]:
    """(line, content) of each inline code span outside fenced blocks."""
    return [(number, content) for number, content, _, _ in placed_code_spans(text)]


def placed_code_spans(text: str) -> list[tuple[int, str, str, str]]:
    """(line, content, the sentence holding the span, the line's text before the span) of each inline code span
    outside fenced blocks."""
    return [(number, span[0].strip('`').strip(), sentence_at(line, span.start()), line[:span.start()])
            for number, (line, code) in enumerate(fenced(text), 1) if not code for span in CODE_SPAN.finditer(line)]


SENTENCE_END = re.compile(r'[.!?] |;')


def sentence_at(line: str, position: int) -> str:
    """The part of the line between the sentence breaks (". ", "! ", "? ", ";") around `position`."""
    start = max((m.end() for m in SENTENCE_END.finditer(line, 0, position)), default=0)
    end = SENTENCE_END.search(line, position)
    return line[start:end.start() if end else len(line)]


def prose_lines(text: str) -> list[str]:
    """Lines outside code with HTML comments blanked too (markers are read from `outside_code` instead)."""
    joined = '\n'.join(outside_code(text))
    return COMMENT.sub(lambda comment: '\n' * comment[0].count('\n'), joined).split('\n')


def inline_targets(line: str) -> list[str]:
    """Destinations of `[text](dest "title")` links on one line: `<dest with spaces>`, or a run without spaces
    whose parentheses balance, so `a_(b).md` stays whole and a `(title)` is left out."""
    found, start = [], 0
    while (start := line.find('](', start)) != -1:
        i = start + 2
        while i < len(line) and line[i] in ' \t':
            i += 1
        if line.startswith('<', i):
            end = line.find('>', i)
            if end != -1:
                found.append(line[i + 1:end])
                start = end
            else:
                start = i
            continue
        depth, end = 0, i
        while end < len(line) and line[end] not in ' \t':
            if line[end] == '(':
                depth += 1
            elif line[end] == ')':
                if depth == 0:
                    break
                depth -= 1
            end += 1
        if end > i:
            found.append(line[i:end])
        start = end
    return found


def links(text: str) -> list[Link]:
    """Relative links in Markdown prose: inline links and reference definitions. External URLs and #anchors are
    skipped; bare `<path>` text is not a link (CommonMark autolinks are URIs only)."""
    found = []
    for number, line in enumerate(prose_lines(text), 1):
        targets = inline_targets(line)
        reference = REFERENCE.match(line)
        if reference:
            targets.append(reference[2][1:-1] if reference[2].startswith('<') else reference[2])
        for target in targets:
            if target.startswith('#') or EXTERNAL.match(target):
                continue
            target = unquote(target.split('#', 1)[0])
            if target:
                found.append(Link(target, number))
    return found


def paragraphs(text: str) -> list[tuple[int, str]]:
    """(first line, normalized text) of each blank-line separated block: whitespace collapsed, case-folded."""
    found, block, start = [], [], 0
    for number, line in enumerate(text.splitlines() + [''], 1):
        if line.strip():
            start = start or number
            block.append(line)
        elif block:
            found.append((start, ' '.join(' '.join(block).split()).casefold()))
            block, start = [], 0
    return found


def repeated_paragraphs(paths: list[Path], min_words: int = PARAGRAPH_WORDS) -> list[Repeat]:
    """Paragraphs of at least `min_words` words that appear in two or more of the files.

    Unreadable or non-UTF-8 files are skipped; the caller reports them if it needs to.
    """
    seen: dict[str, list[tuple[Path, int]]] = {}
    for path in paths:
        try:
            text = path.read_text(encoding='utf-8-sig')
        except (OSError, UnicodeDecodeError):
            continue
        for line, paragraph in paragraphs(text):
            if len(paragraph.split()) >= min_words:
                places = seen.setdefault(paragraph, [])
                if all(place[0] != path for place in places):
                    places.append((path, line))
    return [Repeat(text, tuple(places)) for text, places in seen.items() if len(places) > 1]


def literal(path: str) -> bool:
    """A literal root-relative path as the hook accepts it: no globs, URLs, absolute, backslash or dot parts."""
    return bool(path) and path == path.strip() and '\\' not in path and not re.search(r'[*?\[\]{}]', path) \
        and not re.match(r'^[A-Za-z][\w+.-]*:', path) and not path.startswith(('/', '~')) \
        and all(part not in ('', '.', '..') for part in path.split('/'))


def lexical(source: str, target: str) -> str:
    """A link target as a root-relative path, without touching the disk (for comparing missing paths)."""
    base = '' if target.startswith('/') else posixpath.dirname(source)
    return posixpath.normpath(posixpath.join(base, target.lstrip('/')))


def rel(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()



class Scan:
    """The documents reached from the entry files, the links between them and the findings so far.

    `edges` maps each reached document to the documents it links, so a later mode (changed files to related
    documents) can reuse the same graph.
    """

    def __init__(self, root: Path):
        self.root = root
        self.findings: list[Finding] = []
        self.texts: dict[str, str | None] = {}
        self.depth: dict[str, int] = {}
        self.edges: dict[str, list[tuple[str, int]]] = {}
        self.targets: dict[str, list[tuple[str, int]]] = {}  # every link: (root-relative path, line), even broken
        self.required: set[str] = set()
        self.hints: list[Hint] = []
        self.versions: dict[str, dict | str] = {}  # version_facts.py results per folder
        self.by_name: dict[str, list[str]] | None = None  # every repository path by its last name, built on use
        self.listings: dict[Path, dict[str, str] | None] = {}
        self.index_cache: dict[str, bool] = {}
        self.ignore: tuple[set[str], set[str]] | None = None  # ignored_folders(), read on first use
        self.copies: set[str] = set()  # CLAUDE.md files that are a full copy of the AGENTS.md beside them
        self.packages: dict[str, set[str]] = {}  # each skill's SKILL.md -> the Markdown it reaches
        # The file a session starts from: AGENTS.md, or CLAUDE.md when the repository has no AGENTS.md.
        self.entry = 'CLAUDE.md' if not (root / 'AGENTS.md').is_file() and (root / 'CLAUDE.md').is_file() \
            else 'AGENTS.md'

    def listing(self, folder: Path) -> dict[str, str] | None:
        """{name or case-folded name: name on disk} for one folder, read once; None when it is not a folder."""
        if folder not in self.listings:
            try:
                names = os.listdir(folder)
            except OSError:
                self.listings[folder] = None
            else:
                table = {name.casefold(): name for name in names}
                table.update({name: name for name in names})
                self.listings[folder] = table
        return self.listings[folder]

    def locate(self, source: str, target: str) -> tuple[str | None, bool]:
        """(root-relative path on disk, needs a case or slash fix) for a link written in `source`.

        The path is None when nothing exists there, or the link leaves the root. Each part is matched against
        the folder listing, so a link that only works on a case-insensitive file system (or only with Windows
        backslashes) is found even on Windows, where the file system would accept it silently.
        """
        backslash = '\\' in target
        path = lexical(source, target.replace('\\', '/'))
        if path == '..' or path.startswith('../'):
            return None, backslash
        folder, parts, case = self.root, [], False
        for part in ([] if path == '.' else path.split('/')):
            table = self.listing(folder)
            name = table and (table.get(part) or table.get(part.casefold()))
            if not name:
                return None, backslash
            case = case or name != part
            parts.append(name)
            folder = folder / name
        try:
            if not folder.resolve().is_relative_to(self.root):  # a symlink leading out of the root
                return None, backslash
        except OSError:
            return None, backslash
        return '/'.join(parts) or '.', case or backslash

    def ignored(self, path: str) -> bool:
        """A root-relative path inside a folder the walk prunes: the fixed list, or a plain .gitignore folder name."""
        if self.ignore is None:
            self.ignore = ignored_folders(self.root)
        anywhere, at_root = self.ignore
        parts = path.rstrip('/').split('/')
        # The folders on the path: every part but the last, and the last too when the path names a folder (`out/`).
        folders = parts if path.endswith('/') else parts[:-1]
        return any(folder in anywhere for folder in folders) or bool(folders and folders[0] in at_root)

    def ending_with(self, claim: str) -> list[str]:
        """Real files and folders whose path ends with `claim` on whole segments, exact letter case. The repository
        is listed once, on first use, with the same pruned folders as the document walk."""
        if self.by_name is None:
            self.by_name = {}
            for path in repository_paths(self.root):
                path = path.rstrip('/')
                self.by_name.setdefault(posixpath.basename(path), []).append(path)
        return [path for path in self.by_name.get(posixpath.basename(claim), [])
                if path == claim or path.endswith('/' + claim)]

    def markers(self, entries: list[str]) -> None:
        """Collect required-read paths, parsed as the phase gate hook does: a declaration starts its own line.
        A malformed one is a note; a well-formed one naming no existing file blocks."""
        for name in entries:
            text = self.read(name) if (self.root / name).is_file() else None
            lines = outside_code(text or '')
            joined = '\n'.join(lines)
            for start in MARKER_START.finditer(joined):
                number = joined.count('\n', 0, start.start()) + 1
                whole = MARKER.match(joined, start.start() + start[0].index('<!--'))
                body = whole and MARKER_BODY.fullmatch(whole[1])
                path = body[2] if body else ''
                if not body or any(p not in MARKER_PHASES for p in body[1].split(',')) or not literal(path):
                    shown = ' '.join((whole[0] if whole else lines[number - 1]).split())[:120]
                    self.add('malformed-marker', 'note', name, number,
                             f'the hook rejects this required-read marker: {shown}')
                    continue
                found = self.locate('', path)[0]
                if found is not None and not (self.root / found).is_file():
                    self.add('malformed-marker', 'note', name, number,
                             f'the hook rejects this required-read marker: {path} is a folder, not a file')
                    continue
                self.required.add(path)
                if found is None:
                    self.add('broken-link', 'blocking', name, number,
                             f'required-read marker names {path}, which does not exist in the repository')

    def add(self, code: str, severity: str, path: str, line: int, message: str) -> None:
        self.findings.append(Finding(code, severity, path, line, message))

    def read(self, name: str) -> str | None:
        """The file's text, or None (noted once) when it cannot be read as UTF-8."""
        if name not in self.texts:
            try:
                self.texts[name] = (self.root / name).read_text(encoding='utf-8-sig')
            except (OSError, UnicodeDecodeError) as error:
                self.texts[name] = None
                self.add('unreadable-file', 'note', name, 0, f'skipped, not readable as UTF-8: {error}')
        return self.texts[name]

    def walk(self, entries: list[str]) -> None:
        """Follow links from the entry files to every reachable document, then set each document's level."""
        queue = [name for name in entries if (self.root / name).is_file()]
        for name in queue:
            self.depth.setdefault(name, 0)
        while queue:
            name = queue.pop()
            text = self.read(name)
            if text is None:
                continue
            self.edges[name] = []
            self.targets[name] = []
            for link in links(text):
                child, fix = self.locate(name, link.target)
                self.targets[name].append((child or lexical(name, link.target.replace('\\', '/')), link.line))
                if child is None:
                    # A missing required-read file is already reported (blocking) at its marker.
                    # Preserved history (plans, archive) keeps its old links: a note, not drift.
                    if lexical(name, link.target.replace('\\', '/')) not in self.required:
                        self.add('broken-link', 'note' if historical_document(name) else 'warning', name, link.line,
                                 f'link to {link.target} does not resolve to a file or folder in the repository')
                    continue
                if fix:
                    self.add('link-case', 'warning', name, link.line,
                             f'link to {link.target} works only with case-insensitive names or backslashes; '
                             f'write {posixpath.relpath(child, posixpath.dirname(name) or ".")}')
                if child.lower().endswith('.md') and (self.root / child).is_file():
                    self.edges[name].append((child, link.line))
                    if child not in self.depth:
                        self.depth[child] = -1  # reached; the level is set below
                        queue.append(child)
        self.levels()

    def levels(self) -> None:
        """Shortest path from an entry where only a step out of an index document adds a level (0-1 breadth-first),
        so a chain of plain documents linking each other stays at its index's level."""
        best = {name: 0 for name, depth in self.depth.items() if depth == 0}
        queue = deque(best)
        while queue:
            name = queue.popleft()
            step = 1 if self.is_index(name) else 0
            for child, _ in self.edges.get(name, []):
                if best[name] + step < best.get(child, 1 << 30):
                    best[child] = best[name] + step
                    (queue.append if step else queue.appendleft)(child)
        self.depth.update(best)

    def is_index(self, name: str) -> bool:
        """An AGENTS.md, CLAUDE.md, README.md or index.md, or a document that is mostly a list of links: it links at
        least two different .md documents, and at least half of its non-empty lines (headings, code and comments
        aside) contain a .md link. Topical documents that cite each other, and one-link notes, are not."""
        if name not in self.index_cache:
            text = self.texts.get(name) or ''
            filled = sum(1 for line in prose_lines(text) if line.strip() and not HEADING.match(line))
            linked = {link.line for link in links(text) if link.target.lower().endswith('.md')}
            documents = {child for child, _ in self.edges.get(name, []) if child != name}
            self.index_cache[name] = posixpath.basename(name).lower() in INDEX_NAMES \
                or (len(documents) >= 2 and filled > 0 and 2 * len(linked) >= filled)
        return self.index_cache[name]

    def cycles(self) -> None:
        """Iterative depth-first search over index documents only. A link to a document still on the current
        path closes a cycle. Links to the root entry files ("back to AGENTS.md") and self-links are ignored."""
        entries = {name for name, depth in self.depth.items() if depth == 0}
        indexes = {name for name in self.edges if self.is_index(name) and not exempt(name)}

        def children(name: str) -> list[tuple[str, int]]:
            return [(child, line) for child, line in self.edges.get(name, [])
                    if child in indexes and child not in entries and child != name]

        done: set[str] = set()
        # Entries first, then indexes reached only through plain documents.
        for start in sorted(entries & indexes) + sorted(indexes - entries):
            if start in done:
                continue
            path, stack = [start], [iter(children(start))]
            while stack:
                step = next(stack[-1], None)
                if step is None:
                    done.add(path.pop())
                    stack.pop()
                    continue
                child, line = step
                if child in path:
                    loop = ' -> '.join(path[path.index(child):] + [child])
                    self.add('index-cycle', 'note', path[-1], line, f'link returns to {child}: {loop}')
                elif child not in done:
                    path.append(child)
                    stack.append(iter(children(child)))


def ignored_folders(root: Path) -> tuple[set[str], set[str]]:
    """(names ignored at any depth, names ignored only at the root): the fixed list plus top-level .gitignore
    lines that are plain folder names. Globs, negations and lines with an inner slash are left alone."""
    anywhere, at_root = set(IGNORED_FOLDERS), set()
    try:
        lines = (root / '.gitignore').read_text(encoding='utf-8-sig').splitlines()
    except (OSError, UnicodeDecodeError):
        lines = []
    for line in lines:
        name = line.strip()
        anchored = name.startswith('/')
        name = name.strip('/')
        if name and not line.lstrip().startswith(('#', '!')) and re.fullmatch(r'[\w.-]+', name):
            (at_root if anchored else anywhere).add(name)
    return anywhere, at_root


def repository_paths(root: Path, keep=lambda name: True) -> list[str]:
    """Root-relative paths of the files (and, with folders, `name/`) under the root whose name `keep` accepts,
    sorted. Ignored folders are pruned by name before anything inside them is read; symlinked folders are not
    entered, and a symlinked file is kept only when it stays inside the root."""
    anywhere, at_root = ignored_folders(root)
    found, folders = [], [(root, '')]
    while folders:
        folder, prefix = folders.pop()
        try:
            entries = list(os.scandir(folder))
        except OSError:
            continue
        for entry in entries:
            try:
                if entry.is_dir(follow_symlinks=False):
                    output = entry.name in OUTPUT_FOLDERS and 'docs' not in prefix.split('/')
                    if entry.name not in anywhere and not output and not (prefix == '' and entry.name in at_root) \
                            and not nested_repository(Path(entry.path)):
                        folders.append((Path(entry.path), f'{prefix}{entry.name}/'))
                        if keep(entry.name + '/'):
                            found.append(f'{prefix}{entry.name}/')
                elif keep(entry.name) and (not entry.is_symlink() or inside(root, entry.path)):
                    found.append(prefix + entry.name)
            except OSError:
                continue
    return sorted(found)


def nested_repository(folder: Path) -> bool:
    """A folder below the root with its own .git (a folder for a clone, a file for a worktree or submodule):
    another repository, so it is not walked."""
    return os.path.lexists(folder / '.git')


def markdown_files(root: Path) -> list[str]:
    return repository_paths(root, lambda name: name.lower().endswith('.md'))


def inside(root: Path, path: str) -> bool:
    """False for a symlink that leads out of the root, so its target is never read."""
    try:
        return Path(path).resolve().is_relative_to(root)
    except OSError:
        return False


def imports(scan: Scan, files: list[str]) -> None:
    """The root CLAUDE.md, and each CLAUDE.md beside a nested AGENTS.md, is the one line @AGENTS.md. An AGENTS.md
    without a CLAUDE.md beside it is invisible to Claude Code: a warning at the root, a note below it."""
    present = set(files)
    for name in files:
        if posixpath.basename(name) == 'AGENTS.md' and not exempt(name):
            folder = posixpath.dirname(name)
            claude = posixpath.join(folder, 'CLAUDE.md')
            # The names readiness.py also accepts as Claude Code project rules.
            if any((scan.root / folder / other).is_file() for other in CLAUDE_FILES):
                continue
            loads = f'no rules for {folder}' if folder else 'no project rules'
            scan.add('no-claude', 'note' if folder else 'warning', claude, 0,
                     f'If this repository is used with Claude Code, add {claude} with the one line @AGENTS.md '
                     f'(Claude Code loads {loads} now)')
    for name in files:
        sibling = posixpath.join(posixpath.dirname(name), 'AGENTS.md')
        if posixpath.basename(name) != 'CLAUDE.md' or (name != 'CLAUDE.md' and sibling not in present) \
                or exempt(name):
            continue
        text = scan.read(name)
        if text is None:
            continue
        lines = [line.strip() for line in COMMENT.sub('', text).splitlines() if line.strip()]
        agents = scan.read(sibling) if sibling in present else None
        if agents is not None and ' '.join(text.split()).casefold() == ' '.join(agents.split()).casefold():
            scan.copies.add(name)  # one finding for a full copy; repeats() adds no second one
            scan.add('claude-duplicates-agents', 'warning', name, 1,
                     f'{name} is a full copy of {sibling}; replace it with the one line @AGENTS.md')
        elif lines != ['@AGENTS.md']:
            scan.add('claude-not-import', 'warning', name, 1,
                     'CLAUDE.md is not the one line @AGENTS.md (blank lines and HTML comments aside)')


def history_rule(name: str) -> str | None:
    """Why a document is preserved history, or None: the root CHANGELOG.md or CHANGES.md, or inside a plans or
    archive folder at the root or anywhere under a docs folder. Such a folder elsewhere (product/plans/,
    src/archive/) is live documentation."""
    if name.upper() in ('CHANGELOG.MD', 'CHANGES.MD'):
        return 'changelog at the root'
    folders = name.split('/')[:-1]
    for i, folder in enumerate(folders):
        if folder in ('plans', 'archive') and i == 0:
            return f'{folder} folder at the root'
        if folder in ('plans', 'archive') and 'docs' in folders[:i]:
            return f'{folder} folder under docs/'
    return None


def historical_document(name: str) -> bool:
    """Preserved history (see history_rule), not current documentation."""
    return history_rule(name) is not None


def exempt(name: str) -> bool:
    """History (see history_rule), or a document inside fixtures or examples outside a docs folder: it needs no
    index entry, level or cycle check, and its instruction files are not checked."""
    folders = name.split('/')[:-1]
    return historical_document(name) or any(folder in EXEMPT_OUTSIDE_DOCS and 'docs' not in folders[:i]
                                            for i, folder in enumerate(folders))


ROOT_DOCUMENTS = re.compile(r'(README|CHANGELOG)\.md|(LICENSE|CONTRIBUTING|CODE_OF_CONDUCT|SECURITY)[^/]*', re.I)


def code_readme(scan: Scan, name: str) -> bool:
    """A README.md outside any docs folder whose folder also holds a non-Markdown file: it describes that code
    and is found by its location, so it needs no index entry. A README among documents still does."""
    folders = name.split('/')[:-1]
    if posixpath.basename(name) != 'README.md' or not folders or 'docs' in folders:
        return False
    folder = scan.root.joinpath(*folders)
    return any(not entry.lower().endswith('.md') and (folder / entry).is_file()
               for entry in set((scan.listing(folder) or {}).values()))


def unreachable(scan: Scan, files: list[str]) -> None:
    """Markdown files anywhere that no reached document links to and no required-read marker names. Exempt:
    history, fixtures and examples (see exempt), the conventional root files a host shows on its own (README,
    CHANGELOG, LICENSE, CONTRIBUTING, CODE_OF_CONDUCT, SECURITY), CLAUDE.md files (loaded by location), a README.md
    beside code (see code_readme) and folders whose name starts with a dot (tool state). A skill package (the
    nearest folder above with its own SKILL.md) is reached through that SKILL.md instead of the project index: its
    Markdown is noted when the package's SKILL.md does not reach it. Ignored folders and nested repositories are
    never listed."""
    for name in files:
        folders = name.split('/')[:-1]
        if exempt(name) or name in scan.depth or name in scan.required or posixpath.basename(name) == 'CLAUDE.md' \
                or code_readme(scan, name) \
                or ('/' not in name and ROOT_DOCUMENTS.fullmatch(name)) \
                or any(folder.startswith('.') for folder in folders):
            continue
        package = next(('/'.join(folders[:end]) for end in range(len(folders), 0, -1)
                        if (scan.root.joinpath(*folders[:end]) / 'SKILL.md').is_file()), None)
        start = f'{package}/SKILL.md' if package else scan.entry
        if package and name in package_reach(scan, start):
            continue
        scan.add('unreachable-doc', 'note', name, 0, f'no document reached from {start} links to it')


def package_reach(scan: Scan, skill: str) -> set[str]:
    """The Markdown files a skill's SKILL.md reaches by relative links, itself included; read once per skill."""
    if skill not in scan.packages:
        reached, queue = {skill}, [skill]
        while queue:
            name = queue.pop()
            for link in links(scan.read(name) or ''):
                child = scan.locate(name, link.target)[0]
                if child and child not in reached and child.lower().endswith('.md') and (scan.root / child).is_file():
                    reached.add(child)
                    queue.append(child)
        scan.packages[skill] = reached
    return scan.packages[skill]


def repeats(scan: Scan, instructions: list[str]) -> None:
    """Paragraphs repeated across instruction files. A CLAUDE.md copying the AGENTS.md beside it gets one warning
    per file instead of also appearing in the general note."""
    root = scan.root
    readable = [root / name for name in instructions if scan.read(name) is not None]
    copied: dict[Path, list[tuple[int, int]]] = {}  # CLAUDE.md -> [(its line, AGENTS.md line)]
    for repeat in repeated_paragraphs(readable):
        places = dict(repeat.places)
        for path in [p for p in places if p.name == 'CLAUDE.md' and p.with_name('AGENTS.md') in places]:
            copied.setdefault(path, []).append((places.pop(path), places[path.with_name('AGENTS.md')]))
        if len(places) < 2:
            continue
        (first, line), *others = places.items()
        where = ', '.join(f'{rel(root, path)}:{number}' for path, number in others)
        scan.add('repeated-paragraph', 'note', rel(root, first), line,
                 f'paragraph also in {where}: "{" ".join(repeat.text.split()[:8])} ..."')
    for path, pairs in copied.items():
        claude, agents = rel(root, path), rel(root, path.with_name('AGENTS.md'))
        if claude in scan.copies:
            continue
        pairs.sort()
        count = f'{len(pairs)} paragraph' + ('s' if len(pairs) > 1 else '')
        scan.add('claude-duplicates-agents', 'warning', claude, pairs[0][0],
                 f'{claude} duplicates {agents}: repeats {count} (first at {agents}:{pairs[0][1]}); '
                 f'{claude} should only import it')


def check(root: Path) -> Scan:
    scan = Scan(root)
    if not (root / 'AGENTS.md').is_file():
        scan.add('no-agents', 'warning', 'AGENTS.md', 0, 'no AGENTS.md at the repository root')
    entries = ['AGENTS.md', 'CLAUDE.md']
    scan.markers(entries)
    scan.walk(entries)
    scan.cycles()
    scan.hints = cover_hints(scan)
    words = len((scan.texts.get(scan.entry) or '').split())
    if words > AGENTS_WORDS:
        scan.add('agents-size', 'warning', scan.entry, 0,
                 f'{scan.entry} has {words} words; the advisory size is {AGENTS_WORDS}')
    for name, depth in scan.depth.items():
        if depth > MAX_DEPTH and not exempt(name):
            scan.add('index-depth', 'note', name, 0,
                     f'reached only at level {depth}; more than {MAX_DEPTH} index levels below {scan.entry}')
    untracked(scan)
    files = markdown_files(root)
    imports(scan, files)
    unreachable(scan, files)
    repeats(scan, [name for name in files if posixpath.basename(name) in INSTRUCTION_FILES and not exempt(name)])
    return scan


@dataclass(frozen=True)
class Hint:
    source: str  # the document holding the line
    line: int
    pattern: str  # root-relative, directory level, with * and **
    document: str  # the document the index entry links


def cover_hints(scan: Scan) -> list[Hint]:
    """`Covers: a/, b/**` on an index item's line or the line right under it; the item's linked .md document is
    the one covered (the holding document itself when the item links none). A hint matching nothing is stale."""
    hints = []
    for source, targets in sorted(scan.targets.items()):
        text = scan.texts.get(source) or ''
        documents = {line: target for target, line in targets if target.lower().endswith('.md')}
        raw = [line for line, _ in fenced(text)]
        for number, prose in enumerate(prose_lines(text), 1):
            if 'Covers:' not in prose:
                continue
            document = entry_document(raw, number, documents) or source
            for pattern in raw[number - 1].split('Covers:', 1)[1].split(','):
                pattern = pattern.strip().strip('`').strip()
                if not pattern:
                    continue
                hints.append(Hint(source, number, pattern, document))
                if not covers_anything(scan, pattern):
                    scan.add('stale-hint', 'warning', source, number, f'Covers hint {pattern} matches no path')
    return hints


LIST_ITEM = re.compile(r'^\s*(?:[-*+]|\d+[.)])\s')


def entry_document(raw: list[str], number: int, documents: dict[int, str]) -> str | None:
    """The .md document linked by the index item a Covers line belongs to: the item on the same line, or the
    nearest list item above it within the same block (no blank line or heading between). None when the line
    is not under a linking item."""
    if number in documents:
        return documents[number]
    for line in range(number - 1, 0, -1):
        text = raw[line - 1]
        if not text.strip() or HEADING.match(text):
            return None
        if LIST_ITEM.match(text):
            return documents.get(line)
    return None


def pattern_regex(pattern: str) -> re.Pattern:
    """A directory-level pattern: `*` is one name, `**` any depth; a match also covers everything below it."""
    parts = re.split(r'(\*\*/?|\*|\?)', pattern.strip('/'))
    body = ''.join({'**/': '(?:.*/)?', '**': '.*', '*': '[^/]*', '?': '[^/]'}.get(p, re.escape(p)) for p in parts)
    return re.compile(f'{body}(?:/.*)?')


def covers_anything(scan: Scan, pattern: str) -> bool:
    if not re.search(r'[*?]', pattern):
        return scan.locate('', pattern.rstrip('/'))[0] is not None
    try:
        return next(iter(scan.root.glob(pattern.strip('/'))), None) is not None
    except (OSError, ValueError):
        return False


def run_git(root: Path, command: list[str]) -> subprocess.CompletedProcess:
    """A read-only git command in the root: no stdin, no fsmonitor, no optional index locks."""
    env = dict(os.environ, GIT_OPTIONAL_LOCKS='0')  # never refresh the index while reading
    return subprocess.run(['git', '-c', 'core.quotepath=off', '-c', 'core.fsmonitor=false', '-C', str(root),
                           *command], stdin=subprocess.DEVNULL, capture_output=True, text=True, encoding='utf-8',
                          errors='replace', env=env, timeout=60)


def untracked(scan: Scan) -> None:
    """A note for each entry file, reached document or required-read file that Git does not track (untracked or
    ignored): a fresh clone will not have it. Silent when Git or a repository is unavailable."""
    names = sorted(set(scan.depth) | {path for path in scan.required if (scan.root / path).is_file()})
    if not names:
        return
    tracked: set[str] = set()
    for start in range(0, len(names), 200):  # batches keep the command line short on Windows
        try:
            result = run_git(scan.root, ['ls-files', '--cached', '--', *names[start:start + 200]])
        except (OSError, subprocess.TimeoutExpired):
            return
        if result.returncode:
            return
        tracked.update(result.stdout.splitlines())
    for name in names:
        if name not in tracked:
            scan.add('untracked-doc', 'note', name, 0, 'untracked: a fresh clone will not have it')


def git_changes(scan: Scan) -> list[str]:
    """Changed files from Git, read-only: tracked changes against HEAD plus untracked files, relative to the root.
    Deleted paths (and the old side of a rename) are left out, as is anything inside a nested repository. Without
    Git or a repository, a note and an empty list."""
    commands = (['diff', '--name-only', '--no-renames', '--diff-filter=d', '--relative', 'HEAD'],
                ['ls-files', '--others', '--exclude-standard'])
    found: list[str] = []
    for command in commands:
        try:
            result = run_git(scan.root, command)
        except (OSError, subprocess.TimeoutExpired) as error:
            scan.add('git-unavailable', 'note', '.', 0, f'could not run git ({error}); no changed files listed')
            return []
        if result.returncode:
            reason = (result.stderr.strip().splitlines() or ['no output'])[0]
            scan.add('git-unavailable', 'note', '.', 0, f'git {command[0]} failed: {reason}; no changed files listed')
            return []
        found += [line for line in result.stdout.splitlines() if line.strip()]
    return sorted(path for path in set(found) if not in_nested_repository(scan.root, path))


def in_nested_repository(root: Path, path: str) -> bool:
    """The path is, or sits inside, a folder below the root that has its own .git."""
    parts = path.rstrip('/').split('/')
    return any(nested_repository(root.joinpath(*parts[:end])) for end in range(1, len(parts) + 1)
               if end < len(parts) or path.endswith('/'))


def changed_path(root: Path, value: str) -> str:
    """A changed file as a root-relative forward-slash path (absolute paths under the root are accepted)."""
    path = Path(value)
    if path.is_absolute():
        try:
            value = path.resolve().relative_to(root).as_posix()
        except ValueError:
            return value.replace('\\', '/')
    return posixpath.normpath(value.replace('\\', '/'))


def related(scan: Scan, changed: list[str]) -> list[dict]:
    """[{changed, document, reason}]: which documents relate to each changed file, and why. One entry per pair;
    several reasons are joined."""
    found: dict[tuple[str, str], list[str]] = {}

    def relate(path: str, document: str, reason: str) -> None:
        reasons = found.setdefault((path, document), [])
        if reason not in reasons:
            reasons.append(reason)

    for path in changed:
        if path.lower().endswith('.md') and (scan.root / path).is_file():
            relate(path, path, 'changed document')  # its own facts are checked too
        for document, targets in scan.targets.items():
            for target, _ in targets:
                if target == path:
                    relate(path, document, 'links to the path')
                elif path.startswith(target.rstrip('/') + '/') and target != '.':
                    relate(path, document, f'links to its folder {target.rstrip("/")}')
            for _, span in code_spans(scan.texts.get(document) or ''):
                if posixpath.normpath(span.removeprefix('./')) == path:
                    relate(path, document, 'names the path')
        for hint in scan.hints:
            if pattern_regex(hint.pattern).fullmatch(path):
                relate(path, hint.document, f'Covers hint {hint.pattern} in {hint.source}:{hint.line}')
        for document, folder in nearest_documents(scan, path):
            relate(path, document, f'in a folder that contains it ({folder})')
        # Every task relies on the root rules and commands; named once when nothing else relates them.
        if scan.entry in scan.targets and (path, scan.entry) not in found:
            relate(path, scan.entry, 'entry point')
    return [{'changed': path, 'document': document, 'reason': '; '.join(reasons)}
            for (path, document), reasons in sorted(found.items())]


def nearest_documents(scan: Scan, path: str) -> list[tuple[str, str]]:
    """The README.md and the top-level .md files of docs/ in the nearest folder above `path` that has either.
    The repository root is left out: its documents would relate to every change."""
    folder = posixpath.dirname(path)
    while folder not in ('', '.'):
        table = scan.listing(scan.root / folder) or {}
        found = [f'{folder}/README.md'] if table.get('README.md') == 'README.md' else []
        if table.get('docs') == 'docs' and (scan.root / folder / 'docs').is_dir():
            docs = scan.listing(scan.root / folder / 'docs') or {}
            found += sorted(f'{folder}/docs/{name}' for name in set(docs.values())
                            if name.lower().endswith('.md') and (scan.root / folder / 'docs' / name).is_file())
        if found:
            return [(document, folder) for document in found]
        folder = posixpath.dirname(folder)
    return []


FILE_TYPES = {'md', 'json', 'ts', 'tsx', 'js', 'jsx', 'mjs', 'cjs', 'py', 'php', 'html', 'scss', 'css', 'yml',
              'yaml', 'toml', 'lock', 'txt', 'sh', 'env', 'xml', 'vue', 'svelte', 'rs', 'go', 'java', 'kt', 'swift',
              'cs', 'sql', 'ini', 'cfg', 'conf'}
PATHLIKE = re.compile(r'[\w.-]+(?:/[\w.-]+)*/?')


# A file that does not exist yet. Bare "will" or "later" ("run `x` later") is an instruction, not a plan.
PLANNED = re.compile(r'\b(planned|will (?:be )?(?:add(?:ed)?|creat(?:e|ed)|writ(?:e|ten))'
                     r'|to be (?:added|created|written)|(?:added|comes) later)\b', re.I)
# Phrases that say the file is absent. A bare "never" is an instruction ("never run `x`"), not an absence.
ABSENT = re.compile(r'\b(does not exist|doesn\'t exist|no longer (?:exists?|ships?|used)|was removed|were removed'
                    r'|never existed|is gone)\b', re.I)
# A template rather than a real path: `...`, `<name>`, a glob, or a date pattern.
PLACEHOLDER = re.compile(r'\.\.\.|<[^<>\s]*>|\*|(?<![A-Za-z])(?:YYYY|MM|DD)(?![A-Za-z])')
# Text ending in an external link, then optionally "at": "from [upstream](https://...) `skills/x/SKILL.md`".
AFTER_LINK = re.compile(r'\]\(\s*<?[A-Za-z][\w+.-]*://[^)\s>]*>?(?:\s+"[^"]*")?\s*\)\s*(?:at\s+)?$', re.I)
FOREIGN ='first folder not found here; may belong to another repository or not be a path'


def path_fact(scan: Scan, document: str, line: int, span: str, sentence: str = '', before: str = '') -> dict | None:
    """A backticked path, in this order:
    - matched: it exists with exact letter case from the root or the document's folder, or exactly one real file
      or folder ends with it on whole segments (a shortened path); the evidence names the real path;
    - not-checkable: several real paths end with it;
    - contradicted: a path with a folder part exists only with other letter case, or it is clearly a path of this
      repository (starts with ./ or ../, or its first folder exists at the root or beside the document) and is
      missing;
    - not-checkable otherwise: a placeholder (`...`, `<name>`, a glob, YYYY-MM-DD), a missing path under a
      git-ignored folder (generated output), a missing path right after an external link (another
      repository's path), a missing path its sentence calls planned or absent (removed, no
      longer, never), another repository's path, a git ref, or a bare name found nowhere or only in other case.
    Spans with a space, a scheme, `@` or a leading / are not paths and are skipped."""
    claim = span
    if '/' in claim and PLACEHOLDER.search(claim) and not re.search(r'\s|^/|^[A-Za-z][\w+.-]*:', claim):
        return {'document': document, 'line': line, 'kind': 'path', 'claim': claim, 'status': 'not-checkable',
                'evidence': 'placeholder path'}
    planned, absent = bool(PLANNED.search(sentence)), bool(ABSENT.search(sentence))
    relative = claim.startswith(('./', '../'))
    if not PATHLIKE.fullmatch(claim) or '..' in claim.lstrip('./').split('/'):
        return None
    bare = '/' not in claim.rstrip('/')
    if bare and claim.rsplit('.', 1)[-1].lower() not in FILE_TYPES:
        return None
    fact = {'document': document, 'line': line, 'kind': 'path', 'claim': claim}
    target = claim.rstrip('/')
    escaped = lexical(document, target)
    if relative and (escaped == '..' or escaped.startswith('../')):
        return fact | {'status': 'not-checkable', 'evidence': 'leaves this repository'}
    sources = (document,) if relative else ('', document)
    located = [scan.locate(source, target) for source in sources]
    for found, fix in located:
        if found and not fix:
            return fact | {'status': 'matched', 'evidence': f'{found} exists'}
    # A bare name in other letter case is often another repository's file (a shared `DESIGN.md`), not a typo.
    other_case = next((found for found, fix in located if found), None)
    if other_case and not bare:
        return fact | {'status': 'contradicted', 'evidence': f'only {other_case} exists (letter case differs)'}
    if not relative:
        ends = scan.ending_with(target.removeprefix('./'))
        if len(ends) == 1:
            return fact | {'status': 'matched', 'evidence': f'found as {ends[0]}'}
        if ends:
            return fact | {'status': 'not-checkable', 'evidence': f'{len(ends)} files or folders end with this path'}
    if not bare and scan.ignored(escaped if relative else target):
        return fact | {'status': 'not-checkable', 'evidence': 'under a git-ignored folder (generated output)'}
    if AFTER_LINK.search(before):
        return fact | {'status': 'not-checkable',
                       'evidence': 'follows an external link; may name another repository\'s path'}
    first = target.split('/')[0]
    here = any((scan.listing(scan.root / folder) or {}).get(first) == first
               for folder in ('', posixpath.dirname(document)))
    if (relative or (not bare and here)) and planned:
        return fact | {'status': 'not-checkable', 'evidence': 'described as planned'}
    if (relative or (not bare and here)) and absent:
        return fact | {'status': 'not-checkable', 'evidence': 'described as absent'}
    if relative or (not bare and here):
        return fact | {'status': 'contradicted', 'evidence': 'no such file or folder from the root or the document, '
                                                             'and no file ends with it'}
    if bare and other_case:
        return fact | {'status': 'not-checkable', 'evidence': f'bare file name; only {other_case} exists (letter case '
                                                              'differs), so it may name another repository\'s file'}
    if bare:
        return fact | {'status': 'not-checkable', 'evidence': 'bare file name found nowhere in the repository'}
    return fact | {'status': 'not-checkable', 'evidence': FOREIGN}


# `npm test|start|stop|restart` are npm's shortcuts for the scripts of the same name.
COMMAND = re.compile(r'(?<![\w-])(npm run|npm(?=\s+(?:test|start|stop|restart)\b)|pnpm run|pnpm|yarn run|yarn|composer run-script|composer run|composer|make'
                     r'|php artisan|python3? -m)(?=\s)')
# What npm runs for these shortcuts when package.json has no script of that name.
NPM_DEFAULTS = {'start': 'npm start runs node server.js if it exists', 'restart': 'npm restart runs stop, then start'}
SEPARATOR = re.compile(r'&&|\|\||[;|]')
FROM_DIR = re.compile(r'\bfrom\s+`(?:\./)?([\w.-]+(?:/[\w.-]+)*)/`')  # "from `web/`": a folder, so a slash
VALUE_OPTIONS = {'--filter', '-F', '-C', '--prefix', '--dir', '-d', '-w', '--workspace'}  # take the next token
ELSEWHERE = {'--filter', '-F', '--prefix', '-C', '--dir', '-w', '--workspace', '-r', '--recursive'}
BUILT_IN = {
    'pnpm': {'install', 'i', 'add', 'remove', 'rm', 'update', 'up', 'exec', 'dlx', 'create', 'init', 'publish',
             'link', 'unlink', 'audit', 'outdated', 'list', 'ls', 'store', 'why', 'prune', 'fetch', 'rebuild',
             'import', 'patch', 'setup', 'env', 'deploy', 'pack', 'config', 'run'},
    'yarn': {'install', 'add', 'remove', 'upgrade', 'up', 'init', 'dlx', 'exec', 'why', 'info', 'link', 'unlink',
             'workspace', 'workspaces', 'set', 'config', 'cache', 'global', 'create', 'pack', 'publish', 'version',
             'node', 'plugin', 'run'},
    # Composer built-ins with their documented aliases.
    'composer': {'install', 'i', 'update', 'u', 'upgrade', 'require', 'r', 'req', 'remove', 'rm', 'rem', 'uninstall',
                 'dump-autoload', 'dumpautoload', 'du', 'show', 'info', 'outdated', 'validate', 'create-project',
                 'init', 'config', 'global', 'exec', 'diagnose', 'self-update', 'selfupdate', 'audit', 'why',
                 'depends', 'why-not', 'prohibits', 'licenses', 'license', 'status', 'archive', 'search', 'fund',
                 'bump', 'reinstall', 'check-platform-reqs', 'clear-cache', 'clearcache', 'cc', 'list', 'help',
                 'browse', 'home', 'suggests', 'run-script', 'run'},
}


def command_tokens(code: str, start: int) -> tuple[list[str], str | None, bool]:
    """(options read, the script or target name or None, runs in another package) for the words after a tool,
    up to the next shell separator. Options are skipped, with the value of those that take one."""
    words = SEPARATOR.split(code[start:], 1)[0].split()
    options, elsewhere, i = [], False, 0
    while i < len(words) and words[i].startswith('-'):
        option = words[i].split('=', 1)[0]
        options.append(words[i])
        elsewhere = elsewhere or option in ELSEWHERE
        if option in VALUE_OPTIONS and '=' not in words[i] and i + 1 < len(words):
            options.append(words[i + 1])
            i += 1
        i += 1
    name = words[i] if i < len(words) and re.fullmatch(r'[\w:.@/-]+', words[i]) else None
    # A folder or workspace flag after the name (`npm run dev --prefix apps/web`) also moves the command.
    elsewhere = elsewhere or any(word.split('=', 1)[0] in ELSEWHERE for word in words[i + 1:])
    return options, name, elsewhere


def code_lines(text: str) -> list[tuple[int, str]]:
    """(line, code) for fenced code lines and inline code spans; HTML comments are blanked first."""
    text = COMMENT.sub(lambda comment: '\n' * comment[0].count('\n'), text)
    found = []
    for number, (line, code) in enumerate(fenced(text), 1):
        if code and not FENCE.match(line):
            found.append((number, line))
        elif not code:
            found += [(number, span[0].strip('`')) for span in CODE_SPAN.finditer(line)]
    return found


def nearest_file(scan: Scan, document: str, names: tuple[str, ...]) -> str | None:
    """The first of `names` in the document's folder or a folder above it, up to the root."""
    folder = posixpath.dirname(document)
    while True:
        table = scan.listing(scan.root / folder) or {}
        for name in names:
            if table.get(name) == name and (scan.root / folder / name).is_file():
                return posixpath.join(folder, name) if folder else name
        if folder in ('', '.'):
            return None
        folder = posixpath.dirname(folder)


def manifest_for(scan: Scan, document: str, names: tuple[str, ...]) -> str | None:
    """nearest_file, or else the file in the only direct subfolder of the root that has one (a monorepo whose
    app lives in `web/`). Ignored folders and nested repositories do not count."""
    found = nearest_file(scan, document, names)
    if found:
        return found
    holders = []
    for folder in sorted(set((scan.listing(scan.root) or {}).values())):
        path = scan.root / folder
        if not path.is_dir() or scan.ignored(folder + '/') or nested_repository(path):
            continue
        present = [name for name in names if (path / name).is_file()]
        if present:
            holders.append(f'{folder}/{present[0]}')
    return holders[0] if len(holders) == 1 else None


def scripts(scan: Scan, manifest: str) -> dict | None:
    try:
        data = json.loads((scan.root / manifest).read_text(encoding='utf-8-sig'))
    except (OSError, UnicodeDecodeError, ValueError):
        return None
    value = data.get('scripts') if isinstance(data, dict) else None
    return value if isinstance(value, dict) else {}


def make_targets(text: str) -> set[str]:
    """Targets of the rule lines (`a b c: deps` or `a::`), skipping recipe lines (tab-indented) and variable
    assignments (`X := ...`, `X ?= ...`, `X = ...`)."""
    targets = set()
    for line in text.splitlines():
        if line.startswith('\t') or line.lstrip().startswith('#'):
            continue
        rule = re.match(r'^([^:=#]+?)\s*::?(?![=])', line)
        if rule and not re.match(r'^[^:]*(?:::?|[?+!])?=', line):
            targets.update(rule[1].split())
    return targets


def command_fact(scan: Scan, document: str, line: int, tool: str, options: list[str], name: str | None,
                 elsewhere: bool, base: str | None = None) -> dict | None:
    """A named command checked against the nearest manifest (see manifest_for): package.json scripts,
    composer.json scripts or Makefile targets. `base` is a folder the document says the command runs from
    ("from `web/`"); otherwise the document's folder. artisan and python -m commands are matched only when
    trivially found. A workspace or folder option means it runs in another package; `pnpm X` / `yarn X` may run a
    local binary."""
    program = tool.split()[0]
    where = base + '/' if base else document
    claim = ' '.join([tool, *options] + ([name] if name else []))
    fact = {'document': document, 'line': line, 'kind': 'command', 'claim': claim}

    def status(state: str, evidence: str) -> dict:
        return fact | {'status': state, 'evidence': evidence}

    if tool in ('composer run', 'composer run-script') and {'-l', '--list'} & set(options):
        return status('not-checkable', 'lists the scripts; not a script name')
    if elsewhere:
        return status('not-checkable', 'runs in another package')
    if name is None:
        return None
    if program in ('npm', 'pnpm', 'yarn', 'composer'):
        manifest = manifest_for(scan, where, ('composer.json',) if program == 'composer' else ('package.json',))
        listed = scripts(scan, manifest) if manifest else None
        if listed is None:
            return status('not-checkable', f'no readable {"composer.json" if program == "composer" else "package.json"}'
                                           ' at the document\'s folder or above')
        if name in listed:
            return status('matched', f'script {name} in {manifest}')
        if tool == program and name in BUILT_IN.get(program, ()):
            return status('not-checkable', f'{program} {name} is a built-in command')
        if tool in ('pnpm', 'yarn'):
            return status('not-checkable', f'no script {name} in {manifest}; may be a local binary')
        if tool == 'npm' and name in NPM_DEFAULTS:
            return status('not-checkable', f'no script {name} in {manifest}; {NPM_DEFAULTS[name]}')
        return status('contradicted', f'no script {name} in {manifest}')
    if program == 'make':
        makefile = manifest_for(scan, where, ('Makefile', 'makefile', 'GNUmakefile'))
        if not makefile:
            return status('not-checkable', 'no Makefile at the document\'s folder or above')
        if name in make_targets((scan.root / makefile).read_text(encoding='utf-8-sig', errors='replace')):
            return status('matched', f'target {name} in {makefile}')
        return status('contradicted', f'no target {name} in {makefile}')
    if program == 'php':
        signature = re.compile(rf'signature\s*=\s*[\'"]{re.escape(name)}(?=[\s\'"{{])')
        artisan = manifest_for(scan, where, ('artisan',))  # the Laravel app may live in a subfolder
        app = scan.root / (posixpath.dirname(artisan) if artisan else '') / 'app/Console/Commands'
        for path in sorted(app.rglob('*.php')):
            if signature.search(path.read_text(encoding='utf-8-sig', errors='replace')):
                return status('matched', f'signature {name} in {rel(scan.root, path)}')
        return status('not-checkable', 'not a command signature in app/Console/Commands; '
                                       'Laravel and packages add commands of their own')
    module = name.replace('.', '/')
    for candidate in (f'{module}.py', f'{module}/__main__.py', f'src/{module}.py', f'src/{module}/__main__.py'):
        if scan.locate('', candidate) == (candidate, False):
            return status('matched', f'{candidate} exists')
    return status('not-checkable', 'not a module in this repository; it may be installed or in the standard library')


# "Next 16.3" is the shorthand for Next.js; a bare "Next" needs a dotted version so "Next 3 steps" is no claim.
VERSION_CLAIM = re.compile(r'\b(Angular|React|TypeScript|Vite|Ionic|Capacitor|Laravel|PHP|Node(?:\.js)?|Next\.js'
                           r'|Next(?=\s+v?\d+\.\d))\s+v?(\d+(?:\.\d+)?)\b')
# A version on a line about change or the past describes history, not the current state.
HISTORY = re.compile(r'\b(upgrade[sd]?|upgrading|migrat\w*|moved|removed|deprecated|legacy|previous|previously)\b',
                     re.I)
FROM_BEFORE = re.compile(r'\bfrom\s+$', re.I)  # "from Angular 15": only right before the claimed product
# The packages behind each named product. version_facts.py does not report `next`: it is read from package.json.
PRODUCTS = {'Angular': ('@angular/core',), 'React': ('react',), 'TypeScript': ('typescript',), 'Vite': ('vite',),
            'Ionic': ('@ionic/angular', '@ionic/core', '@ionic/react', '@ionic/vue'),
            'Capacitor': ('@capacitor/core',), 'Laravel': ('laravel/framework',), 'PHP': ('php',),
            'Node': ('node',), 'Node.js': ('node',), 'Next.js': ('next',)}
NODE_PINS = ('.nvmrc', '.node-version')


def version_facts_module():
    """version_facts.py from this folder, loaded by path (the script runs with -I, so its folder is not on
    sys.path)."""
    if 'version_facts' not in sys.modules:
        spec = importlib.util.spec_from_file_location('version_facts', Path(__file__).with_name('version_facts.py'))
        module = importlib.util.module_from_spec(spec)
        sys.modules['version_facts'] = module
        spec.loader.exec_module(module)
    return sys.modules['version_facts']


def reported_versions(scan: Scan, document: str) -> dict[str, tuple[str, str, str]] | str:
    """{package: (kind, value, source)} from version_facts.py for the document's folder, kind being 'locked' or
    'constraint'; or the reason it could not run. Cached per folder."""
    scope = posixpath.dirname(document) or '.'
    if scope not in scan.versions:
        try:
            result = version_facts_module().inspect_versions(scan.root, [scope])
        except (OSError, UnicodeError, ValueError, TypeError, RecursionError) as error:
            scan.versions[scope] = f'version_facts.py could not read the manifests: {error}'
            return scan.versions[scope]
        found: dict[str, tuple[str, str, str]] = {}
        for context in result['contexts']:
            source = context.get('manifest', '')
            lock = context.get('lockfile') or (context.get('lockfiles') or [None])[0] or source
            for row in context.get('packages', []):
                if row.get('locked'):
                    found.setdefault(row['name'], ('locked', row['locked'], lock))
                elif row.get('declared'):
                    found.setdefault(row['name'], ('constraint', row['declared'][0]['constraint'], source))
            for name, rows in context.get('requirements', {}).items():
                found.setdefault(name, ('constraint', rows[0]['constraint'], source))
            if 'node' in context.get('engine_constraints', {}):
                found.setdefault('node', ('constraint', context['engine_constraints']['node'], source))
        scan.versions[scope] = found
    return scan.versions[scope]


def pin_row(scan: Scan, pin: str) -> tuple[str, str, str, str] | None:
    """('pinned', version, file, 'node') from the first non-empty line of an .nvmrc or .node-version file."""
    try:
        lines = [line.strip() for line in (scan.root / pin).read_text(encoding='utf-8-sig').splitlines()]
    except (OSError, UnicodeDecodeError):
        return None
    value = next((line for line in lines if line and not line.startswith('#')), None)
    return ('pinned', value, pin, 'node') if value else None


def declared_row(scan: Scan, document: str, package: str) -> tuple[str, str, str, str] | None:
    """('constraint', value, manifest, package) for a package version_facts.py does not report, read from the
    dependencies or devDependencies of the package.json manifest_for finds."""
    manifest = manifest_for(scan, document, ('package.json',))
    try:
        data = json.loads((scan.root / manifest).read_text(encoding='utf-8-sig')) if manifest else None
    except (OSError, UnicodeDecodeError, ValueError):
        return None
    for field in ('dependencies', 'devDependencies'):
        value = data.get(field, {}).get(package) if isinstance(data, dict) and isinstance(data.get(field), dict) \
            else None
        if isinstance(value, str):
            return 'constraint', value, manifest, package
    return None


def version_fact(scan: Scan, document: str, line: int, product: str, claimed: str) -> dict:
    """A version claim compared with version_facts.py: a locked version must start with the claimed numbers; a
    plain ^, ~ or exact constraint must have the claimed major version. Ranges are not-checkable."""
    product = 'Next.js' if product == 'Next' else product
    fact = {'document': document, 'line': line, 'kind': 'version', 'claim': f'{product} {claimed}'}
    pin = manifest_for(scan, document, NODE_PINS) if product in ('Node', 'Node.js') else None
    row = pin_row(scan, pin) if pin else None
    if row is None and product == 'Next.js':
        row = declared_row(scan, document, 'next')
    if row is None:
        reported = reported_versions(scan, document)
        if isinstance(reported, str):
            return fact | {'status': 'not-checkable', 'evidence': reported}
        row = next((reported[name] + (name,) for name in PRODUCTS.get(product, ()) if name in reported), None)
    if row is None:
        return fact | {'status': 'not-checkable', 'evidence': f'version_facts.py reports no {product} version here'}
    kind, value, source, name = row
    evidence = f'{name} {kind} {value} in {source}'
    numbers = claimed.split('.')
    if kind == 'pinned' and not re.search(r'\d', value):
        return fact | {'status': 'not-checkable', 'evidence': f'{evidence} is an alias, not a number'}
    if kind in ('locked', 'pinned'):
        actual = re.findall(r'\d+', value)[:len(numbers)]
    else:
        plain = re.fullmatch(r'[\^~=v]*\s*(\d+)(?:\.\d+)*(?:\.\*)?', value.strip())
        if not plain:
            return fact | {'status': 'not-checkable', 'evidence': f'{evidence} is a range'}
        actual, numbers = [plain[1]], numbers[:1]
    return fact | {'status': 'matched' if actual == numbers else 'contradicted', 'evidence': evidence}


def document_facts(scan: Scan, documents: list[str]) -> list[dict]:
    """The named facts of each related document. Contradicted facts are also warnings."""
    found = []
    for document in documents:
        text = scan.read(document)
        if text is None:
            continue
        for line, span, sentence, before in placed_code_spans(text):
            fact = path_fact(scan, document, line, span, sentence, before)
            if fact:
                found.append(fact)
        raw = text.splitlines()
        for line, code in code_lines(text):
            # "Run `npm run lint` from `web/`": the line names the folder the command runs in.
            folder = FROM_DIR.search(raw[line - 1]) if line <= len(raw) else None
            base = folder[1] if folder and (scan.root / folder[1]).is_dir() else None
            for m in COMMAND.finditer(code):
                fact = command_fact(scan, document, line, m[1], *command_tokens(code, m.end()), base=base)
                if fact:
                    found.append(fact)
        for line, prose in enumerate(prose_lines(text), 1):
            for m in VERSION_CLAIM.finditer(prose):
                if HISTORY.search(sentence_at(prose, m.start())) or FROM_BEFORE.search(prose[:m.start()]):
                    found.append({'document': document, 'line': line, 'kind': 'version',
                                  'claim': f'{"Next.js" if m[1] == "Next" else m[1]} {m[2]}', 'status': 'not-checkable',
                                  'evidence': 'reads as history'})
                else:
                    found.append(version_fact(scan, document, line, m[1], m[2]))
    # The same claim twice on one line (`npm run x`, then `npm run x -- --check`) is one fact. Keep the first, unless a
    # later mention is contradicted: a planned or historical mention must not hide a contradiction in the same line.
    unique = {}
    for fact in found:
        known = unique.setdefault((fact['document'], fact['line'], fact['kind'], fact['claim']), fact)
        if fact['status'] == 'contradicted' and known['status'] != 'contradicted':
            unique[(fact['document'], fact['line'], fact['kind'], fact['claim'])] = fact
    found = list(unique.values())
    found.sort(key=lambda fact: (fact['document'], fact['line']))
    for fact in found:
        if fact['status'] == 'contradicted':
            scan.add('contradicted-fact', 'warning', fact['document'], fact['line'],
                     f'{fact["kind"]} {fact["claim"]}: {fact["evidence"]}')
    return found


# The checks prove only the named facts below; what the documents mean is the agent's claim review.
MEANING = 'Meaning not checked: review each claim in the related documents.'


def counts(findings: list[Finding]) -> dict[str, int]:
    return {severity: sum(f.severity == severity for f in findings) for severity in SEVERITIES}


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('root')
    parser.add_argument('--json', action='store_true')
    source = parser.add_mutually_exclusive_group()
    source.add_argument('--changed', nargs='+', metavar='PATH', help='list documents related to these files')
    source.add_argument('--changed-from-git', action='store_true',
                        help='the same for the files Git reports as changed or untracked (read-only)')
    args = parser.parse_args(argv)
    root = Path(args.root)
    if not root.is_dir():
        print(f'not a folder: {args.root}', file=sys.stderr)
        return 2
    root = root.resolve()
    scan = check(root)
    changes = [changed_path(root, value) for value in args.changed] if args.changed is not None else None
    if args.changed_from_git:
        changes = git_changes(scan)
    relations = related(scan, changes) if changes is not None else []
    # Task records and archives are intentionally preserved history: listed, never checked as drift.
    historical = sorted({r['document'] for r in relations if historical_document(r['document'])})
    current = sorted({r['document'] for r in relations} - set(historical))
    facts = document_facts(scan, current)
    checked = {fact['document'] for fact in facts if fact['status'] != 'not-checkable'}
    unchecked = sorted(set(current) - checked)
    for relation in relations:
        if relation['document'] in historical:
            relation['historical'] = True
            relation['history'] = history_rule(relation['document'])
        elif relation['document'] in unchecked:
            relation['facts_checked'] = 0  # nothing in it could be matched or contradicted
    findings = sorted(scan.findings, key=lambda f: (SEVERITIES.index(f.severity), f.path, f.line, f.code))
    total = counts(findings)
    if args.json:
        report = {'root': str(root), 'findings': [asdict(f) for f in findings],
                  'reached': sorted(scan.depth), 'counts': total}
        if changes is not None:
            report |= {'changed': changes, 'related': relations, 'facts': facts, 'meaning': 'not checked'}
        print(json.dumps(report, indent=2))
    else:
        for f in findings:
            print(f'{f.severity.upper()} {f.code} {f.path}:{f.line} {f.message}')
        if changes is not None:
            print('Related documents:')
            entry = [r for r in relations if r['reason'] == 'entry point']
            for r in relations:
                if not r.get('historical') and r['reason'] != 'entry point':
                    print(f'  {r["changed"]} -> {r["document"]} ({r["reason"]})')
            if entry:  # every otherwise unrelated file gets the entry point: one line, not one per file
                files = f'{len(entry)} changed file' + ('s' if len(entry) > 1 else '')
                print(f'  {files} -> {entry[0]["document"]} (entry point)')
            for document in historical:
                print(f'  historical, not checked: {document}')
                print(f'    history rule: {history_rule(document)}')
            if not relations:
                print('  none found')
            print('Facts:')
            for fact in facts:
                print(f'  {fact["document"]}:{fact["line"]} {fact["kind"]} {fact["claim"]}: {fact["status"]} '
                      f'({fact["evidence"]})')
            for document in unchecked:
                print(f'  {document}: no checkable facts')
            print(MEANING)
        print(f'docs_check: {total["blocking"]} blocking, {total["warning"]} warning, {total["note"]} note; '
              f'{len(scan.depth)} documents reached')
    return 1 if total['blocking'] else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
