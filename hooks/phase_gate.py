"""PreToolUse hook: after /workflow, code edits and git writes need the current task's recorded approval.

Hooqd retro (2026-11-03): after "Let's do that, push when done" the agent edited code and pushed with no task folder.
The audit of 2026-11-03 (task 2026-11-03-audit-hardening, E1-E8, D1) then found that any phase name in the transcript
counted as permission, chat text granted the lightweight route, and many shell writes slipped past. The rules now:

- The gate is active once the session typed or loaded the workflow router or a phase skill. Loading a phase grants
  nothing by itself.
- Each written target is judged on its own, with `..` resolved and after any `cd`. Free: task records and output
  (`docs/plans/**`, `.artifacts/**` of the target's worktree, and a fixture repository with its own `.git` inside the
  project's `.artifacts`), anything outside the project (the cwd's worktree and the other worktrees of the same
  repository), and rule files while rule-maker is loaded.
- Every other write, and every git write, needs the current task: the `docs/plans/<task>/` the session last wrote
  records in or the user named, looked up inside the target's git worktree. Its PLAN.md checkpoint must either list
  the file on a `- Lightweight edit: <files> — <why>` line (which also allows a `git commit` of only those files
  when the user's latest message asks to commit), or carry an `- Approval:` line that approves, waives or
  reconciles one legacy report (never "not approved", "proposed" or "pending") and quotes in double quotes words that
  match the complete real user answer after the named report was shown: this transcript, or a sibling `*.jsonl` in the same folder (an earlier
  session of the project, so a resumed task keeps its approval). A real user message is one the user typed (also
  while the agent was working), or the choice they picked in AskUserQuestion; tool output, meta entries,
  subagent prompts and hand-backs never count.
- Git commands that write files (`git apply <patch>`, `git checkout ... -- <files>`, `git restore <files>`) are also
  judged per file like an Edit; the files of `git apply` come from the patch headers, and a patch the gate cannot read
  is refused (H3, D36). A record of another approved task with its own write_paths does not stop a file write that
  only the earlier task's write_paths cover (H3, Q17).
- Small-change route (H4, R11): in a task with no plan report, a valid `- Small change: <files> — <what changes>` line
  (comma-separated, repository-relative, existing files; no folders or wildcards) allows writes to exactly those files
  once the Approval line quotes a whole real user message (or AskUserQuestion answer) that came after an offer: a
  `Small change: <files> — <what changes>` line (also wholly in inline code) in an assistant message or delivered question, shown while the task
  was current, with exactly the same file set. Other files, new files, deletions, moves, writes the gate cannot match
  to a file, and git writes outside the Lightweight-edit commit rule are refused with the full-route message. An
  invalid line counts as absent, and the refusal says why.
- A transcript that exists but cannot be read blocks the explicit edit tools. No transcript path: allowed.
- Install guard: in a session the gate is active for, package installs and npx-style downloads need the user's
  latest words (message, AskUserQuestion answer or slash-command arguments) to allow installing.

Shell commands are read best effort; command-text filtering is advice, not a security boundary (workflow/SETUP.md,
"What the hooks enforce"). Exits 0 on bad input.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import posixpath
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from urllib.parse import unquote, urlsplit

PHASES = ('workflow-clarify', 'workflow-specify', 'workflow-execute', 'workflow-deliver')
HOOK_PROTOCOL = '1'
EDIT_TOOLS = ('Edit', 'Write', 'MultiEdit', 'NotebookEdit')
SHELLS = ('Bash', 'PowerShell')
MCP_WRITE = re.compile(r'create|write|edit|delete|apply|update|import|execute|manage', re.I)
MCP_PATH_KEYS = ('file_path', 'filePath', 'path', 'notebook_path', 'target_path', 'targetPath', 'filename', 'file',
                 'destination', 'uri')
TYPED = re.compile(r'<command-name>\s*/(?:workflow-axa:)?(workflow(?:-clarify|-specify|-execute|-deliver)?)\s*</command-name>'
                   r'|^\s*/(?:workflow-axa:)?(workflow(?:-clarify|-specify|-execute|-deliver)?)(?![\w-])', re.M)
RULE_FILE = re.compile(r'(?:^|/)(?:AGENTS|CLAUDE)(?:\.override|\.local)?\.md$|/\.claude/rules/', re.I)
RECORD = re.compile(r'(?:docs/plans|\.artifacts)(?:/|$)', re.I)
# A task path may sit inside markdown emphasis (`**docs/plans/x**`, `_docs/plans/x_`): Putten, 2026-11-07.
TASK_PATH = re.compile(r'docs/plans/([A-Za-z0-9][\w.-]*?)(?=[*_]*(?:/|$|[\s"\'`),;]))')
TASK_NAMED = re.compile(r'docs/plans/([A-Za-z0-9][\w.-]*?)(?=[*_]*(?:/|$|[\s"\'`),;.]))|(?<![\w/-])(\d{4}-\d{2}-\d{2}-[a-z0-9][a-z0-9-]*)')
NULL_TARGETS = ('/dev/null', '/dev/stdout', '/dev/stderr', 'nul', '$null')

# Approval line (TASK-FOLDER.md checkpoint): `- Approval (gate two): <approved/waived/legacy/not approved; ...>`.
APPROVAL = re.compile(r'^\s*[-*]\s*Approval\b[^:\n]*:(.*)$', re.M)
# A resumed task's later confirmation of the same revision: `- Reconfirmed (gate two): r1, <date>: "<words>"`.
RECONFIRMED = re.compile(r'^\s*[-*]\s*Reconfirmed\b[^:\n]*:(.*)$', re.M)
LIGHT_LINE = re.compile(r'^\s*[-*]\s*Lightweight edit:\s*(.+)$', re.M | re.I)
# H4 (R11, A15): `- Small change: <files> — <what changes>`, and the assistant message that offers it to the owner.
SMALL_LINE = re.compile(r'^\s*[-*]\s*Small change:[ \t]*(.*)$', re.M | re.I)
# An offer is a line of the same form, optionally a list item, quoted or in bold: `**Small change:** a.ts — x`.
# V2: a line wholly wrapped in one inline-code span loses one leading and the matching trailing backtick.
SMALL_OFFER_LINE = re.compile(r'^[ \t>*_-]*(`)?[ \t>*_-]*Small change:[*_]*[ \t]*(.*?)(?(1)`)[ \t\r]*$', re.M | re.I)
NEGATIVE = re.compile(r'\b(?:not|never|no)\s+(?:yet\s+)?(?:approved|waived|given)\b|\bunapproved\b|\bproposed\b'
                      r'|\bpending\b|\bawaiting\b|\brevoked\b|\bwithdrawn\b', re.I)
POSITIVE = re.compile(r'\b(?:approved|waived|legacy)\b', re.I)
# Uppercase R identifiers belong to requirements unless explicitly introduced as a revision.
# Keep lowercase rN checkpoint notation and numbered plan/review filenames; exclude qualified IDs.
REVISION = re.compile(r'\b(?i:revision)\s+[rR]?(\d+)(?![\w-])|'
                      r'(?:(?<![\w/-])r|\b(?:plan|review)-r)(\d+)(?![\w-])')
# "no repor" (Putten, 2026-11-07) is a typo of "no report"; "no repository" is not.
NO_REPORT = re.compile(r'\b(?:no\s+(?:plan\s+|html\s+)?repo(?!sitor)\w*|without\s+(?:the\s+|an?\s+)?(?:html\s+|plan\s+)?report)\b', re.I)  # the user skipped the plan report
QUOTE = re.compile(r'"([^"\n]+)"|\u201c([^\u201d\n]+)\u201d')

# Shell writes. Interpreter code that writes files: Python, Node, PHP, Ruby, .NET (E4: node -e writeFileSync).
CODE_WRITE = re.compile(r"\bopen\([^)]*,\s*['\"](?:[wax]|r\+)b?\+?['\"]|\.write_(?:text|bytes)\(|\b(?:write|append)File(?:Sync)?\b"
                        r"|\bcreateWriteStream\b|\b(?:unlink|rm|rename|copyFile)Sync\b|\bos\.(?:remove|unlink|rename|replace)\("
                        r"|\bshutil\.(?:copy\w*|move|rmtree)\(|\.unlink\(|\bfile_put_contents\(|\bFile\.write\("
                        r"|\b(?:WriteAll|AppendAll)\w*\(")
DOTNET_WRITE = re.compile(r"\b(?:WriteAll|AppendAll)\w*\(\s*(['\"])(.+?)\1")
RECORD_TOOL = Path(__file__).resolve().parents[1].joinpath('skills', 'workflow', 'scripts', 'record.py').as_posix()
HEREDOC = re.compile(r'<<-?\s*([\'"]?)([A-Za-z_]\w*)\1')
HERE_STRING = re.compile(r'@([\'"])\r?\n(.*?)\r?\n\1@', re.S)
INTERPRETERS = ('python', 'python3', 'py', 'node', 'deno', 'bun', 'ruby', 'php', 'perl')
SUBSHELLS = ('bash', 'sh', 'zsh', 'powershell', 'pwsh', 'cmd')
CD_COMMANDS = ('cd', 'pushd', 'chdir', 'set-location', 'sl')
CONTENT_WRITERS = ('set-content', 'sc', 'add-content', 'ac', 'out-file', 'clear-content', 'clc', 'new-item', 'ni',
                   'tee-object')
POSIX_WRITERS = ('tee', 'touch', 'truncate', 'mkdir', 'md')
REMOVERS = ('rm', 'del', 'erase', 'rd', 'rmdir', 'remove-item', 'ri', 'unlink', 'shred')
COPIERS = ('cp', 'copy', 'copy-item', 'cpi', 'install', 'rsync')
MOVERS = ('mv', 'move', 'move-item', 'mi', 'ren', 'rename-item', 'rni')
# H4: label words that mark a write as a deletion (or emptying) or as a move, for the small-change route.
DELETING, MOVING = ' deleting ', ' moving or renaming '
PS_TARGET = ('path', 'literalpath', 'filepath', 'destination', 'dest', 'pspath', 'lp')
PS_VALUE = PS_TARGET + ('value', 'encoding', 'itemtype', 'type', 'filter', 'include', 'exclude', 'name', 'newname',
                        'erroraction', 'stream', 'width', 'inputobject', 'credential', 'delimiter', 'warningaction')
GIT_WRITES = ('commit', 'push', 'merge', 'apply', 'cherry-pick', 'rebase', 'revert', 'am', 'pull', 'rm', 'mv', 'restore',
              'switch')


# Paths

def slash(path: str) -> str:
    return path.replace('\\', '/')


def absolute(path: str, base: str) -> str:
    """Forward-slash absolute path with `.` and `..` resolved; Git Bash /d/x becomes d:/x. Relative stays relative
    when there is no base."""
    p = slash(path.strip())
    if p.startswith('~'):
        p = slash(str(Path.home())) + p[1:]
    p = re.sub(r'^/([a-zA-Z])(?=/|$)', r'\1:', p)
    if not re.match(r'^(?:[a-zA-Z]:|/)', p) and base:
        p = absolute(base, '').rstrip('/') + '/' + p
    drive = ''
    found = re.match(r'^([a-zA-Z]:)(.*)$', p)
    if found:
        drive, p = found.group(1), found.group(2) or '/'
    return drive + posixpath.normpath(p)


def key(path: str) -> str:
    return path.rstrip('/').lower()


def under(path: str, root: str) -> bool:
    k, r = key(path), key(root)
    return bool(r) and (k == r or k.startswith(r + '/'))


def relative(path: str, root: str | None) -> str:
    return path[len(root.rstrip('/')):].lstrip('/') if root and under(path, root) else path


def git_clean_called(command: str, powershell: bool) -> bool:
    """A `git clean` that deletes (not `-n`/`--dry-run`), read from the parsed command words, so the words "git clean"
    inside a commit message, an echo or a heredoc body never count."""
    text, _ = split_bodies(command)
    for words, _ in segments(lex(text, powershell)):
        while words and (re.match(r'^[A-Za-z_]\w*=', words[0]) or words[0] in ('sudo', 'command', 'env', 'time')):
            words = words[1:]
        name = re.sub(r'\.exe$', '', slash(words[0]).rsplit('/', 1)[-1].lower()) if words else ''
        if name in ('bash', 'sh', 'zsh', 'powershell', 'pwsh', 'cmd'):
            # A subshell's command text (`bash -c "..."`, `powershell -Command "..."`, `cmd /c ...`) is read as well.
            flag = next((i for i, arg in enumerate(words[1:-1], 1) if arg.lower() in ('-c', '-command', '/c')), None)
            if flag is not None and git_clean_called(' '.join(words[flag + 1:]), name in ('powershell', 'pwsh')):
                return True  # only the first flag is read: the rest is its command text (review V10)
            continue
        if name != 'git':
            continue
        args, i = words[1:], 0
        while i < len(args) and args[i].startswith('-'):
            i += 2 if args[i] in ('-C', '-c', '--git-dir', '--work-tree', '--namespace') else 1
        if i < len(args) and args[i] == 'clean':
            rest = args[i + 1:]
            if not any(a in ('-n', '--dry-run') or re.fullmatch(r'-[A-Za-z]*n[A-Za-z]*', a) for a in rest):
                return True
    return False


def bulk_delete(event: dict, targets: list[tuple[str, str, str]], project) -> str | None:
    """T3 of 2026-11-12 (owner Q9 a): git clean, deleting the .artifacts folder itself and wildcard deletes under it.
    Named files and folders under .artifacts stay deletable (ARTIFACTS.md cleanup)."""
    command = str((event.get('tool_input') or {}).get('command', '')) if event.get('tool_name') in SHELLS else ''
    if command and git_clean_called(command, event.get('tool_name') == 'PowerShell'):
        return ('workflow-axa: `git clean` deletes untracked and ignored output in bulk, including .artifacts. '
                'Delete named files instead (ARTIFACTS.md); `git clean -n` only lists them.')
    for kind, where, label in targets:
        if kind != 'path' or DELETING not in label:
            continue
        rel = relative(where, project.root_of(where)).rstrip('/')
        if key(rel) == '.artifacts' or (key(rel).startswith('.artifacts/') and re.search(r'[*?\[]', rel)):
            return (f'workflow-axa: {label} deletes the .artifacts folder or a wildcard set of files in it. Delete named '
                    'files or folders instead, after the ownership checks in ARTIFACTS.md.')
    return None


def is_absolute(path: str) -> bool:
    return bool(re.match(r'^(?:[a-zA-Z]:|/)', path))


def worktree(path: str) -> str | None:
    """The nearest folder at or above the path that holds `.git` (a folder, or a linked worktree's file)."""
    if not is_absolute(path):
        return None
    full = absolute(path, '')
    if re.match(r'^[a-zA-Z]:', full) and os.name != 'nt':
        return None  # a Windows path on POSIX names no folder here; pathlib would read it as relative to the cwd
    parts = full.rstrip('/').split('/')  # parsed as text, so no parent is ever "." or the process folder
    for end in range(len(parts), 0, -1):
        folder = '/'.join(parts[:end])
        try:
            if os.path.exists(folder + '/.git'):
                return folder if folder and not folder.endswith(':') else folder + '/'
        except (OSError, ValueError):
            return None
    return None


def common_dir(root: str | None) -> str | None:
    """The repository's shared git folder, so two worktrees of one repository compare equal."""
    if not root:
        return None
    git = Path(root) / '.git'
    if git.is_dir():
        return key(slash(str(git)))
    try:
        found = re.match(r'\s*gitdir:\s*(.+?)\s*$', git.read_text(encoding='utf-8', errors='replace'))
    except OSError:
        return None
    if not found:
        return None
    gitdir = absolute(found.group(1), root)
    try:
        return key(absolute((Path(gitdir) / 'commondir').read_text(encoding='utf-8').strip(), gitdir))
    except OSError:
        pass
    parts = gitdir.rstrip('/').split('/')
    return key('/'.join(parts[:-2])) if len(parts) > 2 and parts[-2] == 'worktrees' else key(gitdir)


class Project:
    """The project folder: the cwd's worktree (or the cwd), plus the other worktrees of the same repository."""

    def __init__(self, cwd: str):
        self.cwd = absolute(cwd, '') if cwd else ''
        self.root = (worktree(self.cwd) or self.cwd) if self.cwd else ''
        self.common = common_dir(worktree(self.cwd)) if self.cwd else None

    def contains(self, path: str) -> bool:
        if not is_absolute(path):
            return True  # relative with no cwd: inside the project
        if self.root and under(path, self.root):
            return True
        tree = worktree(path)
        return bool(tree and self.common and common_dir(tree) == self.common)

    def root_of(self, path: str) -> str:
        return worktree(path) or self.root

    def is_record(self, path: str) -> bool:
        """Task records and output of the target's worktree. V2: a disposable fixture repository (its own `.git`) in
        the project's own .artifacts folder is output too; a linked worktree of this repository there is not."""
        tree = self.root_of(path)
        if RECORD.match(relative(path, tree)):
            return True
        return (bool(self.root) and key(tree) != key(self.root) and under(path, self.root)
                and bool(re.match(r'\.artifacts(?:/|$)', relative(path, self.root), re.I))
                and not (self.common and common_dir(tree) == self.common))


# Shell commands

def lex(text: str, powershell: bool) -> list[tuple[str, str]]:
    """Words and operators. Quotes are removed without escape handling, so Windows paths keep their backslashes."""
    out: list[tuple[str, str]] = []
    word, started, quote, depth, i = '', False, '', 0, 0

    def flush():
        nonlocal word, started
        if started:
            out.append(('w', word))
        word, started = '', False

    while i < len(text):
        c = text[i]
        if quote:
            if quote == '"' and not powershell and c == '\\' and text[i + 1:i + 2] in ('"', '\\'):
                word += text[i + 1]  # bash: \" and \\ inside double quotes (Putten: `"... (user: \"let's ...\")"`)
                i += 2
                continue
            if c == quote:
                quote = ''
            else:
                word += c
            i += 1
            continue
        if c in '"\'':
            quote, started = c, True
        elif c == '#' and not started:
            while i < len(text) and text[i] != '\n':
                i += 1
            continue
        elif c in ' \t\r':
            flush()
        elif c in '\n;':
            flush()
            out.append(('op', ';'))
        elif text.startswith(('&&', '||'), i):
            flush()
            out.append(('op', ';'))
            i += 1
        elif c == '|':
            flush()
            out.append(('op', '|'))
        elif c == '(' and started:
            depth += 1
            word += c
        elif c == ')' and depth:
            depth -= 1
            word += c
        elif c in '(){}' and not (c == '{' and started) and not (c == '}' and started):
            flush()
            out.append(('op', ';'))
        elif c == '>' or (c == '&' and text.startswith('&>', i)):
            fd = '&' if c == '&' else ('1' if not started else word if word in ('1', '2', '3', '*') else None)
            if c == '&':
                i += 1
            if fd is None:
                flush()
                fd = '1'
            else:
                word, started = '', False
            i += 1
            while i < len(text) and text[i] in '>|':
                i += 1
            if i < len(text) and text[i] == '&':  # 2>&1, >&2: a copy of a stream, no file
                i += 1
                while i < len(text) and (text[i].isdigit() or text[i] == '-'):
                    i += 1
                continue
            out.append(('op', 'redir:' + fd))
            continue
        elif c == '<':
            flush()
            while i < len(text) and text[i] in '<-':
                i += 1
            out.append(('op', 'in'))
            continue
        elif c == '&':
            flush()
            if not powershell:
                out.append(('op', ';'))
        else:
            word += c
            started = True
        i += 1
    flush()
    return out


def segments(tokens: list[tuple[str, str]]):
    """(words, redirect targets) per simple command."""
    words: list[str] = []
    redirects: list[str] = []
    pending = ''
    for kind, value in tokens:
        if kind == 'op' and value in (';', '|'):
            yield words, redirects
            words, redirects, pending = [], [], ''
        elif kind == 'op':
            pending = value
        elif pending:
            if pending in ('redir:1', 'redir:&', 'redir:*'):
                redirects.append(value)
            pending = ''
        else:
            words.append(value)
    yield words, redirects


def split_bodies(command: str) -> tuple[str, list[str]]:
    """The command without heredoc and PowerShell here-string bodies, and those bodies."""
    bodies = [m.group(2) for m in HERE_STRING.finditer(command)]
    command = HERE_STRING.sub("''", command)
    lines, kept, i = command.split('\n'), [], 0
    while i < len(lines):
        line = lines[i]
        kept.append(line)
        i += 1
        for found in HEREDOC.finditer(line):
            body = []
            while i < len(lines) and lines[i].strip() != found.group(2):
                body.append(lines[i])
                i += 1
            i += 1
            bodies.append('\n'.join(body))
    return '\n'.join(kept), bodies


def path_literals(code: str) -> list[str]:
    """Quoted strings in inline code that look like file paths."""
    found = []
    for match in re.finditer(r'([\'"])((?:(?!\1)[^\n])+?)\1', code):
        text = match.group(2).strip()
        if '://' in text or not re.fullmatch(r'[\w.~:$/\\ -]+', text):
            continue
        if (('/' in text or '\\' in text) and re.search(r'[A-Za-z0-9]{2}', text)) or re.search(r'\w\.\w{1,6}$', text):
            found.append(text)
    return found


def ps_params(args: list[str]) -> tuple[dict[str, list[str]], list[str]]:
    named: dict[str, list[str]] = {}
    positional: list[str] = []
    i = 0
    while i < len(args):
        arg = args[i]
        if re.match(r'^-[A-Za-z]', arg):
            name, _, inline = arg[1:].partition(':')
            name = name.lower()
            if inline:
                named.setdefault(name, []).append(inline)
            elif name in PS_VALUE and i + 1 < len(args):
                named.setdefault(name, []).append(args[i + 1])
                i += 1
        else:
            positional.append(arg)
        i += 1
    return named, positional


def git_writes(args: list[str], here: str) -> list[tuple[str, str, str]]:
    repo, alias, i = here, False, 0
    while i < len(args):
        arg = args[i]
        if arg in ('-C', '-c') and i + 1 < len(args):
            if arg == '-C':
                repo = absolute(args[i + 1], repo)
            else:
                alias = alias or args[i + 1].lower().startswith('alias.')
            i += 2
            continue
        if arg.startswith('--work-tree='):
            repo = absolute(arg.split('=', 1)[1], repo)
        elif not arg.startswith('-'):
            break
        i += 1
    sub, rest = (args[i], args[i + 1:]) if i < len(args) else ('', [])
    write = (sub in GIT_WRITES or (sub == 'reset' and '--hard' in rest)
             or (sub == 'clean' and not {'-n', '--dry-run'} & set(rest))
             or (sub == 'checkout' and bool({'--', '.', '-f', '--force'} & set(rest)))
             or (sub == 'stash' and rest[:1] in ([], ['pop'], ['apply'], ['push'], ['save'], ['drop'], ['clear']))
             or (sub == 'branch' and bool({'-D', '--force'} & set(rest)))
             or (sub == 'worktree' and rest[:1] == ['add']) or (alias and bool(sub)))
    if not write:
        return []
    shown = {'reset': ' --hard', 'branch': ' -D', 'worktree': ' add'}.get(sub, '')
    if sub == 'commit' and any(a == '--amend' for a in rest):
        shown = ' --amend'  # rewrites an earlier commit: never a lightweight commit
    files = git_file_writes(sub, rest, repo)
    return [('git', repo, f"`git {sub}{shown}`" + (GIT_FILE_WRITE if files else ''))] + files


GIT_FILE_WRITE = ' of files'  # marks the git target of a command whose written files are separate path targets (H3)


GIT_APPLY_VALUES = ('--whitespace', '--exclude', '--include', '--directory', '--build-fake-ancestor')
GIT_RESTORE_VALUES = ('-s', '--source', '--conflict')


def git_file_writes(sub: str, rest: list[str], repo: str) -> list[tuple[str, str, str]]:
    """H3 (D36): the files `git apply`, `git checkout ... -- <files>` and `git restore <files>` write, as path targets
    judged like an Edit (approval and write_paths). A patch the gate cannot read becomes a 'refused' target."""
    top = worktree(repo) or repo
    if sub == 'checkout' and '--' in rest:
        return [('path', absolute(f, repo), f'`git checkout` of {f}') for f in rest[rest.index('--') + 1:]]
    if sub == 'restore':
        files, skip, literal = [], False, False
        for arg in rest:
            if skip:
                skip = False
            elif literal or not arg.startswith('-'):
                files.append(arg)
            elif arg == '--':
                literal = True
            elif arg in GIT_RESTORE_VALUES:
                skip = True
        return [('path', absolute(f, repo), f'`git restore` of {f}') for f in files]
    if sub != 'apply' or (set(rest) & {'--check', '--stat', '--numstat', '--summary'} and '--apply' not in rest):
        return []  # a report on the patch stays an approval-only git write, as before H3 (owner: preserve protections)
    patches, strip, prefix, value_of = [], 1, '', None
    for arg in rest:
        if value_of == '-p' and arg.isdigit():
            strip = int(arg)
        elif value_of == '--directory':
            prefix = arg.strip('/') + '/'
        elif value_of:
            pass  # the value of another option, such as --whitespace nowarn
        elif arg in GIT_APPLY_VALUES or arg == '-p':
            value_of = arg  # the value is the next word
            continue
        elif re.fullmatch(r'-p\d+', arg):
            strip = int(arg[2:])
        elif arg.startswith('--directory='):
            prefix = arg.split('=', 1)[1].strip('/') + '/'
        elif arg == '-' or not arg.startswith('-'):
            patches.append(arg)
        value_of = None
    reason = ("workflow-axa: `git apply` was refused because the gate cannot read the patch {what}, so it cannot check "
              "which files it changes against the approved plan. Save the patch as a file and pass its path to "
              "`git apply`, or make the change with the Edit tool.")
    if not patches or '-' in patches:
        return [('refused', repo, reason.format(what='from standard input'))]
    targets = []
    for name in patches:
        try:
            text = Path(absolute(name, repo)).read_text(encoding='utf-8', errors='replace')
        except (OSError, ValueError) as error:
            return [('refused', repo, reason.format(what=f'{name} ({type(error).__name__})'))]
        files = patch_files(text, strip)
        if not files:
            return [('refused', repo, reason.format(what=f'{name} (it names no files)'))]
        targets += [('path', absolute(prefix + f, top), f'`git apply` writing {prefix + f}') for f in files]
    return list(dict.fromkeys(targets))  # each file once per command, also across patches


def patch_files(text: str, strip: int = 1) -> list[str]:
    """The files a unified or git diff touches, from its headers: `diff --git a/x b/y`, `--- a/x`, `+++ b/y`, and
    rename/copy lines. /dev/null (a new or deleted file's other side) is skipped; `strip` is git apply's -p.
    Header lines count only outside hunks: each `@@ -a,b +c,d @@` is followed by its b old and d new lines, so a
    removed line starting with "-- " or an added line starting with "++ " inside a hunk is never read as a header."""
    def cut(name: str) -> str:
        name = name.strip().strip('"')
        parts = name.split('/')
        return '/'.join(parts[strip:]) if len(parts) > strip else ''

    files: list[str] = []
    old = new = 0  # lines left in the current hunk
    for line in text.splitlines():
        if (old > 0 or new > 0) and line[:1] not in ('', ' ', '+', '-', '\\'):
            old = new = 0  # not hunk content (a hunk shorter than it said): read the line as a header again
        if old > 0 or new > 0:
            if line.startswith('\\'):
                continue  # "\ No newline at end of file"
            if line.startswith('-'):
                old -= 1
            elif line.startswith('+'):
                new -= 1
            else:
                old, new = old - 1, new - 1  # context (also a blank context line)
            continue
        names: list[str] = []
        found = re.match(r'^@@ -\d+(?:,(\d+))? \+\d+(?:,(\d+))? @@', line)
        if found:
            old, new = int(found.group(1) or 1), int(found.group(2) or 1)
            continue
        found = re.match(r'^diff --git (\S+) (\S+)\s*$', line)
        if found:
            names += [cut(found.group(1)), cut(found.group(2))]
        found = re.match(r'^(?:---|\+\+\+) ([^\t]+)', line)
        if found and found.group(1).strip() != '/dev/null':
            names.append(cut(found.group(1)))
        found = re.match(r'^(?:rename|copy) (?:from|to) (.+?)\s*$', line)
        if found:
            names.append(found.group(1).strip('"'))
        files += [n for n in dict.fromkeys(names) if n and n not in files]
    return files


def shell_writes(command: str, cwd: str | None, powershell: bool = False) -> list[tuple[str, str, str]]:
    """What a shell command writes, best effort: ('path', absolute path, label), ('git', repository folder, label) and
    ('ambiguous', relative path, label) for a write relative to a folder an unresolved variable named (cwd None)."""
    text, bodies = split_bodies(command)
    here = None if cwd is None else absolute(cwd, '') if cwd else ''
    writes: list[tuple[str, str, str]] = []
    names: dict[str, str] = {}  # shell variables set earlier in the command (f=docs/plans/t/PLAN.md, $f = '...')

    def expand(value: str) -> str:
        return re.sub(r'\$\{?(\w+)\}?', lambda m: names.get(m.group(1), m.group(0)), value)

    def add(target: str, label: str):
        target = expand(target)
        if not target or target.lower() in NULL_TARGETS or '$' in target or target.startswith('-'):
            return  # an unknown variable or an option: not judged
        if here is None and not re.match(r'^(?:[A-Za-z]:|[\/]|~)', target):
            writes.append(('ambiguous', target, label))  # relative to a folder an unresolved variable named
            return
        writes.append(('path', absolute(target, here), label))

    for found in DOTNET_WRITE.finditer(text):
        add(found.group(2), f'a .NET file write into {found.group(2)}')
    for words, redirects in segments(lex(text, powershell)):
        # H4: a redirect from nothing (`> f`, `: > f`, `cat /dev/null > f`) empties the file. `>>` cannot be told apart
        # here, so it is counted as emptying too; that only matters on the small-change route, where it is refused.
        empties = [w.lower() for w in words] in ([], [':'], ['true'], ['cat', '/dev/null'], ['type', 'nul'])
        for target in redirects:
            add(target, f'a redirect{DELETING if empties else " into "}{target}')
        if len(words) >= 3 and re.fullmatch(r'\$[A-Za-z_]\w*', words[0]) and words[1] == '=':
            names[words[0][1:]] = expand(words[2])  # PowerShell: $f = 'path'
            continue
        while words and (re.match(r'^[A-Za-z_]\w*=', words[0]) or words[0] in ('sudo', 'command', 'env', 'time',
                                                                                 'nohup', 'exec', 'then', 'do', 'else', '!', '&')):
            found = re.match(r'^([A-Za-z_]\w*)=(.*)$', words[0])
            if found:
                names[found.group(1)] = expand(found.group(2))
            words = words[1:]
        if not words:
            continue
        called = re.fullmatch(r'\$(?:\{(\w+)\}|(\w+))', words[0])
        held = names.get((called.group(1) or called.group(2)) if called else '', '')
        if 'record.py' in held:
            # 2026-11-11 (E36, D36): `R="python ... record.py" && $R append docs/plans/<task>/...` hid the record write,
            # so the current task never followed it. Only a variable set earlier in this command and holding record.py.
            words = [w.strip('"\'') for w in held.split()] + words[1:]
        name = re.sub(r'\.exe$', '', slash(words[0]).rsplit('/', 1)[-1].lower())
        args = words[1:]
        plain = [a for a in args if not a.startswith('-')]
        if name in CD_COMMANDS:
            if plain and plain[-1] != '-':
                target = expand(plain[-1])  # rc3 trial L6: `cd "$R"` was not expanded, so records looked like code
                if '$' in target or (here is None and not re.match(r'^(?:[A-Za-z]:|[\/]|~)', target)):
                    here = None  # unresolved: later relative writes need an explicit path
                else:
                    here = absolute(target, here)
        elif name == 'git':
            found = git_writes(args, here or '')
            writes += [('ambiguous', '', label) if here is None and not re.match(r'^(?:[A-Za-z]:|/)', repo) else
                       (kind, repo, label) for kind, repo, label in found]
        elif name in SUBSHELLS:
            for i, arg in enumerate(args[:-1]):
                if arg.lower() in ('-c', '-command', '/c'):
                    writes += shell_writes(args[i + 1], here, name in ('powershell', 'pwsh'))
                    break
        elif name in CONTENT_WRITERS:
            named, positional = ps_params(args)
            for target in [v for k in PS_TARGET for v in named.get(k, [])] or positional[:1]:
                add(target, f'`{words[0]}`{DELETING if name in ("clear-content", "clc") else " into "}{target}')
        elif name == 'truncate':
            files, size, skip = [], None, False
            for arg in args:
                if skip:
                    size, skip = arg, False
                elif arg in ('-s', '--size'):
                    skip = True
                elif arg.startswith('--size='):
                    size = arg.split('=', 1)[1]
                elif not arg.startswith('-'):
                    files.append(arg)
            for target in files:
                add(target, f'`{words[0]}`{DELETING if size in ("0", "-0") else " on "}{target}')
        elif name in POSIX_WRITERS + REMOVERS:
            named, positional = ps_params(args)
            for target in [v for k in PS_TARGET for v in named.get(k, [])] + positional:
                add(target, f'`{words[0]}`{DELETING if name in REMOVERS else " on "}{target}')
        elif name in COPIERS:
            named, positional = ps_params(args)
            targets = named.get('destination', []) + named.get('dest', [])
            if not targets and len(positional) > 1:
                targets = positional[-1:]  # the destination is the last argument
            for target in targets:
                add(target, f'`{words[0]}` into {target}')
        elif name in MOVERS:
            named, positional = ps_params(args)
            for target in [v for k in PS_TARGET for v in named.get(k, [])] + positional:
                add(target, f'`{words[0]}`{MOVING}{target}')
        elif name == 'sed' and any(re.match(r'^-[A-Za-z]*i', a) or a == '--in-place' for a in args):
            files, script_given, skip = [], False, False
            for arg in args:
                if skip:
                    skip = False
                elif arg in ('-e', '-f', '--expression', '--file'):
                    script_given = skip = True
                elif not arg.startswith('-'):
                    files.append(arg)
            for target in files if script_given else files[1:]:
                add(target, f'an in-place edit (`sed -i`) of {target}')
        elif name in INTERPRETERS and any(slash(expand(a)).endswith(('record.py', 'render_report.py')) for a in args):
            # Putten (2026-11-07): `R=".../record.py"; python -X utf8 -I "$R" batch ...` hid the record write, so the
            # current task never followed it.
            script = next(i for i, a in enumerate(args) if slash(expand(a)).endswith(('record.py', 'render_report.py')))
            rest = args[script + 1:]
            if slash(expand(args[script])).endswith('record.py'):
                files = [a for a in rest if not a.startswith('-')][1:2]  # record.py <verb> <file> ...
            else:
                files = [rest[i + 1] for i, a in enumerate(rest[:-1]) if a == '--output']
            for target in files:
                add(target, f'`{slash(expand(args[script])).rsplit("/", 1)[-1]}` writing {target}')
        elif name in INTERPRETERS:
            code = ''
            for i, arg in enumerate(args):
                if arg in ('-c', '-e', '--eval', '-E', '-r') and i + 1 < len(args):
                    code = args[i + 1]
                    break
            if name == 'perl' and any(re.match(r'^-[A-Za-z]*i', a) for a in args):
                for target in [a for a in plain if a != code][1 if not code else 0:]:
                    add(target, f'an in-place edit (`perl -i`) of {target}')
                continue
            if not code and (not plain or plain[0] == '-'):
                code = '\n'.join(bodies)
            if code and CODE_WRITE.search(code):
                literals = [t for t in (expand(t) for t in path_literals(expand(code))) if '$' not in t]
                for target in literals:
                    add(target, f'inline {name} code writing {target}')
                if not literals and here is None:
                    writes.append(('ambiguous', '', f'inline {name} code that writes files'))
                elif not literals and here:
                    writes.append(('path', here, f'inline {name} code that writes files in {here}. The gate could not '
                                   f'tell which file it writes. For task records use `python -X utf8 -I "{RECORD_TOOL}"`; '
                                   'for other files use the Edit or Write tools'))
    return writes


def shell_report_paths(command: str, cwd: str, powershell: bool = False) -> list[str]:
    """Resolve report-path arguments in a shell call using the gate's existing lexer, variable and cd conventions.

    This is a conservative, best-effort recogniser, not shell execution. Unknown variables or working directories
    cannot provide report evidence; approval then requires focused reconfirmation.
    """
    text, bodies = split_bodies(command)
    here: str | None = absolute(cwd, '') if cwd else None
    names: dict[str, str] = {}
    paths: list[str] = []

    def expand(value: str) -> str:
        return re.sub(r'\$\{?(\w+)\}?', lambda match: names.get(match.group(1), match.group(0)), value)

    for words, redirects in segments(lex(text, powershell)):
        if len(words) >= 3 and re.fullmatch(r'\$[A-Za-z_]\w*', words[0]) and words[1] == '=':
            names[words[0][1:]] = expand(words[2])  # PowerShell: $t = 'docs/plans/task'
            continue
        while words and (re.match(r'^[A-Za-z_]\w*=', words[0]) or words[0] in ('sudo', 'command', 'env', 'time',
                                                                                 'nohup', 'exec', 'then', 'do', 'else', '!', '&')):
            assignment = re.match(r'^([A-Za-z_]\w*)=(.*)$', words[0])
            if assignment:
                names[assignment.group(1)] = expand(assignment.group(2))
            words = words[1:]
        if not words:
            continue
        name = re.sub(r'\.exe$', '', slash(words[0]).rsplit('/', 1)[-1].lower())
        args = words[1:]
        if name in CD_COMMANDS:
            plain = [arg for arg in args if not arg.startswith('-')]
            if plain and plain[-1] != '-':
                target = expand(plain[-1])
                if '$' in target or (here is None and not is_absolute(target) and not target.startswith('~')):
                    here = None
                else:
                    here = absolute(target, here or '')
            continue
        for arg in args + redirects:
            # A whole argument, or a path inside one: `python -c "open('plan-r1.html')"`, `bash -c "cat ..."`.
            # A quoted path may contain spaces, so the whole argument is tried too; only existing reports count later.
            whole = [arg] if arg.lower().endswith('.html') else []
            pieces = whole + (PATH_PIECE.findall(arg) if not whole or re.search(r'\s', arg) else [])
            paths += [p for p in (resolve_piece(piece, expand, here) for piece in pieces) if p]
    for body in bodies:  # heredoc and here-string bodies: audit 2026-11-05, `python - <<'EOF' ... open('...html')`
        paths += [p for p in (resolve_piece(piece, expand, here) for piece in PATH_PIECE.findall(body)) if p]
    return paths


PATH_PIECE = re.compile(r"""[^\s"'`;|&<>()=,\[\]{}]+\.html\b""", re.I)


def resolve_piece(piece: str, expand, here: str | None) -> str | None:
    """An absolute path for a report-like piece, or None when a variable or the working folder is unknown."""
    target = expand(piece)
    if '$' in target or not target.lower().endswith('.html'):
        return None
    if here is None and not is_absolute(target) and not target.startswith('~'):
        return None
    return absolute(target, here or '')


# The tool call

def targets_of(event: dict) -> list[tuple[str, str, str]]:
    tool, data, cwd = event.get('tool_name') or '', event.get('tool_input') or {}, str(event.get('cwd') or '')
    if tool in SHELLS:
        return shell_writes(str(data.get('command', '')), cwd, tool == 'PowerShell')
    if tool in EDIT_TOOLS:
        path = str(data.get('file_path') or data.get('notebook_path') or '')
        return [('path', absolute(path, cwd), f'editing {path}')] if path else []
    if tool.startswith('mcp__') and MCP_WRITE.search(tool.rsplit('__', 1)[-1]):
        paths = [str(data[k]) for k in MCP_PATH_KEYS if isinstance(data.get(k), str) and data[k].strip()]
        paths = [re.sub(r'^file:/{2,3}', '', p) for p in paths if '://' not in p or p.startswith('file:')]
        if paths:
            return [('path', absolute(p, cwd), f'the MCP tool {tool} on {p}') for p in paths]
        return [('mcp', absolute(cwd, '') if cwd else '', f'the MCP tool {tool}')]
    return []


# The transcript

# One small state file per transcript; files unused for CACHE_DAYS are removed when the hook writes (tests point
# WORKFLOW_AXA_GATE_CACHE at their own temporary folder).
CACHE_DIR = Path(os.environ.get('WORKFLOW_AXA_GATE_CACHE') or Path(tempfile.gettempdir()) / 'workflow-axa-gate')
CACHE_DAYS = 14
STATE_VERSION = 25
REFUSAL = re.compile(r"(?<!\w)(?:no|not|don'?t|niet|nee)(?!\w)")
TASK_REVIEW = re.compile(r'docs/plans/([A-Za-z0-9][\w.-]*?)/(?:reviews/)?([\w.-]+\.html)\b')
BARE_REVIEW = re.compile(r'(?<![\w/.-])reviews/([\w.-]+\.html)\b')
REPORT_REFERENCE = re.compile(r'(?:(?:[A-Za-z]:/|/)[^\n`<>"\']*?)?'
                              r'docs/plans/[A-Za-z0-9][\w.-]*?/(?:reviews/)?[\w.-]+\.html'
                              r'(?=[*_]*(?:$|[\s`<>"\'\]),;]|\.(?=\s|$)|[!?](?=\s|$)))')
INLINE_TARGET = re.compile(r'''\s*(?:<([^<>"'\r\n]+)>|([^\s<>"']+))(?:\s+(?:"(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*'|\((?:[^()\\]|\\.)*\)))?\s*''')
URI_REFERENCE = re.compile(r'(?<![\w+.-])(?:[A-Za-z][\w+.-]*://|[A-Za-z][\w+.-]+:)'
                           r'[^\s`<>"\'()]+')
# Report fingerprints this hook leaves in the transcript as host-recorded hook context (never agent text): one after a
# tool call that names a task report (read, written or rendered), and one when the owner answers.
SHOWN_MARK, REPLY_MARK = 'workflow-axa report fingerprint', 'workflow-axa report at owner reply'
FINGERPRINT = re.compile(r'^(workflow-axa report (?:fingerprint|at owner reply)): (docs/plans/\S+?\.html) sha256=([0-9a-f]{64})$', re.M)
IDE_TEXT = re.compile(r'<(ide_\w+)>.*?</\1>', re.S)
SKILL_READ = re.compile(r'/(workflow(?:-clarify|-specify|-execute|-deliver)?)/SKILL\.md$')


def package_skill_read(data: dict) -> bool:
    """For plain_reply's Stop hook only (H2, 2026-11-11): a whole Read (no offset or limit) of the router's or a phase's
    SKILL.md, under CLAUDE_PLUGIN_ROOT when the host sets it. The gate's own activation below keeps its broader rule:
    any whole read of such a file turns the gate on (owner: "Preserve ALL existing ... protections")."""
    path = slash(str(data.get('file_path', '')))
    if data.get('limit') or data.get('offset') or not SKILL_READ.search(path):
        return False
    root = os.environ.get('CLAUDE_PLUGIN_ROOT')
    return not root or under(absolute(path, ''), absolute(root, ''))


def user_text(entry: dict) -> str | None:
    """What the user typed, or None for tool results, meta, sidechain (an agent's prompt), a subagent's hand-back or
    a task notification (origin other than human), hook or command output. IDE context tags are removed."""
    origin = entry.get('origin')
    if entry.get('type') != 'user' or entry.get('isMeta') or entry.get('isSidechain') or entry.get('isCompactSummary') \
            or 'toolUseResult' in entry or (isinstance(origin, dict) and origin.get('kind') != 'human'):
        return None
    message = entry.get('message') or {}
    if message.get('role', 'user') != 'user':
        return None
    content = message.get('content')
    if isinstance(content, str):
        text = content
    elif isinstance(content, list):
        if any(isinstance(b, dict) and b.get('type') == 'tool_result' for b in content):
            return None
        text = '\n'.join(str(b.get('text', '')) for b in content if isinstance(b, dict) and b.get('type') == 'text')
    else:
        return None
    return human_words(text)


def human_words(text: str) -> str | None:
    """The typed text without host notes and IDE context, or None for command output and notifications."""
    if re.search(r'<(?:local-command-std\w+|bash-std\w+|bash-input|user-prompt-submit-hook|task-notification)>', text):
        return None
    text = re.sub(r'<system-reminder>.*?</system-reminder>', ' ', text, flags=re.S)
    return IDE_TEXT.sub(' ', text)


def queued_text(entry: dict) -> str | None:
    """A message the owner typed while the agent was working (Putten, 2026-11-07). The host records it as a
    `queued_command` attachment with a human origin; subagent hand-backs (origin peer), task notifications, sidechain
    and meta entries never count."""
    data = entry.get('attachment') or {}
    origin = data.get('origin')
    if data.get('type') != 'queued_command' or entry.get('isSidechain') or entry.get('isMeta') \
            or data.get('commandMode') != 'prompt' or not isinstance(origin, dict) or origin.get('kind') != 'human':
        return None
    prompt = data.get('prompt')
    if isinstance(prompt, str):
        text = prompt
    elif isinstance(prompt, list):
        text = '\n'.join(str(b.get('text', '')) for b in prompt if isinstance(b, dict) and b.get('type') == 'text')
    else:
        return None
    return human_words(text)


def clean(text: str) -> str:
    """Case, spacing, curly quotes and trailing punctuation ignored."""
    text = text.replace('’', "'").replace('‘', "'").replace('“', '"').replace('”', '"')
    return re.sub(r'[\s.!?,;:]+$', '', ' '.join(text.split()).casefold())


def fresh_state() -> dict:
    return {'v': STATE_VERSION, 'offset': 0, 'head': '', 'mark': '', 'n': 0, 'lines': 0, 'parsed': 0,
            'active': False, 'rules': False, 'tasks': [], 'users': [], 'presented': {}, 'asks': {}, 'last_user': -1,
            'last_words': '', 'report_presented': {}, 'chat_presented': {}, 'paused_tasks': {},
            'shown_at': {}, 'shown_roots': {}, 'chat_roots': {}, 'user_tasks': {}, 'fingerprints': {}, 'replies': {}, 'task_roots': {},
            'small_shown': {}}


def set_task(state: dict, name: str, n: int, record: str = '', written: bool = False):
    """Make `name` the current task. A record the agent writes (`written`) for a task the owner paused is a handoff note:
    it does not make that task current again (Putten, 2026-11-07). The owner naming the task still does."""
    current = state['tasks'][-1][0] if state['tasks'] else None
    if written and name != current and name in state.get('paused_tasks', {}):
        return
    if name and not re.search(r'\.\w{1,4}$', name) and (not state['tasks'] or state['tasks'][-1][0] != name):
        state['tasks'].append([name, n])
    root = worktree(record) if name and record else None
    if root:  # where this task's records were written: a task spanning several repositories keeps one record set
        state.setdefault('task_roots', {})[name] = slash(root)


# Approval forms that lift a plan-only pause. Deny by default: the first real clause is one explicit
# approval, and every later clause must be on the short allow list below. A hold word anywhere wins.
_COURTESY = re.compile(r"^(?:yes|yep|yeah|ja|ok|okay|sure|great|good|fine|perfect|thanks|thank you|lgtm|nice|please|yes please|"
                       r"looks good|looks great|all good|yes to all|alright|cool)$")
_ASK = re.compile(r"^(?:(?:yes|yep|yeah|ja|ok|okay|sure|great|good|fine|perfect|thanks|lgtm|alright|cool|please|i)[\s,]+)*"
                  r"(?:(?:approved?|aproved|approvd|goedgekeurd)(?: (?:plan )?r\d+)?|approve (?:it|this|the plan)|"
                  r"(?:implement|build)(?: (?:it|this|the plan|the approved plan|(?:plan )?r\d+))?|go ahead|go for it|go|proceed|"
                  r"do it|start implementing|ga je gang|doe maar|"
                  r"(?:continue|resume)(?: (?:this task|the task|the approved task|implementing|the build|with the build|"
                  r"(?:docs/plans/)?\d{4}-\d{2}-\d{2}-[\w-]+/?))?)"
                  r"(?: now)?(?: please)?(?: now)?(?: (?:implement|build|do) it(?: now)?(?: please)?)?"
                  r"(?:$|\s+(?:and|then)\s+(?P<rest>.+))")
_LIMIT = re.compile(r"^(?:but\s+)?(?:do not|don't|dont|never|no)\s+(?:commit|push|merge|deploy|publish|release|tag)\w*"
                    r"(?:\s+(?:or|and|nor)\s+(?:commit|push|merge|deploy|publish|release|tag)\w*)*"
                    r"(?:\s+(?:it|this|anything|yet|until i(?: have)? review\w*(?: it)?))?$")
_ALLOWED_TAIL = re.compile(
    r"^(?:(?:plan )?r\d+(?: as written)?|as written|"
    r"(?:implement|build) (?:it|this|the plan|(?:plan )?r\d+)(?: now)?(?: please)?|go ahead|go|go for it|do it|"
    r"(?:check|verify|test) (?:if|that|whether) it works?(?:ed)?(?: (?:let me know|tell me)(?: when (?:it'?s |you'?re |also )?done)?)?|"
    r"(?:let me know|tell me|report back)(?: when (?:it'?s |you'?re |also )?done)?|run the tests|thanks|thank you)$")
_HOLD = re.compile(r"\b(?:not|no|never|nope|don'?t|do not|wait\w*|hold|first|yet|until|later|tomorrow|next|once|"
                   r"before|after|pending|except|unless|conditional\w*|revise|discuss\w*|think|sleep|kidding|nvm|"
                   r"scratch|standby|tight|await\w*|minute|moment|monday|tuesday|wednesday|thursday|friday|"
                   r"saturday|sunday|sprint|reject\w*|instead|cancel\w*|undo|stop\w*|pause\w*|"
                   r"niet|nog|nee|wacht\w*|morgen|eerst|later|stoppen)\b")


def control_intent(text: str) -> str | None:
    """Recognise direct stop/resume requests, not feature prose mentioning a Stop button.

    This intentionally small vocabulary is not a natural-language permission classifier.
    Other wording remains subject to the phase instructions and host permissions.
    Pass the raw message where possible: a question mark means it is not an instruction.
    """
    words = clean(text)
    if re.search(r"\b(?:do not|don't|dont|never)\s+(?:ever\s+)?(?:start\s+)?(?:implementing|implement|building|build|"
                 r"write (?:application )?code|edit (?:application )?files)(?:\s+(?:it|this|anything|the plan|plan r\d+))?"
                 r"(?:[.!?;,]|$|\s+(?:yet|until|now|but|and)\b)", words):
        return 'pause'
    if re.match(r"^(?:please\s+)?(?:stop|pause|cancel)(?:[.!?]|$|\s+(?:now|here|this task|the task|working|coding|implementation)\b)", words):
        return 'pause'
    # "wait, not yet" after a go puts the pause back (sixth review).
    if re.match(r"^(?:please\s+)?(?:wait|hold on|hold up|hold off|not yet|no wait|nog niet|wacht)\b", words):
        return 'pause'
    # An explicit approval that asks for the build lifts a plan-only pause (rc.32; deny-by-default in
    # rc.33 after three independent reviews). Questions, held approvals and feature prose never do.
    if '?' in text:
        return None
    clauses = [c.strip() for c in re.split(r"[.;:!,\n]+|\s[-\u2013\u2014]+\s|\bbut\b", words) if c.strip()]
    clauses = [c for c in clauses if not _COURTESY.match(c)]
    if not clauses or any(_HOLD.search(c) for c in clauses if not _LIMIT.match(c)):
        return None
    first = next((c for c in clauses if not _LIMIT.match(c)), None)
    found = _ASK.match(first) if first else None
    if not found:
        return None
    tail = ([found.group('rest')] if found.group('rest') else []) + [c for c in clauses if c is not first]
    if all(_LIMIT.match(c) or _ALLOWED_TAIL.match(c) for c in tail):
        return 'resume'
    return None


def add_words(state: dict, n: int, text: str, kind: str):
    """Retain the full answer, including restrictions; oversized answers cannot be clipped into consent."""
    raw = re.sub(r'\s*\(recommended\)\s*$', '', text, flags=re.I)
    words = clean(raw)
    state['users'].append([n, words[:16000], len(words) > 16000, kind])
    state['last_words'] = (state['last_words'] + ' . ' if state['last_user'] == n else '') + words[:4000]
    state['last_user'] = n
    task = state['tasks'][-1][0] if state['tasks'] else '*'
    state['user_tasks'][str(n)] = task
    intent = control_intent(raw)
    # One message can arrive in several parts (several answers). It resumes only when no part holds
    # the build back: a pause or a hold word in any part keeps or restores the pause.
    if intent is None and ('?' in raw or (_HOLD.search(words) and not _LIMIT.match(words))):
        intent = 'held'
    intents = state.setdefault('intents', {})
    rank = {'pause': 3, 'held': 2, 'resume': 1}
    if rank.get(intent, 0) > rank.get(intents.get(str(n)), 0) or str(n) not in intents:
        intents[str(n)] = intent
    lifted = state.setdefault('lifted', {})
    if intents[str(n)] in ('pause', 'held') and str(n) in lifted:
        for key, at in lifted.pop(str(n)).items():
            state['paused_tasks'][key] = at
    if intent == 'pause':
        state['paused_tasks'][task] = n
    elif intents[str(n)] == 'resume':
        before = {key: state['paused_tasks'].pop(key) for key in (task, '*') if key in state['paused_tasks']}
        if before:
            lifted.setdefault(str(n), {}).update(before)


def local_report_target(reference: str) -> str:
    """Resolve absolute local file URIs; remote/unknown schemes are not local report paths."""
    reference = reference.strip()
    if not URI_REFERENCE.match(reference):
        path = slash(reference).removeprefix('./').split('#', 1)[0]
        if not (is_absolute(path) or path.startswith('docs/plans/')) or '?' in path:
            return ''
    else:
        try:
            uri = urlsplit(reference)
            if uri.scheme.lower() != 'file' or uri.netloc.lower() not in ('', 'localhost') or uri.query:
                return ''
            path = slash(unquote(uri.path, errors='strict'))
        except (ValueError, UnicodeError):
            return ''
        if not path.startswith('/') or path.startswith('//'):
            return ''
        if re.match(r'^/[A-Za-z]:/', path):
            path = path[1:]  # file:///C:/... is a Windows drive path, not POSIX /C:/...
    found = TASK_REVIEW.search(path)
    if not found or found.end() != len(path) or re.search(r'[\x00-\x1f`<>"\']', path):
        return ''
    return path


def inline_link_end(text: str, start: int) -> int | None:
    """Find the end of one whole link payload, treating titles and angle targets as opaque."""
    i, depth, quote, angle = start, 1, '', False
    while i < len(text) and depth:
        char = text[i]
        if char == '\\' and i + 1 < len(text):
            i += 2
            continue
        if quote:
            if char == quote:
                quote = ''
        elif angle:
            if char == '>':
                angle = False
        elif char in ('"', "'"):
            quote = char
        elif char == '<':
            angle = True
        elif char == '(':
            depth += 1
        elif char == ')':
            depth -= 1
        i += 1
    return i if not depth else None


def presentation_references(text: str) -> list[str]:
    """Read paths/URIs atomically; consume balanced labels and opaque destinations without rewriting either."""
    references, normalized, i = [], slash(text), 0
    while i < len(text):
        uri = URI_REFERENCE.match(text, i)
        if uri:
            target = local_report_target(uri.group(0))
            if target:
                references.append(target)
            i = uri.end()
            continue
        if text[i] == '[':
            start, depth = i, 1
            i += 1
            while i < len(text) and depth:
                if text[i] == '\\' and i + 1 < len(text) and text[i + 1] in '\\[]':
                    i += 2
                    continue
                depth += (text[i] == '[') - (text[i] == ']')
                i += 1
            if depth:
                break
            after = i
            while after < len(text) and text[after].isspace():
                after += 1
            if after < len(text) and text[after] == ':':
                return []  # unsupported reference definitions: never infer their target from a label
            if after < len(text) and text[after] == '(':
                end = inline_link_end(text, after + 1)
                if end is None:
                    break  # no malformed suffix can leak into bare path parsing
                target = INLINE_TARGET.fullmatch(text[after + 1:end - 1])
                if target and not (start and text[start - 1] == '!'):
                    path = local_report_target(target.group(1) or target.group(2))
                    if path:
                        references.append(path)
                i = end
            continue
        reference = REPORT_REFERENCE.match(normalized, i)
        if reference:
            references.append(reference.group(0))
            i = reference.end()
        else:
            i += 1
    return references


def present_reports(state: dict, text: str, n: int, cwd: str):
    """Bind visible report references to the workspace actually named, not the edited target's copy."""
    for reference in presentation_references(text):
        found = TASK_REVIEW.search(reference)
        task, report = found.groups()
        prefix = reference[:found.start()]
        root = absolute(prefix, cwd) if prefix else Project(cwd).root
        reports = state['report_presented'].setdefault(task, {})
        reports.setdefault(report.lower(), n)
        state['presented'][task] = max(reports.values())
        shown = state['shown_at'].setdefault(task, {})
        shown[report.lower()] = (shown.get(report.lower(), []) + [n])[-50:]
        roots = state['shown_roots'].setdefault(task, {})
        roots[report.lower()] = (roots.get(report.lower(), []) + [[n, root]])[-50:]
    # Kit run 8: the plan was named as `reviews/plan-r2.html`, relative to the current task's folder. A bare name
    # counts for the current task only when that report exists in its folder.
    current = state['tasks'][-1][0] if state['tasks'] else None
    if not current:
        return
    home = state.get('task_roots', {}).get(current) or Project(cwd).root
    for name in BARE_REVIEW.findall(slash(text)):
        if home and (Path(home) / 'docs' / 'plans' / current / 'reviews' / name).is_file():
            reports = state['report_presented'].setdefault(current, {})
            reports.setdefault(name.lower(), n)
            state['presented'][current] = max(reports.values())
            shown = state['shown_at'].setdefault(current, {})
            shown[name.lower()] = (shown.get(name.lower(), []) + [n])[-50:]
            roots = state['shown_roots'].setdefault(current, {})
            roots[name.lower()] = (roots.get(name.lower(), []) + [[n, slash(home)]])[-50:]


def small_offers(state: dict, text: str, n: int, task: str | None):
    """H4: record each `Small change: <files> — <what changes>` line of a delivered assistant message or
    AskUserQuestion question as an offer of exactly that file set, under the task current when it was shown. An offer
    while no task is current counts for none; other path words in the message never count."""
    if not task:
        return
    for found in SMALL_OFFER_LINE.finditer(text):
        files = sorted({key(f) for f in small_files(found.group(2))})
        if files:
            rows = state.setdefault('small_shown', {}).setdefault(task, [])
            rows.append([n, files, small_description(found.group(2), offer=True)])
            del rows[:-20]


def owner_said(state: dict, n: int, text: str):
    """A real user message, typed at the prompt or while the agent was working."""
    for a, b in TASK_NAMED.findall(slash(text)):
        set_task(state, a or b, n)
    if '<command-name>' in text:
        state['last_user'] = n  # a slash command: its arguments are not consent
        args = re.search(r'<command-args>(.*?)</command-args>', text, re.S)
        state['last_words'] = clean(args.group(1))[:4000] if args else ''
    else:
        add_words(state, n, text, 'msg')


def feed(state: dict, entry: dict, raw: str, cwd: str):
    """Fold one transcript entry into the state."""
    n = state['n']
    state['n'] += 1
    content = (entry.get('message') or {}).get('content')
    if entry.get('type') == 'attachment':  # recorded by the host from this hook's own output, not by the agent
        hook = entry.get('attachment') or {}
        text = queued_text(entry)
        if text is not None:
            state['active'] = state['active'] or bool(TYPED.search(text))
            owner_said(state, n, text)
            return
        if hook.get('type') == 'hook_additional_context' and hook.get('hookEvent') in ('PostToolUse', 'UserPromptSubmit') \
                and not entry.get('isSidechain'):
            for mark, path, sha in FINGERPRINT.findall('\n'.join(str(line) for line in hook.get('content') or [])):
                found = TASK_REVIEW.fullmatch(path) or TASK_REVIEW.match(path)
                if not found:
                    continue
                rows = state['replies' if mark == REPLY_MARK else 'fingerprints'].setdefault(found.group(1), {})
                seen = rows.setdefault(found.group(2).lower(), [])
                if mark == REPLY_MARK:
                    # report_check reads only the first mark after an owner message. Hand-backs and notifications
                    # also fire UserPromptSubmit; their marks are dropped rather than allowed to push the answer's
                    # own mark out of a capped list. At most one mark per owner message, so no cap is needed.
                    if not seen or seen[-1][0] < state['last_user']:
                        seen.append([n, sha])
                elif not seen or seen[-1][1] != sha:  # a repeat of the latest hash adds nothing to report_check
                    rows[found.group(2).lower()] = (seen + [[n, sha]])[-50:]
        return
    if entry.get('type') == 'user':
        typed = content if isinstance(content, str) else '\n'.join(
            str(b.get('text', '')) for b in content or [] if isinstance(b, dict) and b.get('type') == 'text')
        typed = re.sub(r'<system-reminder>.*?</system-reminder>', ' ', typed, flags=re.S)
        state['active'] = state['active'] or (not entry.get('isMeta') and bool(TYPED.search(typed)))
        text = user_text(entry)
        if text is not None:
            owner_said(state, n, text)
            return
        result = entry.get('toolUseResult')
        if not entry.get('isSidechain') and not entry.get('isMeta') \
                and isinstance(result, dict) and isinstance(result.get('answers'), dict) and isinstance(content, list):
            for block in content:
                if not isinstance(block, dict) or block.get('type') != 'tool_result' or block.get('is_error'):
                    continue
                asked = state['asks'].pop(block.get('tool_use_id'), None)
                if asked is None:
                    continue
                at, origin, questions, *asked_task = asked
                for question, value in result['answers'].items():
                    if question in questions:
                        # A matched host answer establishes that this question was actually delivered.
                        # The question alone, a cancelled tool or thinking never presents/approves anything.
                        present_reports(state, question, at, origin)
                        small_offers(state, question, at, asked_task[0] if asked_task else None)
                        add_words(state, n, str(value), 'answer')
        return
    if entry.get('type') != 'assistant' or entry.get('isSidechain') or not isinstance(content, list):
        return
    # Only user-visible assistant text presents a plan. Writing its file or loading a
    # phase is not presentation. Repeating a link to the same immutable report is harmless.
    visible = '\n'.join(str(b.get('text', '')) for b in content
                        if isinstance(b, dict) and b.get('type') == 'text')
    origin = str(entry.get('cwd') or cwd)
    present_reports(state, visible, n, origin)
    small_offers(state, visible, n, state['tasks'][-1][0] if state['tasks'] else None)
    if re.search(r'\b(?:plan|proposal|implementation scope)\b', visible, re.I):
        for task in TASK_PATH.findall(slash(visible) + '/'):
            for a, b in REVISION.findall(visible):
                state['chat_presented'].setdefault(task, {}).setdefault(str(int(a or b)), n)
                roots = state['chat_roots'].setdefault(task, {})
                revision = str(int(a or b))
                roots[revision] = (roots.get(revision, []) + [[n, key(Project(origin).root)]])[-50:]
    for block in content:
        if not isinstance(block, dict) or block.get('type') != 'tool_use':
            continue
        name, data = block.get('name'), block.get('input') or {}
        current = state['tasks'][-1][0] if state['tasks'] else None
        if name == 'AskUserQuestion' and block.get('id'):
            questions = [q['question'] for q in data.get('questions', [])
                         if isinstance(q, dict) and isinstance(q.get('question'), str)]
            state['asks'][block['id']] = [n, origin, questions, current]
            state['asks'] = dict(list(state['asks'].items())[-200:])
        elif name == 'Skill':
            skill = str(data.get('skill', '')).split(':')[-1]
            state['active'] = state['active'] or skill == 'workflow' or skill in PHASES
            state['rules'] = state['rules'] or skill == 'rule-maker'
        elif name == 'Read' and not data.get('limit') and not data.get('offset') \
                and SKILL_READ.search(slash(str(data.get('file_path', '')))):
            state['active'] = True  # the router's fallback: a whole read loads the skill
        elif name in EDIT_TOOLS:
            found = TASK_PATH.search(slash(str(data.get('file_path') or data.get('notebook_path') or '')) + '/')
            if found:
                set_task(state, found.group(1), n, slash(str(data.get('file_path') or data.get('notebook_path') or '')),
                         written=True)
        elif name in SHELLS:
            for kind, where, _ in shell_writes(str(data.get('command', '')), str(entry.get('cwd') or cwd),
                                               name == 'PowerShell'):
                for task in TASK_PATH.findall(where + '/') if kind == 'path' else []:
                    set_task(state, task, n, where, written=True)


def digest(data: bytes) -> str:
    return hashlib.sha1(data).hexdigest()


def scan(path: Path, cwd: str) -> dict:
    """The transcript's state. Complete lines are folded in once and cached under the system temp folder (keyed by
    the transcript path, checked by the first and last 4 KB read), so each call parses only the new lines.
    Raises OSError or ValueError when the file cannot be read as a transcript."""
    data = path.read_bytes()
    cache = CACHE_DIR / (digest((str(path.resolve()) + '\n' + key(absolute(cwd, ''))).encode('utf-8')) + '.json')
    try:
        state = json.loads(cache.read_text(encoding='utf-8'))
        offset = state['offset']
        if state.get('v') != STATE_VERSION or offset > len(data) or state['head'] != digest(data[:4096]) \
                or state['mark'] != digest(data[max(0, offset - 4096):offset]):
            raise ValueError('stale')
    except (OSError, ValueError, KeyError, TypeError):
        state = fresh_state()
    end = data.rfind(b'\n') + 1

    def fold(chunk: bytes, into: dict):
        for line in chunk.split(b'\n'):
            if not line.strip():
                continue
            into['lines'] += 1
            if b'"tool_result"' in line and b'"answers"' not in line and b'"origin"' not in line:
                into['parsed'] += 1  # a tool's output: never consent, task or skill state
                into['n'] += 1
                continue
            text = line.decode('utf-8', errors='replace')
            try:
                entry = json.loads(text)
            except ValueError:
                continue
            if isinstance(entry, dict):
                into['parsed'] += 1
                feed(into, entry, text, cwd)

    if end > state['offset']:
        fold(data[state['offset']:end], state)
        state.update(offset=end, head=digest(data[:4096]), mark=digest(data[max(0, end - 4096):end]))
        try:
            CACHE_DIR.mkdir(exist_ok=True)
            temp = cache.with_suffix(f'.{os.getpid()}.tmp')
            temp.write_text(json.dumps(state), encoding='utf-8')
            os.replace(temp, cache)
            old = time.time() - CACHE_DAYS * 86400
            for stale in CACHE_DIR.glob('*.json'):
                if stale.stat().st_mtime < old:
                    stale.unlink()
        except OSError:
            pass  # the cache only saves time
    if end < len(data):  # a last line without a newline yet: judge it, do not cache it
        state = json.loads(json.dumps(state))
        fold(data[end:], state)
    if state['lines'] and not state['parsed']:
        raise ValueError('no JSON lines')
    return state


AGREEMENT = re.compile(r'^\s*[-*]\s*Agreement\b[^:\n]*:(.*)$', re.M)
AGREED = re.compile(r'\b(?:agreed|waived|legacy|not required)\b', re.I)
NOT_AGREED = re.compile(r'\b(?:not|never|no)\s+(?:yet\s+)?agreed\b|\bpending\b|\bproposed\b|\bawaiting\b', re.I)


def agreement_problem(text: str) -> str | None:
    """Gate one on the two-gate route (T2 of 2026-11-12, owner Q7b a). Only checkpoints with an `Approval (gate two)`
    line are checked; older single-gate tasks and legacy approvals are not."""
    approval = next(iter(APPROVAL.findall(text)), None)
    if not re.search(r'^\s*[-*]\s*Approval\s*\(gate two\)', text, re.M | re.I) or (
            approval and re.search(r'\blegacy\b', QUOTE.sub('', approval), re.I)):
        return None
    found = AGREEMENT.search(text)
    if not found:
        return 'has no `- Agreement (gate one):` line'
    words = QUOTE.sub('', found.group(1))  # the owner's quoted words never decide the state
    agreed, negative = AGREED.search(words), NOT_AGREED.search(words)
    # The first state word decides: "agreed ..., awaiting approval" is agreed; "not agreed yet" is not.
    if not agreed or (negative and negative.start() <= agreed.start()):
        return f'records the agreement as "{found.group(1).strip()[:80]}", which is not agreed, waived, legacy or not required'
    return None


def checkpoint(plan: str) -> str:
    # Any heading level and suffix: Altinstar used `### Current checkpoint (D4)` (E2 of 2026-11-12). The section ends
    # at the next heading of the same or a higher level.
    found = re.search(r'^(#{1,6})[ \t]+Current checkpoint\b[^\n]*$', plan, re.M | re.I)
    if not found:
        return plan
    end = re.compile(r'^#{1,%d}[ \t]' % len(found.group(1)), re.M).search(plan, found.end())
    return plan[found.end():end.start() if end else len(plan)]


def lightweight_files(text: str, root: str) -> set[str]:
    files = set()
    for found in LIGHT_LINE.finditer(text):
        listed = re.split(r'\s+(?:—|–|--|-)\s+', found.group(1), maxsplit=1)[0]
        for name in re.split(r'[,\s]+', listed):
            name = slash(name.strip('`"\'')).removeprefix('./')
            if name:
                files.add(key(relative(absolute(name, root), root) if is_absolute(name) else name))
    return files


COMMIT_WORD = re.compile(r'\bcommit\b')


def owner_asks_commit(words: str) -> bool:
    """The owner's latest words ask for a commit: a clause (split like the install guard's) that says "commit" and has
    no refusal word. "just commit" asks; "do not commit" and "looks good" do not."""
    return any(COMMIT_WORD.search(clause) and not INSTALL_REFUSAL.search(clause) for clause in CLAUSE.split(words))


def changed_files(root: str) -> list[str] | None:
    """Every path `git status` reports as changed in the worktree (staged, unstaged and untracked), or None."""
    import subprocess
    try:
        out = subprocess.run(['git', '--no-optional-locks', '-C', root, 'status', '--porcelain=v1', '-z',
                              '--untracked-files=all'],
                             capture_output=True, timeout=15)
    except (OSError, ValueError, subprocess.SubprocessError):
        return None
    if out.returncode:
        return None
    files, parts = [], out.stdout.decode('utf-8', errors='replace').split('\0')
    i = 0
    while i < len(parts):
        entry = parts[i]
        i += 1
        if len(entry) < 4:
            continue
        files.append(entry[3:])
        if entry[0] in 'RC' or entry[1] in 'RC':  # a rename or copy also names its source
            if i < len(parts) and parts[i]:
                files.append(parts[i])
            i += 1
    return files


def lightweight_commit_problem(target: tuple[str, str, str], state: dict, root: str, listed: set[str],
                               line: str = 'Lightweight edit') -> str | None:
    """Putten (2026-11-07): None when this `git commit` only commits the recorded lightweight files (plus task records)
    and the owner's latest message asks for it, otherwise why not. Push, amend and other git writes are never covered.
    `line` names the checkpoint line in the messages: the small-change route (H4) uses the same rule."""
    kind, _where, label = target
    if kind != 'git' or label != '`git commit`':
        return (f'its `- {line}:` line covers file edits and, when the owner asks for it, a `git commit` of '
                f'only those files; {label} still needs implementation approval')
    if not owner_asks_commit(state.get('last_words', '')):
        return (f'its `- {line}:` line allows a `git commit` of those files only when the owner\'s latest '
                'message asks for the commit. Ask the owner whether to commit; their reply is enough')
    files = changed_files(root)
    if files is None:
        return f'the gate could not list the changed files in {root} with `git status`'
    extra = [f for f in files if key(slash(f)) not in listed and not re.match(r'docs/plans/', slash(f), re.I)]
    if extra:
        shown = ', '.join(extra[:8]) + (' …' if len(extra) > 8 else '')
        return (f'these changed files are not on its `- {line}:` line: {shown}. If they belong to the '
                f'{line.lower()}, add them to that line; otherwise commit only the listed files or get implementation '
                'approval')
    return None


def report_file(folder: Path | None, name: str) -> Path | None:
    for path in ((folder / 'reviews' / name, folder / name) if folder else ()):
        if path.is_file():
            return path
    return None


def report_check(state: dict, task: str, name: str, answer: int, folder: Path | None) -> str:
    """'' when the owner's answer at `answer` covers the exact bytes shown: the fingerprint recorded before the report's
    last presentation before that answer, the same at the answer, and the same now. Otherwise why not."""
    report_key = name.lower()
    shown = [n for n in state.get('shown_at', {}).get(task, {}).get(report_key, []) if n < answer]
    if not shown:
        return f'{name} was not presented before that answer'
    roots = [root for n, root in state.get('shown_roots', {}).get(task, {}).get(report_key, []) if n == shown[-1]]
    if folder is None or not roots or key(roots[-1]) != key(slash(str(folder.parents[2]))):
        return f'{name} was presented for a different or unknown workspace; copied task records do not transfer approval'
    prints = state.get('fingerprints', {}).get(task, {}).get(report_key, [])
    before = [sha for n, sha in prints if n < shown[-1]]
    if not before:
        return f'no fingerprint of {name} was recorded before it was presented (an older session, another host or a report not read or written by a tool)'
    sha = before[-1]
    if any(other != sha for n, other in prints if shown[-1] < n < answer):
        return f'{name} changed after it was presented'
    after = min((n for n, *_ in state['users'] if n > answer), default=None)
    replies = [other for n, other in state.get('replies', {}).get(task, {}).get(report_key, []) if n > answer and (after is None or n < after)]
    if not replies:
        return f'no fingerprint of {name} was recorded with that answer'
    if replies[0] != sha:
        return f'{name} changed between its presentation and that answer'
    path = report_file(folder, name)
    try:
        if not path or hashlib.sha256(path.read_bytes()).hexdigest() != sha:
            return f'{name} is not the report that was approved (its content changed)'
    except OSError:
        return f'{name} cannot be read'
    return ''


def consent_at(quote: str, state: dict, task: str, reports: tuple[str, ...] = (), revisions: tuple[int, ...] = (),
               folder: Path | None = None, why: list | None = None, used: list | None = None) -> int | None:
    """Where the whole real answer came after this report was shown, for the exact report bytes (report_check), or None.
    This checks provenance, not semantic intent or the truth/completeness of the agent-written scope record."""
    start = presentation_start(quote, state, task, reports, revisions)
    if start is None:
        return None
    wanted = clean(quote)
    for n, words, truncated, _kind in state['users']:
        if n <= start or words != wanted or truncated:
            continue
        if revoked_after(state, task, n):
            if why is not None:
                why.append('a later real user message withdraws it')
            continue  # a later real withdrawal applies in this session too
        if not reports and NO_REPORT.search(quote):
            roots = state.get('chat_roots', {}).get(task, {})
            before = [[root for at, root in roots.get(str(rev), []) if at < n] for rev in revisions]
            if folder is None or any(not seen or seen[-1] != key(slash(str(folder.parents[2]))) for seen in before):
                continue
            return n  # the owner skipped the report: a chat-presented revision has no report bytes to compare
        names = reports or tuple(sorted((r for r, at in state.get('shown_at', {}).get(task, {}).items() if any(m < n for m in at)),
                                        key=lambda r: max(m for m in state['shown_at'][task][r] if m < n))[-1:])
        problems = [p for p in (report_check(state, task, name, n, folder) for name in names) if p] if names \
            else ['no report was presented before that answer']
        if not problems:
            if used is not None:
                used.extend(names)
            return n
        if why is not None:
            why.append(problems[0])
    return None


def presentation_start(quote: str, state: dict, task: str, reports: tuple[str, ...], revisions: tuple[int, ...]) -> int | None:
    shown = state.get('report_presented', {}).get(task, {})
    if reports:
        if any(name.lower() not in shown for name in reports):
            return None
        start = max(shown[name.lower()] for name in reports)
    elif NO_REPORT.search(quote):
        shown_chat = state.get('chat_presented', {}).get(task, {})
        times = [shown_chat.get(str(revision)) for revision in revisions]
        start = max(times) if times and all(n is not None for n in times) else None
    else:
        start = state['presented'].get(task)
    return start


# After an approval in an earlier session: words that withdraw it, and words that may narrow it (P1/P3 live tests).
REVOKED = re.compile(r"\b(?:revoke[sd]?|withdraw[sn]?|withdrawn|retract(?:ed|s)?)\b|\bnot approved\b|\bno longer approved\b"
                     r"|\bcancel (?:this|the) (?:task|approval|plan)\b|\bdo not (?:implement|continue)\b|\bdon't (?:implement|continue)\b")
RESTRICTS = re.compile(r"\b(?:but|except|only|without|nothing in|no changes? (?:to|in)|must not|never|leave)\b")
WAITING_APPROVAL = re.compile(r'\b(?:approval|implementation|decision)\s+(?:(?:is|remains?|still)\s+)*'
                              r'(?:pending|awaiting)\b|\b(?:pending|awaiting)\s+(?:approval|permission|decision)\b', re.I)
REFUSED_APPROVAL = re.compile(r'\b(?:not|never|no)\s+(?:yet\s+)?approved\b|\bunapproved\b', re.I)


def revoked_after(state: dict, task: str, after: int = -1) -> bool:
    """A withdrawal belongs to the task active/named at that actual user message."""
    return any(n > after and state.get('user_tasks', {}).get(str(n), '*') in (task, '*')
               and REVOKED.search(words) for n, words, _t, _k in state.get('users', []))


def earlier_consent(transcript: Path, quote: str, task: str, cwd: str, reports: tuple[str, ...] = (),
                    revisions: tuple[int, ...] = (), budget: float = 2.5, folder: Path | None = None,
                    recorded: frozenset = frozenset(), current: dict | None = None,
                    used: list | None = None) -> tuple[bool, str]:
    """The same test in sibling transcripts (earlier sessions of this project) that name this task's folder, and why an
    approval found there does not carry over: the report bytes differ from those presented and approved (report_check),
    a later revocation, a later stop without a continuation since, or a later restriction the checkpoint does not record."""
    if revoked_after(current or {}, task):
        return False, 'a real user message in the current session withdraws that approval'
    started = time.monotonic()
    try:
        siblings = sorted((p for p in transcript.parent.glob('*.jsonl') if p != transcript),
                          key=lambda p: p.stat().st_mtime, reverse=True)
    except OSError:
        return False, ''
    note = ''
    for sibling in siblings:
        if time.monotonic() - started > budget:
            break
        try:
            if task.encode('utf-8') not in sibling.read_bytes():
                continue
            state = scan(sibling, cwd)
        except (OSError, ValueError):
            continue
        why, names = [], []
        at = consent_at(quote, state, task, reports, revisions, folder, why, names)  # same task, report bytes and revision
        if at is None:
            note = note or (f'in an earlier session, {why[0]}' if why else '')
            continue
        later = [(n, words) for n, words, _t, _k in state['users'] if n > at
                 and state.get('user_tasks', {}).get(str(n), '*') in (task, '*')]
        for n, words in later:
            if REVOKED.search(words):
                return False, f'a later message in that session withdraws it ("{words[:120]}")'
        intents = state.get('intents', {})
        said = lambda n, w: intents[str(n)] if str(n) in intents else control_intent(w)
        stopped = [n for n, words in later if said(n, words) == 'pause']
        if stopped and not any(n > stopped[-1] and said(n, w) == 'resume' for n, w in later) \
                and not any(((current or {}).get('intents', {}).get(str(_n)) if str(_n) in (current or {}).get('intents', {})
                             else control_intent(w)) == 'resume'
                            and (current or {}).get('user_tasks', {}).get(str(_n), '*') in (task, '*')
                            for _n, w, _t, _k in (current or {}).get('users', [])):
            return False, 'that session was stopped after the approval and nobody has asked to continue since'
        for n, words in later:
            if RESTRICTS.search(words) and words not in recorded:
                return False, f'a later message in that session may restrict it and is not recorded ("{words[:120]}")'
        if used is not None:
            used.extend(names)
        return True, ''
    return False, note


def revision_numbers(text: str) -> list[int]:
    return [int(a or b) for a, b in REVISION.findall(text)]


class RecordFix(str):
    """A block caused by how the agent wrote the record, not by missing consent (Putten, 2026-11-07): the message says
    what to fix so the owner is not asked to approve again."""


RECORD_EXAMPLE = '`- Approval (gate two): r1 approved, <date>, no report: "<the owner\'s whole message>"`'


def unmatched_quote(quote: str, state: dict, task: str, reports: tuple[str, ...], revisions: tuple[int, ...]) -> str | None:
    """Why a quoted answer was not found, when the cause is known: the quote is only part of a real message given after
    the plan was shown (a record fix), or the matching message came before any presentation (missing consent)."""
    wanted, start = clean(quote), presentation_start(quote, state, task, reports, revisions)
    users = [(n, words) for n, words, truncated, _kind in state['users'] if not truncated]
    if start is not None:
        longer = [words for n, words in users if n > start and wanted and words.startswith(wanted) and words != wanted]
        if longer and not any(words == wanted for n, words in users if n > start):
            return RecordFix(f'quotes "{quote}", but that is only part of the owner\'s whole message after the plan was '
                             f'shown: "{longer[-1][:600]}". Quote that whole message, with all its conditions, then '
                             'retry; do not ask the owner again')
    exact = [n for n, words in users if words == wanted]
    if exact and (start is None or all(n <= start for n in exact)):
        shown = (f'names its report path docs/plans/{task}/reviews/<file>.html' if reports or not NO_REPORT.search(quote)
                 else f'contains the word plan, the task path docs/plans/{task} and the revision '
                      f'r{max(revisions) if revisions else "<N>"}')
        when = 'it came before the plan for this task was presented' if start is not None else \
            'the gate found no presentation of this task\'s plan in this session'
        return (f'quotes "{quote}", a real message from the owner, but {when}. A plan counts as shown when one '
                f'message of yours {shown} (markdown emphasis is fine). An answer given before that cannot approve '
                'it: present the plan that way, ask the owner, then quote their new answer')
    return None


def refuses(quotes: list[str]) -> bool:
    """A quoted answer that refuses or delays rather than approves."""
    return any(clean(q) in {'no', 'nope', 'not yet', 'not now', 'nee', 'niet', 'decline', 'hold off',
                            'pending', 'awaiting', 'proposed', 'not waived', 'not given'}
               or REVOKED.search(clean(q)) or WAITING_APPROVAL.search(q)
               or REFUSED_APPROVAL.search(q) for q in quotes)


SMALL_DASH = re.compile(r'(?:^|\s+)(?:—|–|--|-)(?:\s+|$)')


def small_files(rest: str) -> list[str]:
    """The comma-separated file part of a Small change line (before ` — `), each without quotes, backticks or `./`."""
    listed = SMALL_DASH.split(rest.strip(), maxsplit=1)[0]
    names = [slash(n.strip().strip('`"\'').strip()).removeprefix('./') for n in listed.split(',')]
    return [n for n in names if n]


# RR1: a short question to the owner after the description ("Approve?", "OK?", "Shall I proceed?"). Only these words,
# so a question that adds to the change ("Also delete the Cancel button?") stays part of the description.
SMALL_ASK = re.compile(r'(?<=[.!?])\s+(?:(?:approve|approved|ok|okay|go|ahead|proceed|shall|should|can|may|i|we|it|this|'
                       r'that|yes|fine|good|sound|sounds|agree|agreed|confirm|do|you|apply)\b[\s,]*){1,5}\?$', re.I)


def small_description(rest: str, offer: bool = False) -> str:
    """SP8: the `<what changes>` part of a Small change line (after ` — `), whitespace-normalized. RR1: surrounding
    `*`/`_` emphasis and end punctuation are dropped, and on an offer a short approval question after it; the words
    themselves must still match exactly."""
    parts = SMALL_DASH.split(rest.strip(), maxsplit=1)
    text = ' '.join(parts[1].split()) if len(parts) > 1 else ''
    if offer:
        text = SMALL_ASK.sub('', text)
    previous = None
    while text != previous:
        previous = text
        text = text.strip().rstrip('.!?').strip()
        if len(text) > 1 and text[0] in '*_' and text[-1] == text[0]:
            text = text.strip(text[0])
    return text


def small_change(text: str, root: str) -> tuple[list[str] | None, str]:
    """H4 (R11): the files of a valid `- Small change: <files> — <what changes>` checkpoint line, as lowercase
    repository-relative paths. (None, why) for an invalid line, which then counts as absent; (None, '') for none.
    Valid files are comma-separated, repository-relative, existing files: no folder, wildcard or `..`."""
    found = SMALL_LINE.search(text)
    if not found:
        return None, ''
    names = small_files(found.group(1))
    if not names:
        return None, 'it names no files'
    for name in names:
        if re.search(r'[*?\[\]{}]', name):
            return None, f'{name} is a wildcard'
        if is_absolute(name) or name.startswith('~') or '..' in name.split('/'):
            return None, f'{name} is not a repository-relative path'
        path = Path(root or '.') / name
        if name.endswith('/') or path.is_dir():
            return None, f'{name} is a folder'
        if not path.is_file():
            return None, f'{name} does not exist (a small change never adds a file)'
    return [key(n) for n in dict.fromkeys(names)], ''


def small_offer_start(state: dict, task: str, files: list[str], description: str) -> int | None:
    """The first offer, shown while this task was current, whose `Small change:` line lists exactly the same file set
    (order and spacing ignored) and the same description (SP8, whitespace-normalized) as the checkpoint line. A line
    edited later to add a file or change what changes needs a new offer."""
    wanted = sorted(set(files))
    starts = [n for n, offered, shown in state.get('small_shown', {}).get(task, [])
              if offered == wanted and shown == description]
    return min(starts) if starts else None


class Reconfirm(str):
    """SP2: the Approval line records a yes that this session cannot see (often one given in an earlier session). The
    refusal asks for a new yes on a separate Reconfirmed line, so the original quote stays as recorded."""


def small_yes_problem(quotes: list[str], state: dict, task: str, files: list[str], description: str) -> str | None:
    """Why these quotes are not each the whole of a real user message after this session's offer of the same file set
    and description, not withdrawn since, or None."""
    start = small_offer_start(state, task, files, description)
    if start is None:
        return (f'no message of yours in this session says "Small change:" with every listed file '
                f'({", ".join(files)}) and the same description as the checkpoint line ("{description[:160]}"), so '
                'the owner was not shown this change')
    for quote in quotes:
        wanted = clean(quote)
        if not any(n > start and words == wanted and not truncated and not revoked_after(state, task, n)
                   for n, words, truncated, _kind in state['users']):
            return (f'it quotes "{quote}", but no real user message after your "Small change:" message is exactly '
                    'those words and still stands')
    return None


def small_approval_problem(text: str, state: dict, task: str, files: list[str]) -> str | None:
    """Why the Approval line does not carry the owner's yes to this small change, or None. The yes must be the whole of
    a real user message after the offer, not withdrawn since; stop and pause handling stay in judge(). A later session
    cannot see the original yes: a `- Reconfirmed (gate two): small change, <date>: "<words>"` line that passes the
    same test stands in for it while the Approval line still says approved (SP2). Returns a Reconfirm then."""
    found = APPROVAL.search(text)
    if not found:
        return 'the checkpoint has no `- Approval:` line quoting the owner\'s yes'
    line = found.group(1).strip()
    marker = QUOTE.sub('', line)
    if NEGATIVE.search(marker) or not POSITIVE.search(marker):
        return f'the Approval line does not say outside the quotes that the small change is approved (`{line[:160]}`)'
    quotes = [a or b for a, b in QUOTE.findall(line) if re.search(r'\w', a or b)]
    if not quotes:
        return 'the Approval line quotes none of the owner\'s words'
    if refuses(quotes):
        return 'the Approval line quotes a refusal or delay'
    description = small_description(SMALL_LINE.search(text).group(1))
    why = small_yes_problem(quotes, state, task, files, description)
    if why is None:
        return None
    for again in RECONFIRMED.finditer(text):
        if not re.search(r'\bsmall change\b', QUOTE.sub('', again.group(1)), re.I):
            continue  # a report revision's confirmation, not this route's
        said = [a or b for a, b in QUOTE.findall(again.group(1)) if re.search(r'\w', a or b)]
        if said and not refuses(said) and small_yes_problem(said, state, task, files, description) is None:
            return None
    return Reconfirm(why)


def small_route_problem(target: tuple[str, str, str], files: list[str], text: str, state: dict, task: str,
                        root: str) -> str | None:
    """A write under a valid Small change line in a task without a plan report: only the listed existing files, and
    only after the owner's quoted yes. Git writes need the same yes; their files are separate path targets (H3)."""
    kind, where, label = target
    full = ('Switch to the full route: agree the behavior (workflow-clarify), then render and present the plan report '
            '(workflow-specify) and get it approved.')
    if (kind == 'path' and DELETING in label) or (kind == 'git' and label.startswith('`git rm`')):
        return f"workflow-axa: {label} is refused in task {task}: a small change never deletes a file. {full}"
    if (kind == 'path' and MOVING in label) or (kind == 'git' and label.startswith('`git mv`')):
        return f"workflow-axa: {label} is refused in task {task}: a small change never moves or renames a file. {full}"
    if kind == 'path' and (key(relative(where, root)) not in files or not Path(where).is_file()):
        return (f"workflow-axa: {label} is not covered by the current task {task}: its `- Small change:` line lists only "
                f"{', '.join(files)}, and a small change never adds a file. {full}")
    if kind not in ('path', 'git'):
        return (f"workflow-axa: {label} cannot be matched to the files of the `- Small change:` line of task {task}. "
                f"{full}")
    if kind == 'git' and not label.endswith(GIT_FILE_WRITE):
        # Commit, push and every other git write that is not a file write: the Lightweight-edit rule exactly. The
        # quoted yes alone never allows them; a commit also needs the owner's latest message to ask for it.
        light = lightweight_commit_problem(target, state, root, set(files), 'Small change')
        if light:
            return f"workflow-axa: {label} is not covered by the small change in task {task}: {light}."
    why = small_approval_problem(text, state, task, files)
    if isinstance(why, Reconfirm):
        return (f"workflow-axa: {label} needs the owner's yes to the small change in task {task}: {why}. If the owner "
                "approved it in an earlier session, show the same \"Small change:\" line again in one message and ask "
                "the owner, then add their whole new answer on a separate line: "
                "`- Reconfirmed (gate two): small change, <date>: \"<the owner's whole answer>\"`. Keep the "
                f"`- Approval:` line as it is: never change the original Approval quote. {full}")
    if why:
        return (f"workflow-axa: {label} needs the owner's yes to the small change in task {task}: {why}. Show the change "
                "in one message that says \"Small change:\" and names every listed file, ask the owner, then quote their "
                f"whole answer on the `- Approval:` line. {full}")
    return None


def small_change_without_report(state: dict, cwd: str) -> bool:
    """For plain_reply.py: the current task has a valid `- Small change:` line (the gate's own validation) and no plan
    report. An invalid line counts as absent here too."""
    if not state.get('tasks'):
        return False
    task = state['tasks'][-1][0]
    root = Project(cwd).root if cwd else ''
    plan = task_plan(task, state, root)
    try:
        text = checkpoint(plan.read_text(encoding='utf-8', errors='replace'))
    except OSError:
        return False
    return (small_change(text, root)[0] is not None and report_problem(plan.parent, text) is not None
            and not has_plan_report(plan.parent))


def has_plan_report(folder: Path) -> bool:
    """Whether the task folder or its reviews/ folder holds an .html report. The small route needs neither (D46)."""
    try:
        return any([*folder.glob('*.html'), *(folder / 'reviews').glob('*.html')])
    except OSError:
        return False


def approval_problem(text: str, state: dict, task: str, transcript: Path, cwd: str, folder: Path | None = None,
                     used: list | None = None) -> str | None:
    """Why the checkpoint's Approval line does not authorise implementation, or None. `used` collects the reports whose
    approved bytes were verified."""
    found = APPROVAL.search(text)
    if not found:
        return 'has no `- Approval:` line'
    line = found.group(1).strip()
    # The checkpoint status and the verbatim answer are separate fields. A later
    # acceptance gate can remain pending inside an implementation approval.
    marker = QUOTE.sub('', line)
    if NEGATIVE.search(marker):
        return f'does not approve a revision (`{line[:160]}`)'
    if not POSITIVE.search(marker):
        return RecordFix(f'does not say outside the quotes that a revision is approved (`{line[:160]}`). Write the '
                         f'status outside the quotes and the owner\'s words inside them, for example {RECORD_EXAMPLE}. '
                         'If the owner already approved after the plan was shown, do not ask the owner again')
    reports = tuple(re.findall(r'([\w.-]+\.html)\b', line))
    revisions = revision_numbers(line)
    other_revisions = [r for other in text.splitlines() if other.strip() != found.group(0).strip()
                       for r in revision_numbers(other)]
    if not revisions and not reports and any(NO_REPORT.search(a or b) for a, b in QUOTE.findall(line)):
        return RecordFix('names no revision. A plan shown in chat without a report is identified by the revision you '
                         f'showed; write it outside the quotes, for example {RECORD_EXAMPLE}. If the owner already '
                         'approved after the plan was shown, do not ask the owner again')
    if not revisions:
        # A legacy report can be the immutable scope identity. The complete real
        # answer must still follow that exact report's presentation below.
        marker = re.sub(r'[\w./-]+\.html\b', '', QUOTE.sub('', line))
        if not re.search(r'\blegacy\b', marker, re.I) or len(set(reports)) != 1:
            return ('has no explicit revision or reconciled legacy report identity; use resume-task to inspect '
                    'the original report, full user answer and current scope. Record legacy only when those '
                    'establish the same unchanged scope; otherwise ask through workflow-clarify/workflow-specify. '
                    'Do not invent a revision or edit or disable the hook')
        if other_revisions:
            return ('names only a legacy report but the checkpoint also names a revision; reconcile that scope '
                    'through resume-task, then clarify/specify only the unresolved part')
    elif other_revisions and max(other_revisions) > max(revisions):
        return f'approves r{max(revisions)}, but the checkpoint names revision r{max(other_revisions)}, which it does not approve'
    quotes = [a or b for a, b in QUOTE.findall(line) if re.search(r'\w', a or b)]
    if not quotes:
        return 'quotes none of the user\'s words; record their approval in double quotes, exactly as they wrote it'
    if refuses(quotes):
        return 'quotes an explicit refusal or delay, not implementation approval'
    recorded = frozenset(clean(a or b) for a, b in QUOTE.findall(text))
    notes = []

    def holds(quote: str) -> bool:
        why = []
        if consent_at(quote, state, task, reports, tuple(revisions), folder, why, used) is not None:
            return True
        notes.extend(why)
        ok, note = earlier_consent(transcript, quote, task, cwd, reports, tuple(revisions), folder=folder,
                                   recorded=recorded, current=state, used=used)
        if note:
            notes.append(note)
        return ok

    missing = [q for q in quotes if not holds(q)]
    if not missing:
        return None
    # The original quote stays as recorded; a later confirmation of the same revision and report sits on its own line.
    for again in RECONFIRMED.finditer(text):
        line_again = again.group(1)
        said = [a or b for a, b in QUOTE.findall(line_again) if re.search(r'\w', a or b)]
        if said and set(revision_numbers(line_again)) == set(revisions) and set(re.findall(r'([\w.-]+\.html)\b', line_again)) <= set(reports) \
                and all(holds(q) for q in said):
            return None
    report = f'docs/plans/{task}/reviews/{reports[0]}' if reports else f'the r{max(revisions)} plan' if revisions else 'the plan'
    fingerprint_gap = next((note for note in notes if 'no fingerprint of ' in note), None)
    if fingerprint_gap:
        return (f'cannot verify report evidence: {fingerprint_gap}. Check the active hook registration before '
                'requesting approval again: it must run phase_gate.py on PostToolUse and UserPromptSubmit from '
                'the same plugin root as PreToolUse. If the registration is old, missing or uncertain, restart '
                'Claude Code with one verified plugin source. Do not keep asking for the same approval in this '
                f'session. After recovery, read and present {report}, obtain the real answer, and preserve it on '
                'a separate Reconfirmed (gate two) line. Keep existing approval records and edits intact')
    known = unmatched_quote(missing[0], state, task, reports, tuple(revisions))
    if known:
        return known
    why = f' ({notes[0]})' if notes else ''
    return (f'quotes "{missing[0]}", but no user message given after this task\'s plan was presented contains those '
            f'words as the whole message or whole selected answer, in this session or an earlier one{why}. Keep all '
            'conditions; do not quote only its start. Approval comes from the user: present the plan, ask them, then quote '
            f'their exact words. To reconfirm a resumed task, keep this Approval line unchanged, read {report} whole by '
            'that path (this records its fingerprint), name that path in your reply, ask whether it still holds as approved, '
            'and record their exact answer on a separate '
            f'`- Reconfirmed (gate two): r{max(revisions) if revisions else "<N>"}, <date>: "<their words>"` line')


def report_problem(folder: Path, text: str) -> str | None:
    """Live rounds w2/w3: an Approval line was answered with no plan report. Approval needs the HTML report in
    task folder or `reviews/`, and the very report the Approval line names when it names one. An Approval line that
    records the user's "no report" needs none; approval_problem still checks its quoted words as consent."""
    found = APPROVAL.search(text)
    if found and any(NO_REPORT.search(a or b) for a, b in QUOTE.findall(found.group(1))):
        return None  # approval_problem still verifies the complete quoted user answer
    named = re.findall(r'([\w.-]+\.html)\b', found.group(1)) if found else []
    try:
        # The project's review folder, else reviews/ (VISUAL-REVIEW); loop w6: Altinstar keeps them in the task folder.
        reports = {p.name.lower() for p in [*folder.glob('*.html'), *(folder / 'reviews').glob('*.html')]}
    except OSError:
        reports = set()
    if not reports:
        return 'no plan report (no .html file in the task folder or its reviews/ folder)'
    missing = [name for name in named if name.lower() not in reports]
    if missing:
        return f'no plan report named {missing[0]} in the task folder, although the Approval line names it'
    return None


MANIFEST = re.compile(r'<script type="application/json" id="report-manifest">(.*?)</script>', re.S)


def report_write_paths(folder: Path, reports: list[str]) -> tuple[list[str], str | None]:
    """The explicit `write_paths` of these reports (render_report.py manifest), and the name of a report that lists
    them in an unreadable form (None when all are readable). Reports without a manifest add nothing."""
    allowed: list[str] = []
    for name in dict.fromkeys(reports):
        path = report_file(folder, name)
        try:
            found = MANIFEST.search(path.read_text(encoding='utf-8')) if path else None
            listed = json.loads(found.group(1)).get('write_paths') if found else None
        except (OSError, ValueError, AttributeError):
            listed = None
        if listed is None:
            continue
        if not isinstance(listed, list) or not all(isinstance(p, str) and p.strip() for p in listed):
            return allowed, name
        allowed += [p.strip() for p in listed]
    return allowed, None


def covers(allowed: list[str], where: str, root: str) -> bool:
    rel = key(relative(where, root))
    return any(rel == key(p.rstrip('/')) or (p.endswith('/') and rel.startswith(key(p))) for p in allowed)


def task_plan(task: str, state: dict, root: str) -> Path:
    """The task's PLAN.md in this worktree, or where the session wrote its records for a task that spans several
    repositories (Core plus client and module repos). A linked worktree of the same repository never borrows another
    worktree's records."""
    plan = Path(root or '.') / 'docs' / 'plans' / task / 'PLAN.md'
    home = state.get('task_roots', {}).get(task)
    if not plan.is_file() and home and common_dir(home) != common_dir(root):
        plan = Path(home) / 'docs' / 'plans' / task / 'PLAN.md'
    return plan


def approved_write_paths(task: str, state: dict, root: str, project: 'Project', transcript: Path) -> list[str]:
    """The write_paths a task's valid approval grants, or [] when it has no valid approval, no plan report, no
    write_paths or an unreadable list. Used only to narrow the task-switch stop (H3), never to grant a write."""
    plan = task_plan(task, state, root)
    try:
        text = checkpoint(plan.read_text(encoding='utf-8', errors='replace'))
    except OSError:
        return []
    used: list[str] = []
    if report_problem(plan.parent, text) or approval_problem(text, state, task, transcript, project.cwd, plan.parent,
                                                            used):
        return []
    allowed, bad = report_write_paths(plan.parent, used)
    return [] if bad else allowed


def scope_problem(target: tuple[str, str, str], root: str, folder: Path, reports: list[str]) -> str | None:
    """The approved report's explicit `write_paths` (render_report.py manifest) bound file writes; reports without
    them keep approval-only behaviour. Git and unresolved shell writes are not path-checked."""
    kind, where, label = target
    if kind != 'path' or not reports:
        return None
    allowed, bad = report_write_paths(folder, reports)
    if bad:
        return (f"workflow-axa: {label} cannot be checked against the approved plan: {bad} lists its write paths in "
                "an unreadable form. Re-render the plan with explicit `write_paths` and ask the owner to approve it.")
    if not allowed:
        return None  # an older report without write paths: approval-only, as before
    if covers(allowed, where, root):
        return None
    return (f"workflow-axa: {label} is outside the files the approved plan may change ({', '.join(allowed)}). If this "
            "work needs another file, or the owner's approval narrowed the scope, update the plan's write paths in a new "
            "revision, present it and get it approved before this edit. Task records and .artifacts stay writable.")


def authority_problem(target: tuple[str, str, str], state: dict, project: Project, transcript: Path) -> str | None:
    kind, where, label = target
    root = project.root_of(where) if where else project.root
    try:
        existing = sorted(p.parent.name for p in (Path(root or '.') / 'docs' / 'plans').glob('*/PLAN.md'))
    except OSError:
        existing = []
    if not state['tasks'] and existing:
        # P1 live test: a resumed session was told to start workflow-clarify although its task folder existed.
        shown = ', '.join(existing[:5]) + (' …' if len(existing) > 5 else '')
        return (f"workflow-axa: {label} cannot be matched to a task's approval yet: this session has not written a task "
                f"record or had a task folder named by the user. Existing tasks here: {shown}. If you are resuming one, "
                "update its records first (for example the checkpoint in docs/plans/<task>/PLAN.md); its recorded "
                "approval is then checked, including the owner's answer in earlier sessions. For new work, invoke "
                "workflow-clarify. Task records stay writable.")
    if not state['tasks']:
        return (f"workflow-axa: this session started /workflow, but it has not written or named a task folder "
                f"(docs/plans/<task>/), so there is no recorded approval for {label}. Invoke workflow-clarify now: it "
                "writes the task folder and, for a small settled change, asks both gates in one message. A reply like "
                "\"do it\" or \"push when done\" after an investigation starts clarify; it is not approval of an unseen "
                "plan. A lightweight edit (no behavior a user or caller can notice) needs a checkpoint line in the task's "
                "PLAN.md naming its files: `- Lightweight edit: <files> — <why>`.")
    task, changed_at = state['tasks'][-1]
    # The task that was current when the user last spoke. A handoff note to another task followed by a record of the
    # same task again is no switch (Putten, 2026-11-07).
    then = next((name for name, at in reversed(state['tasks']) if at <= state['last_user']), None)
    if len(state['tasks']) > 1 and changed_at > state['last_user'] and then != task:
        # H3 (Q17, D36): a note in another approved task's records does not stop a file write that only the earlier
        # task's approved write_paths cover. Both tasks need explicit write_paths; the write is then judged in full
        # against the earlier task below. Every other case keeps the stop.
        mine = approved_write_paths(then, state, root, project, transcript) if then and kind == 'path' else []
        theirs = approved_write_paths(task, state, root, project, transcript) if mine else []
        if mine and theirs and covers(mine, where, root) and not covers(theirs, where, root):
            task = then
        else:
            back = (f" If it belongs to {then}, the task current at the user's last message, write a record of {then} "
                    "(for example its checkpoint) and retry; no reply is needed then.") if then else ''
            return (f"workflow-axa: {label} was stopped because the current task changed to {task} after the user's "
                    f"last message (a write to docs/plans/{task}/ makes it current).{back} If it belongs to {task}, tell "
                    "the user and let them answer before you edit: any reply from them after the switch is enough, and "
                    "they need not type the task name.")
    plan = task_plan(task, state, root)
    try:
        text = checkpoint(plan.read_text(encoding='utf-8', errors='replace'))
    except OSError:
        return (f"workflow-axa: {label} needs the current task's approval, but the current task {task} has no PLAN.md in "
                f"this worktree ({root}). Record the task there, or name the task this change belongs to.")
    listed = lightweight_files(text, root)
    if kind == 'path' and key(relative(where, root)) in listed:
        return None
    light = None
    if listed and kind == 'git':
        light = lightweight_commit_problem(target, state, root, listed)
        if light is None:
            return None
    elif listed and kind == 'path':
        light = (f'its `- Lightweight edit:` line does not list {relative(where, root)}. If this file belongs to the '
                 'lightweight edit (no behavior a user or caller can notice), add it to that line; otherwise it needs '
                 'implementation approval')
    problem = report_problem(plan.parent, text)
    small, ignored = small_change(text, root)
    has_report = has_plan_report(plan.parent)
    # H4: a valid small change in a task folder with no .html report. D46: an Approval line naming a missing report
    # while another report exists keeps the full route.
    if problem and small is not None and not has_report:
        return small_route_problem(target, small, text, state, task, root)
    ignored = f" Its `- Small change:` line was ignored: {ignored}." if ignored else ''
    if small is not None and (has_report or not problem):
        # SP4: a valid line that the full route overrides. Say so, or the agent keeps quoting yeses for it.
        why = 'this task has a plan report' if has_report else \
            'its Approval line quotes "no report", which belongs to the full route'
        ignored = f" Its `- Small change:` line is ignored because {why}; use the full route or a new task."
    if problem and light:
        return (f"workflow-axa: {label} is not covered by the current task {task}: {light}. It has no implementation "
                f"approval either ({problem}).{ignored} Do not edit or disable the hook to bypass this block.")
    if problem:
        return (f"workflow-axa: {label} needs implementation approval, but the current task {task} has {problem}."
                f"{ignored} Approval needs the plan report from workflow-specify; if the owner declined a report, the "
                "quoted answer on the Approval line must contain their words for that (for example \"no report\"). For "
                "a change with no behavior a user or caller can notice, record a `- Lightweight edit: <files> — <why>` "
                "line in the checkpoint instead.")
    used: list[str] = []
    problem = approval_problem(text, state, task, transcript, project.cwd, plan.parent, used)
    if not problem:
        missing = agreement_problem(text)
        if missing:
            return (f"workflow-axa: {label} needs the recorded agreement (gate one) as well as the plan approval, but "
                    f"the current task {task} {missing}. Record the owner's agreement answer on the `- Agreement (gate "
                    "one):` line of its checkpoint (workflow-clarify step 4); a single answer that says yes to both "
                    "gates is recorded on both lines. Do not edit or disable the hook to bypass this block.")
        outside = scope_problem(target, root, plan.parent, used)
        return outside + ignored if outside else outside
    if isinstance(problem, RecordFix):
        return (f"workflow-axa: {label} is blocked by how the approval is recorded in the current task {task}: the "
                f"Approval line in {slash(str(plan))} {problem}. Fix the line with record.py set-line, then retry."
                f"{ignored} Do not edit or disable the hook to bypass this block.")
    return (f"workflow-axa: {label} needs implementation approval, and the current task {task} does not have it: the "
            f"Approval line in {slash(str(plan))} {problem}.{ignored} Loading a phase grants nothing by itself. Agree the behavior "
            "(workflow-clarify), approve the plan (workflow-specify), and record the user's answer in quotes on the "
            "`- Approval:` line before requesting the edit. For an older record, use resume-task to reconcile the "
            "original report, complete answer and scope; ask only where that evidence is insufficient. "
            "Do not edit or disable the hook to bypass this block. Task records, .artifacts and the report stay writable.")


# Report guides (round v3), unchanged

REPORT_GUIDES = ('codebase-map/TASK-REPORT.md', 'simple-english/SKILL.md', 'codebase-map/FLOWCHART-DESIGN.md')
UI_GUIDE = 'codebase-map/UI-FLOW.md'


def unread_report_guides(path: Path, reads: 'ReadEvidence | None' = None) -> list[str]:
    """Report guides not read whole in this context, when specify or deliver loaded (round v3: in all four
    worktrees the report was rendered before its writing rules were read). Reuses plain_reply's read test."""
    missing = reply_module().unread_files(path, (reads or ReadEvidence(str(path))).get())
    wanted = REPORT_GUIDES + (UI_GUIDE,)
    return sorted({rel for phase in ('workflow-specify', 'workflow-deliver') for rel in missing.get(phase, ())
                   if rel in wanted})


_REPLY = None


def reply_module():
    """plain_reply.py, loaded once per hook process."""
    global _REPLY
    if _REPLY is None:
        import importlib.util
        spec = importlib.util.spec_from_file_location('plain_reply', Path(__file__).with_name('plain_reply.py'))
        _REPLY = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(_REPLY)
    return _REPLY


class EvidenceUnavailable(Exception):
    """plain_reply.py could not be loaded or its scan failed on an unexpected entry. Callers skip the check, as
    they did before H2 when such an error reached main() (no new blocking for these tools)."""


class ReadEvidence:
    """One plain_reply.scan_reads pass per hook event, shared by the report-guide and declared-read checks.
    A read error is remembered and raised again to each caller: OSError/ValueError for a transcript that cannot be
    read (unchanged), EvidenceUnavailable for a broken plain_reply.py or a scan error."""

    def __init__(self, transcript: str):
        self.path, self.result, self.error = Path(transcript), None, None

    def get(self) -> dict:
        if self.result is None and self.error is None:
            try:
                # The gate's own checks keep the old rule: any whole read of a phase SKILL.md loads it (H2 rework).
                # Passing this module avoids loading phase_gate.py a second time inside plain_reply.
                self.result = reply_module().scan_reads(self.path, entry_required=False,
                                                        gate=sys.modules.get(__name__))
            except (OSError, ValueError) as error:
                self.error = error
            except (SyntaxError, ImportError, AttributeError, KeyError, TypeError) as error:
                self.error = EvidenceUnavailable(f'{type(error).__name__}: {error}')
        if self.error is not None:
            raise self.error
        return self.result


# Project-declared required reads (R10, P69). Optional `<!-- workflow-axa:required-read phases=specify,execute,deliver
# path="tests/README.md" -->` lines in the project root's AGENTS.md/CLAUDE.md name files that must be read whole in the
# current context before those phases start and before a report is validated or rendered while they are loaded.

DECLARED_PHASES = {'specify': 'workflow-specify', 'execute': 'workflow-execute', 'deliver': 'workflow-deliver'}
ROOT_RULES = ('AGENTS.md', 'CLAUDE.md')
# A declaration starts its own line (at most three spaces in), so indented code blocks and list-item examples are text.
DECLARATION_START = re.compile(r'^ {0,3}<!--\s*workflow-axa:required-read', re.M)
DECLARATION = re.compile(r'<!--\s*workflow-axa:required-read(.*?)-->', re.S)
DECLARATION_BODY = re.compile(r'\s+phases=([a-z]+(?:,[a-z]+)*)\s+path="([^"\r\n]+)"\s*')
FENCE = re.compile(r'^\s*(`{3,}|~{3,})')  # at any indentation, including inside list items


class DeclarationError(ValueError):
    """A root rule file that exists cannot be read, or one of its required-read declarations is malformed."""


def outside_fences(text: str) -> str:
    """The text without fenced code blocks and inline code spans, where declarations are only examples."""
    kept, fence = [], ''
    for line in text.splitlines():
        found = FENCE.match(line)
        if fence:
            if found and found.group(1)[0] == fence[0] and len(found.group(1)) >= len(fence) \
                    and not line.strip()[len(found.group(1)):].strip():
                fence = ''
            kept.append('')
            continue
        if found:
            fence = found.group(1)
            kept.append('')
            continue
        kept.append(re.sub(r'`[^`\n]*`', '', line))
    return '\n'.join(kept)


def declared_path(raw: str, root: str, source: str) -> str:
    """A literal project-root-relative path to an existing regular file, or DeclarationError. No globs, URLs,
    absolute, dot or linked parts."""
    parts = raw.split('/')
    if raw != raw.strip() or '\\' in raw or re.search(r'[*?\[\]{}]', raw) or re.match(r'^[A-Za-z][\w+.-]*:', raw) \
            or raw.startswith(('/', '~')) or any(part in ('', '.', '..') for part in parts):
        raise DeclarationError(f'{source} declares path="{raw}", which is not a literal project-root-relative path')
    try:
        base, target = Path(root).resolve(), Path(root).joinpath(*parts)
        linked = any(link.is_symlink() or getattr(link, 'is_junction', lambda: False)()
                     for link in (Path(root).joinpath(*parts[:end]) for end in range(1, len(parts) + 1)))
        resolved = target.resolve()
        exists, regular = target.exists(), target.is_file()
    except (OSError, RuntimeError, ValueError) as error:
        raise DeclarationError(f'{source} declares path="{raw}", which cannot be checked ({type(error).__name__})')
    if linked or (resolved != base and base not in resolved.parents):
        raise DeclarationError(f'{source} declares path="{raw}", which is a link or leaves the project root')
    if not exists:
        raise DeclarationError(f'{source} declares path="{raw}", but that declared file does not exist; correct '
                               'the declaration')
    if not regular:
        raise DeclarationError(f'{source} declares path="{raw}", which is not a regular file; correct the declaration')
    return raw


def declared_reads(root: str) -> dict[str, list[str]]:
    """{phase skill: [root-relative paths]}: the deduplicated union of the root AGENTS.md and CLAUDE.md declarations.
    Absent files declare nothing. Raises DeclarationError for an unreadable existing file or a malformed declaration."""
    out: dict[str, list[str]] = {}
    for name in ROOT_RULES if root else ():
        file = Path(root) / name
        if not os.path.lexists(file):
            continue
        try:
            text = outside_fences(file.read_text(encoding='utf-8-sig', errors='replace'))
        except OSError as error:
            raise DeclarationError(f'{name} exists at the project root but cannot be read ({type(error).__name__})')
        for start in DECLARATION_START.finditer(text):
            whole = DECLARATION.match(text, text.index('<!--', start.start()))
            body = DECLARATION_BODY.fullmatch(whole.group(1)) if whole else None
            phases = body.group(1).split(',') if body else []
            if not body or any(phase not in DECLARED_PHASES for phase in phases):
                shown = ' '.join((whole.group(0) if whole else text[start.start():start.start() + 120]).split())
                raise DeclarationError(f'{name} has a malformed required-read declaration ({shown[:160]}); use '
                                       '<!-- workflow-axa:required-read phases=specify,execute,deliver '
                                       'path="relative/file.md" --> with phases from specify, execute and deliver')
            relative_path = declared_path(body.group(2), root, name)
            for phase in phases:
                listed = out.setdefault(DECLARED_PHASES[phase], [])
                if relative_path not in listed:
                    listed.append(relative_path)
    return out


def read_identity(path: str) -> str:
    """Exact normalized absolute path; Windows drive paths compare without case."""
    full = absolute(path, '').rstrip('/')
    return full.lower() if re.match(r'^[A-Za-z]:', full) else full


def report_operation(command: str, powershell: bool) -> bool:
    """render_report.py asked to validate input or write a report (--validate-input/--output, or their argparse
    abbreviations). Help and the read-only --check stay outside."""
    for words, _redirects in segments(lex(split_bodies(command)[0], powershell)):
        names = [slash(word).rsplit('/', 1)[-1].lower() for word in words]
        if 'render_report.py' not in names:
            continue
        options = [word.split('=', 1)[0] for word in words[names.index('render_report.py') + 1:]]
        if any(option in ('-h', '--help') for option in options):
            continue
        if any(len(option) >= 3 and '--validate-input'.startswith(option) or
               len(option) >= 4 and '--output'.startswith(option) for option in options):
            return True
    return False


def required_read_problem(event: dict, reads: ReadEvidence | None = None) -> str | None:
    """Why an incoming phase Skill call or report operation must wait for declared reads, or None."""
    tool, data = event.get('tool_name'), event.get('tool_input') or {}
    incoming = str(data.get('skill', '')).lstrip('/').split(':')[-1] if tool == 'Skill' else ''
    phase = incoming if incoming in DECLARED_PHASES.values() else ''
    report = tool in SHELLS and report_operation(str(data.get('command', '')), tool == 'PowerShell')
    transcript = str(event.get('transcript_path') or '')
    if not (phase or report) or not transcript:
        return None  # not a supported boundary, or no transcript: enforcement unavailable (SETUP.md)
    reads = reads or ReadEvidence(transcript)
    root = Project(str(event.get('cwd') or '')).root
    recovery = ('Reading files, skills and rules and the record.py task-record helper stay available; do not edit '
                'or disable the hook to pass this check.')
    try:
        declared = declared_reads(root)
    except DeclarationError as error:
        if report:  # only a report operation while a declared phase could be loaded is affected
            try:
                if not set(DECLARED_PHASES.values()) & reads.get()['loaded']:
                    return None
            except (OSError, ValueError):
                pass
            except EvidenceUnavailable:
                return None  # plain_reply.py is broken: skip the check, as before H2
        what = phase or 'this report operation'
        return (f'workflow-axa: {what} cannot check the project\'s required reads: {error}. Fix the declaration in '
                f'the project root ({root}), then retry. {recovery}')
    if not declared:
        return None  # an undeclared project keeps its existing behavior
    try:
        evidence = reads.get()
    except EvidenceUnavailable:
        return None  # plain_reply.py is broken: skip the check, as before H2
    except (OSError, ValueError):
        return (f'workflow-axa: the session transcript ({transcript}) cannot be read, so the files this project '
                f'declares as required reads cannot be checked before {phase or "this report operation"}. Restore '
                f'transcript access, then retry. {recovery}')
    wanted = [phase] if phase else [name for name in DECLARED_PHASES.values() if name in evidence['loaded']]
    opened = {read_identity(path) for path in evidence['complete'] if is_absolute(path) or path.startswith('~')}
    missing = list(dict.fromkeys(rel for name in wanted for rel in declared.get(name, ())
                                 if read_identity(root.rstrip('/') + '/' + rel) not in opened))
    if not missing:
        return None
    before = phase or f'this report operation while {", ".join(n for n in wanted if declared.get(n))} is loaded'
    return (f'workflow-axa: this project\'s root AGENTS.md/CLAUDE.md requires a complete read in the current context '
            f'before {before}. Not yet read: {", ".join(missing)} (relative to {root}). Read each file whole with the '
            'Read tool by that path (no offset or limit), then retry. A failed, partial, truncated, subagent or '
            f'pre-compaction read does not count. {recovery}')


def deny(reason: str) -> int:
    print(json.dumps({'hookSpecificOutput': {'hookEventName': 'PreToolUse', 'permissionDecision': 'deny',
                                             'permissionDecisionReason': reason}}))
    return 0


def judge(event: dict) -> int:
    transcript = str(event.get('transcript_path') or '')
    reads = ReadEvidence(transcript) if transcript else None
    command = str((event.get('tool_input') or {}).get('command', '')) if event.get('tool_name') in SHELLS else ''
    if 'render_report.py' in command and '--help' not in command and transcript:
        try:
            unread = unread_report_guides(Path(transcript), reads)
        except (OSError, ValueError, AttributeError, EvidenceUnavailable):
            unread = []
        if unread:
            return deny("workflow-axa: read these whole before rendering the report, because they set its content and "
                        f"wording: {', '.join(unread)} (under the workflow-axa skills folder). Then render.")
    problem = required_read_problem(event, reads)
    if problem:
        return deny(problem)
    project = Project(str(event.get('cwd') or ''))
    all_targets = targets_of(event)
    direct_records = [t for t in all_targets
                      if event.get('tool_name') in ('Write', 'Edit', 'MultiEdit') and t[0] == 'path'
                      and project.contains(t[1])
                      and re.fullmatch(r'docs/plans/[^/]+/(?:PLAN|TODO|FINDINGS|DECISIONS)\.md',
                                       relative(t[1], project.root_of(t[1])), re.I)]
    if direct_records and transcript:
        try:
            active = scan(Path(transcript), project.cwd)['active']
        except (OSError, ValueError):
            return deny('workflow-axa: the supplied session transcript cannot be read. Direct canonical task-record '
                        'edits remain blocked. Restore transcript access or use the existing record.py helper '
                        'with normal tool permissions; do not bypass a denied helper command.')
        if active:
            return deny(f'workflow-axa: use python -X utf8 -I "{RECORD_TOOL}" for canonical task records. '
                        'Use new for initial creation in an existing directory, or append, batch, set-line or '
                        'replace-section for updates. The helper stays available for planning and stopped-task '
                        'handoff, subject to normal permissions. Do not use Write/Edit/MultiEdit for these records.')
    bulk = bulk_delete(event, all_targets, project)
    targets = [t for t in all_targets
               if t[0] != 'path' or (project.contains(t[1]) and not project.is_record(t[1]))]
    if (not targets and not bulk) or not transcript:
        return 0  # nothing gated, or no transcript to judge by (documented in SETUP.md)
    path = Path(transcript)
    try:
        state = scan(path, project.cwd)
    except FileNotFoundError:
        return 0
    except (OSError, ValueError):
        if event.get('tool_name') in EDIT_TOOLS or any(t[0] == 'git' for t in targets):
            return deny(f"workflow-axa: the session transcript ({transcript}) could not be read, so the phase gate cannot "
                        f"check the current task's approval for {targets[0][2]}. Project files and git writes stay "
                        "blocked until it can be read; task records, .artifacts and files outside the project stay "
                        "writable.")
        return 0
    if not state['active']:
        return 0
    registered = next((arg.split('=', 1)[1] for arg in sys.argv[1:]
                       if arg.startswith('--hook-protocol=')), None)
    if registered != HOOK_PROTOCOL:
        return deny(f'workflow-axa: incompatible hook registration protocol {registered}; this script requires '
                    f'{HOOK_PROTOCOL}. Restart Claude Code with one complete verified plugin version. '
                    'Do not retry approval in this mixed session or disable the gate. Read-only work and '
                    'task records remain available.')
    if bulk:
        return deny(bulk)
    task = state['tasks'][-1][0] if state['tasks'] else '*'
    if task in state.get('paused_tasks', {}) or '*' in state.get('paused_tasks', {}):
        return deny("workflow-axa: the user stopped, paused or cancelled this task. Do not start another write. "
                    "Record the handoff only; implementation needs an explicit continuation request.")
    if state['rules']:
        targets = [t for t in targets if t[0] != 'path' or not RULE_FILE.search(t[1])]  # D20: rule-maker writes rules
    for target in targets:
        if target[0] == 'refused':
            return deny(target[2])
        if target[0] == 'ambiguous':
            return deny(f"workflow-axa: {target[2]} is relative to a folder set by a shell variable the gate cannot "
                        "resolve, so it cannot tell whether this is a task record. Use an explicit path (or set the "
                        "variable in the same command) and retry.")
        problem = authority_problem(target, state, project, path)
        if problem:
            about_approval = 'approval' in problem and 'current task changed' not in problem
            return deny(problem + (worktree_copy_note(target, state, project) if about_approval else ''))
    return 0


def worktree_copy_note(target: tuple[str, str, str], state: dict, project) -> str:
    """T5 of 2026-11-12 (E4, E10, E11): in a linked worktree, say when its copy of the task's PLAN.md differs from the
    main checkout's. The refusal itself is unchanged: a linked worktree never borrows another worktree's records."""
    root = project.root_of(target[1]) if target[1] else project.root
    if not root or not state['tasks']:
        return ''
    try:
        found = re.match(r'\s*gitdir:\s*(.+?)\s*$', (Path(root) / '.git').read_text(encoding='utf-8', errors='replace'))
    except OSError:
        return ''  # no .git file: the main checkout or no repository
    parts = re.split(r'/\.git/worktrees/', absolute(found.group(1), root), maxsplit=1) if found else []
    if len(parts) != 2:
        return ''
    task = state['tasks'][-1][0]
    mine, theirs = (Path(r) / 'docs' / 'plans' / task / 'PLAN.md' for r in (root, parts[0]))
    try:
        if not theirs.is_file() or (mine.is_file() and mine.read_bytes() == theirs.read_bytes()):
            return ''
    except OSError:
        return ''
    return (f" Note: this linked worktree's copy {slash(str(mine))} differs from the main checkout's copy at "
            f"{slash(str(theirs))}. The gate reads approval only from this worktree's own records, so an approval "
            "recorded in the main checkout does not count here: work in the main checkout, or record and present the "
            "approval in this worktree.")


INSTALL = re.compile(r'(?:^|[;&|(]\s*)(?:npm\s+(?:i|install|ci|add)\b|yarn\s+(?:add|install|dlx)\b'
                     r'|pnpm\s+(?:add|install|i|dlx)\b|composer\s+(?:install|require|update)\b'
                     r'|(?:pip3?|(?:python3?|py)(?:\s+-3[\d.]*)?\s+-m\s+pip|uv\s+pip)\s+install\b)', re.I | re.M)
NPX = re.compile(r'(?:^|[;&|(]\s*)(?:npx|bunx|npm\s+exec)\s+(?:-{1,2}[\w-]*\s+)*([@\w./-]+)', re.I | re.M)
INSTALL_WORD = re.compile(r'\b(?:install\w*|npm ci|npx|bunx|dlx|npm exec)\b')
INSTALL_REFUSAL = re.compile(r"(?<!\w)(?:no|not|don'?t|never|niet|nee)(?!\w)")
CLAUSE = re.compile(r'[.!?;,]+(?:\s|$)|\s+but\s+')


def bin_name(spec: str) -> str:
    """The command an npx-style package spec runs: `@scope/pkg@1.2` runs `pkg`, `vitest@latest` runs `vitest`."""
    spec = re.sub(r'(?<=.)@[^/@]*$', '', spec)
    return spec.rsplit('/', 1)[-1] or spec


def allows_install(words: str) -> bool:
    """The user's latest words allow installing: a clause (split at sentence punctuation, commas and "but") that
    names installing and has no refusal word. "install it, no need to ask" allows; "do not install" does not."""
    return any(INSTALL_WORD.search(clause) and not INSTALL_REFUSAL.search(clause) for clause in CLAUSE.split(words))


def install_problem(event: dict) -> str | None:
    """Loop w7 (Altinstar): `npx vitest` without node_modules downloaded vitest from the registry. In a session the
    phase gate is active for, installs and downloading npx need the user's latest words to allow installing. The
    words come from the same extraction as consent: real user messages, AskUserQuestion answers and slash-command
    arguments; never tool output, task notifications or system notes."""
    if event.get('tool_name') not in SHELLS or not event.get('transcript_path'):
        return None
    command = str((event.get('tool_input') or {}).get('command', ''))
    found = INSTALL.search(command)
    if not found:
        tool = NPX.search(command)
        if not tool:
            return None
        cwd = Path(str(event.get('cwd') or '.'))
        name = bin_name(tool.group(1))
        targets = [cwd] + [cwd / t for t in re.findall(r'\bcd\s+["\']?([^"\'\s;&|]+)', command)]
        for folder in targets:
            for parent in [folder, *folder.parents]:
                if any((parent / 'node_modules' / '.bin' / (name + ext)).exists() for ext in ('', '.cmd')):
                    return None
        what = f'`{tool.group(0).strip(" ;&|(")}` ({name} is not installed in this project, so it would be downloaded)'
    else:
        what = f'`{found.group(0).strip(" ;&|(")}`'
    try:
        state = scan(Path(str(event['transcript_path'])), Project(str(event.get('cwd') or '')).cwd)
    except (OSError, ValueError):
        return None  # judge() handles an unreadable transcript for the writes it gates
    if not state['active'] or allows_install(state['last_words']):
        return None
    return (f"workflow-axa: {what} installs packages or contacts a package registry. Never install on your own: ask "
            "the owner with the plan, or use what the project or main checkout already has (TASK-FOLDER: a fresh "
            "worktree has no installed dependencies).")


STYLE_FILE = re.compile(r'\.(?:css|scss|sass|less|styl)$', re.I)
STYLE_RULE = re.compile(r'^[^{}\n]*\{[^}\n:]*:[^}\n]*\}|^\s*[\w-]+\s*:\s*[^;{}\n]+;\s*$', re.M)
NOTE_LIMIT = 4_000_000  # characters of old plus new text the style note reads
STYLE_CUES = ('inline-or-runtime-style', 'style-injection-or-css-in-js')


def ui_cues() -> dict[str, re.Pattern]:
    """The review cues of ui-design's review_ui_diff.py, loaded from this package; none when it is missing."""
    script = Path(__file__).resolve().parents[1] / 'skills' / 'ui-design' / 'scripts' / 'review_ui_diff.py'
    try:
        spec = importlib.util.spec_from_file_location('workflow_axa_review_ui_diff', script)
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module  # its dataclasses look their module up while it loads
        try:
            spec.loader.exec_module(module)
        finally:
            sys.modules.pop(spec.name, None)
        return dict(module.COMPILED)
    except (OSError, ImportError, AttributeError, SyntaxError):
        return {}


def edit_texts(event: dict, path: str) -> tuple[str, str]:
    """The text an edit replaces and the text it writes (for Write: the committed file and the new content)."""
    data = event.get('tool_input') or {}
    pairs = []
    if event.get('tool_name') == 'Edit':
        pairs = [(str(data.get('old_string') or ''), str(data.get('new_string') or ''))]
    elif event.get('tool_name') == 'MultiEdit':
        pairs = [(str(e.get('old_string') or ''), str(e.get('new_string') or ''))
                 for e in data.get('edits') or [] if isinstance(e, dict)]
    elif event.get('tool_name') == 'Write':
        old = ''
        root = worktree(path)
        if root:
            try:
                done = subprocess.run(['git', '-C', root, 'show', f'HEAD:{relative(path, root)}'], capture_output=True,
                                      text=True, encoding='utf-8', errors='replace', timeout=2)
                old = done.stdout if done.returncode == 0 else ''
            except (OSError, subprocess.SubprocessError):
                old = ''
        pairs = [(old, str(data.get('content') or ''))]
    return '\n'.join(o for o, _ in pairs), '\n'.join(n for _, n in pairs)


def markup_names(text: str) -> set[str]:
    """Tag names and class names in markup, to tell a new element or class from reworded text."""
    names = {f'<{m.lower()}' for m in re.findall(r'<\s*([A-Za-z][\w.:-]*)', text)}
    for value in re.findall(r"""\b(?:class|className)\s*=\s*["'{]([^"'}]*)""", text):
        names.update(f'.{c}' for c in value.split())
    return names


def style_notes(event: dict, project, cwd: str) -> list[str]:
    """T4 of 2026-11-12 (owner Q8 a): a note, never a refusal, when an edit adds styling to an application file, or a
    new tag or class to a file of the task's small change. "Adds" means more matches after the edit than before."""
    data = event.get('tool_input') or {}
    if not isinstance(data, dict) or not data.get('file_path') or not event.get('transcript_path'):
        return []
    path = absolute(str(data['file_path']), cwd)
    if not project.contains(path) or project.is_record(path):
        return []
    root = project.root_of(path)
    rel = relative(path, root)
    low = rel.lower()
    if low.endswith(('.md', '.markdown')) or re.search(r'(?:^|/)(?:tests?|__tests__)/', low) \
            or re.search(r'\.(?:test|spec)\.', low):
        return []
    state = scan(Path(str(event['transcript_path'])), cwd)  # first: sessions without the workflow pay nothing more
    if not state['active']:
        return []
    old, new = edit_texts(event, path)
    if old == new or len(old) + len(new) > NOTE_LIMIT:
        return []  # very large texts: no note, rather than a PostToolUse timeout that would drop the fingerprints
    cues = ui_cues()
    styling = [code for code in STYLE_CUES if code in cues
               and len(cues[code].findall(new)) > len(cues[code].findall(old))]
    if STYLE_FILE.search(low) and len(STYLE_RULE.findall(new)) > len(STYLE_RULE.findall(old)):
        styling.insert(0, 'stylesheet rule')
    added_markup = markup_names(new) - markup_names(old)
    if not styling and not added_markup:
        return []
    notes = []
    if styling:
        notes.append(f'workflow-axa note: the edit adds styling to {rel} ({", ".join(dict.fromkeys(styling))}). '
                     'DESIGN.md rule 4: reuse an existing class and name it, or ask the owner "I couldn\'t find a '
                     'matching style for [element]. Is there an existing element I should mimic?". This note does '
                     'not block the edit.')
    if added_markup and state['tasks']:
        plan = task_plan(state['tasks'][-1][0], state, root)
        try:
            files, _ = small_change(checkpoint(plan.read_text(encoding='utf-8', errors='replace')), root)
        except OSError:
            files = None
        if files and key(rel) in files:
            notes.append(f'workflow-axa note: the edit adds {", ".join(sorted(added_markup))} to {rel}, a file of this '
                         "task's small change. A small change only rewords, reorders or hides existing elements; a "
                         'new element or class needs the full route. This note does not block the edit.')
    return notes


def fingerprints(event: dict) -> int:
    """Leave report fingerprints in the transcript as hook context (the host records it; the agent cannot write it):
    after a tool call that names a task report (read, written or rendered), and when the owner answers (a typed message
    or an AskUserQuestion answer) for the reports this session has presented for its current task."""
    kind, cwd = event.get('hook_event_name'), str(event.get('cwd') or '')
    project = Project(cwd)
    lines = []
    if kind == 'PostToolUse' and event.get('tool_name') != 'AskUserQuestion':
        data = event.get('tool_input') or {}
        named = [absolute(str(data.get('file_path')), cwd)] if isinstance(data, dict) and data.get('file_path') else []
        if isinstance(data, dict) and event.get('tool_name') in SHELLS:
            named.extend(shell_report_paths(str(data.get('command') or ''), cwd,
                                            event.get('tool_name') == 'PowerShell'))
        for candidate in named:
            path = Path(candidate)
            report = TASK_REVIEW.search(slash(str(path)))
            if report and path.is_file() and project.contains(slash(str(path))):
                lines.append((SHOWN_MARK, f'docs/plans/{report.group(1)}/{"reviews/" if "/reviews/" in slash(str(path)) else ""}'
                              f'{path.name}', path))
    elif kind in ('UserPromptSubmit', 'PostToolUse') and event.get('transcript_path'):
        state = scan(Path(str(event['transcript_path'])), cwd)
        if not state['active'] or not state['tasks']:
            return 0
        task = state['tasks'][-1][0]
        for name in state.get('shown_at', {}).get(task, {}):
            roots = state.get('shown_roots', {}).get(task, {}).get(name, [])
            if not roots or not project.contains(roots[-1][1]):
                continue
            folder = Path(roots[-1][1]) / 'docs' / 'plans' / task
            path = report_file(folder, name)
            if path:
                lines.append((REPLY_MARK, f'docs/plans/{task}/{"reviews/" if path.parent.name == "reviews" else ""}{path.name}', path))
    out = []
    for mark, shown, path in lines:
        try:
            out.append(f'{mark}: {shown} sha256={hashlib.sha256(path.read_bytes()).hexdigest()}')
        except OSError:
            continue
    if kind == 'PostToolUse' and event.get('tool_name') in ('Edit', 'Write', 'MultiEdit'):
        try:
            out.extend(style_notes(event, project, cwd))
        except Exception:  # a missing note never costs the report fingerprints collected above
            pass
    if out:
        print(json.dumps({'hookSpecificOutput': {'hookEventName': kind, 'additionalContext': '\n'.join(dict.fromkeys(out))}}))
    return 0


def main() -> int:
    try:
        event = json.load(sys.stdin)
    except ValueError:
        return 0
    if not isinstance(event, dict):
        return 0
    if event.get('hook_event_name') in ('PostToolUse', 'UserPromptSubmit'):
        try:
            return fingerprints(event)
        except Exception:  # a fingerprint that cannot be recorded only means a later reconfirmation
            return 0
    try:
        problem = install_problem(event)
        if problem:
            return deny(problem)
        return judge(event)
    except Exception as error:  # a bug here must not open the gate for the edit tools
        if event.get('tool_name') in EDIT_TOOLS:
            return deny(f"workflow-axa: the phase gate failed ({type(error).__name__}: {error}), so it cannot check this "
                        "edit. Report this to the workflow-axa owner; task records can still be written with record.py.")
        return 0


if __name__ == '__main__':
    sys.exit(main())
