"""PreToolUse hook: after /workflow, code edits and git writes need the current task's recorded approval.

Hooqd retro (2026-11-03): after "Let's do that, push when done" the agent edited code and pushed with no task folder.
The audit of 2026-11-03 (task 2026-11-03-audit-hardening, E1-E8, D1) then found that any phase name in the transcript
counted as permission, chat text granted the lightweight route, and many shell writes slipped past. The rules now:

- The gate is active once the session typed or loaded the workflow router or a phase skill. Loading a phase grants
  nothing by itself.
- Each written target is judged on its own, with `..` resolved and after any `cd`. Free: task records and output
  (`docs/plans/**`, `.artifacts/**` of the target's worktree), anything outside the project (the cwd's worktree and
  the other worktrees of the same repository), and rule files while rule-maker is loaded.
- Every other write, and every git write, needs the current task: the `docs/plans/<task>/` the session last wrote
  records in or the user named, looked up inside the target's git worktree. Its PLAN.md checkpoint must either list
  the file on a `- Lightweight edit: <files> — <why>` line, or carry an `- Approval:` line that approves, waives or
  reconciles one legacy report (never "not approved", "proposed" or "pending") and quotes in double quotes words that
  match the complete real user answer after the named report was shown: this transcript, or a sibling `*.jsonl` in the same folder (an earlier
  session of the project, so a resumed task keeps its approval). A real user message is one the user typed, or the
  choice they picked in AskUserQuestion; tool output, meta entries, subagent prompts and hand-backs never count.
- A transcript that exists but cannot be read blocks the explicit edit tools. No transcript path: allowed.
- Install guard: in a session the gate is active for, package installs and npx-style downloads need the user's
  latest words (message, AskUserQuestion answer or slash-command arguments) to allow installing.

Shell commands are read best effort; command-text filtering is advice, not a security boundary (workflow/SETUP.md,
"What the hooks enforce"). Exits 0 on bad input.
"""
from __future__ import annotations

import hashlib
import json
import os
import posixpath
import re
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
TASK_PATH = re.compile(r'docs/plans/([A-Za-z0-9][\w.-]*?)(?=/|$|[\s"\'`),;])')
TASK_NAMED = re.compile(r'docs/plans/([A-Za-z0-9][\w.-]*?)(?=/|$|[\s"\'`),;.])|(?<![\w/-])(\d{4}-\d{2}-\d{2}-[a-z0-9][a-z0-9-]*)')
NULL_TARGETS = ('/dev/null', '/dev/stdout', '/dev/stderr', 'nul', '$null')

# Approval line (TASK-FOLDER.md checkpoint): `- Approval (gate two): <approved/waived/legacy/not approved; ...>`.
APPROVAL = re.compile(r'^\s*[-*]\s*Approval\b[^:\n]*:(.*)$', re.M)
# A resumed task's later confirmation of the same revision: `- Reconfirmed (gate two): r1, <date>: "<words>"`.
RECONFIRMED = re.compile(r'^\s*[-*]\s*Reconfirmed\b[^:\n]*:(.*)$', re.M)
LIGHT_LINE = re.compile(r'^\s*[-*]\s*Lightweight edit:\s*(.+)$', re.M | re.I)
NEGATIVE = re.compile(r'\b(?:not|never|no)\s+(?:yet\s+)?(?:approved|waived|given)\b|\bunapproved\b|\bproposed\b'
                      r'|\bpending\b|\bawaiting\b|\brevoked\b|\bwithdrawn\b', re.I)
POSITIVE = re.compile(r'\b(?:approved|waived|legacy)\b', re.I)
# Uppercase R identifiers belong to requirements unless explicitly introduced as a revision.
# Keep lowercase rN checkpoint notation and numbered plan/review filenames; exclude qualified IDs.
REVISION = re.compile(r'\b(?i:revision)\s+[rR]?(\d+)(?![\w-])|'
                      r'(?:(?<![\w/-])r|\b(?:plan|review)-r)(\d+)(?![\w-])')
NO_REPORT = re.compile(r'\b(?:no\s+(?:plan\s+|html\s+)?report|without\s+(?:the\s+|an?\s+)?(?:html\s+|plan\s+)?report)\b', re.I)  # the user skipped the plan report
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
    return [('git', repo, f"`git {sub}{shown}`")]


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
        for target in redirects:
            add(target, f'a redirect into {target}')
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
                add(target, f'`{words[0]}` into {target}')
        elif name in POSIX_WRITERS + REMOVERS:
            named, positional = ps_params(args)
            for target in [v for k in PS_TARGET for v in named.get(k, [])] + positional:
                add(target, f'`{words[0]}` on {target}')
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
                add(target, f'`{words[0]}` on {target}')
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
        elif name in INTERPRETERS and any(slash(a).endswith(('record.py', 'render_report.py')) for a in args):
            script = next(i for i, a in enumerate(args) if slash(a).endswith(('record.py', 'render_report.py')))
            rest = args[script + 1:]
            if slash(args[script]).endswith('record.py'):
                files = [a for a in rest if not a.startswith('-')][1:2]  # record.py <verb> <file> ...
            else:
                files = [rest[i + 1] for i, a in enumerate(rest[:-1]) if a == '--output']
            for target in files:
                add(target, f'`{slash(args[script]).rsplit("/", 1)[-1]}` writing {target}')
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
STATE_VERSION = 14
REFUSAL = re.compile(r"(?<!\w)(?:no|not|don'?t|niet|nee)(?!\w)")
TASK_REVIEW = re.compile(r'docs/plans/([A-Za-z0-9][\w.-]*?)/(?:reviews/)?([\w.-]+\.html)\b')
REPORT_REFERENCE = re.compile(r'(?:(?:[A-Za-z]:/|/)[^\n`<>"\']*?)?'
                              r'docs/plans/[A-Za-z0-9][\w.-]*?/(?:reviews/)?[\w.-]+\.html'
                              r'(?=$|[\s`<>"\'\]),;]|\.(?=\s|$)|[!?](?=\s|$))')
INLINE_TARGET = re.compile(r'''\s*(?:<([^<>"'\r\n]+)>|([^\s<>"']+))(?:\s+(?:"(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*'|\((?:[^()\\]|\\.)*\)))?\s*''')
URI_REFERENCE = re.compile(r'(?<![\w+.-])(?:[A-Za-z][\w+.-]*://|[A-Za-z][\w+.-]+:)'
                           r'[^\s`<>"\'()]+')
# Report fingerprints this hook leaves in the transcript as host-recorded hook context (never agent text): one after a
# tool call that names a task report (read, written or rendered), and one when the owner answers.
SHOWN_MARK, REPLY_MARK = 'workflow-axa report fingerprint', 'workflow-axa report at owner reply'
FINGERPRINT = re.compile(r'^(workflow-axa report (?:fingerprint|at owner reply)): (docs/plans/\S+?\.html) sha256=([0-9a-f]{64})$', re.M)
IDE_TEXT = re.compile(r'<(ide_\w+)>.*?</\1>', re.S)
SKILL_READ = re.compile(r'/(workflow(?:-clarify|-specify|-execute|-deliver)?)/SKILL\.md$')


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
    if re.search(r'<(?:local-command-std\w+|bash-std\w+|bash-input|user-prompt-submit-hook|task-notification)>', text):
        return None
    text = re.sub(r'<system-reminder>.*?</system-reminder>', ' ', text, flags=re.S)
    return IDE_TEXT.sub(' ', text)


def clean(text: str) -> str:
    """Case, spacing, curly quotes and trailing punctuation ignored."""
    text = text.replace('’', "'").replace('‘', "'").replace('“', '"').replace('”', '"')
    return re.sub(r'[\s.!?,;:]+$', '', ' '.join(text.split()).casefold())


def fresh_state() -> dict:
    return {'v': STATE_VERSION, 'offset': 0, 'head': '', 'mark': '', 'n': 0, 'lines': 0, 'parsed': 0,
            'active': False, 'rules': False, 'tasks': [], 'users': [], 'presented': {}, 'asks': {}, 'last_user': -1,
            'last_words': '', 'report_presented': {}, 'chat_presented': {}, 'paused_tasks': {},
            'shown_at': {}, 'shown_roots': {}, 'chat_roots': {}, 'user_tasks': {}, 'fingerprints': {}, 'replies': {}}


def set_task(state: dict, name: str, n: int):
    if name and not re.search(r'\.\w{1,4}$', name) and (not state['tasks'] or state['tasks'][-1][0] != name):
        state['tasks'].append([name, n])


def control_intent(text: str) -> str | None:
    """Recognise direct stop/resume requests, not feature prose mentioning a Stop button.

    This intentionally small vocabulary is not a natural-language permission classifier.
    Other wording remains subject to the phase instructions and host permissions.
    """
    words = clean(text)
    if re.search(r"\b(?:do not|don't)\s+(?:start\s+)?(?:implement|write (?:application )?code|edit (?:application )?files)(?:[.!?]|$|\s+(?:yet|until|now)\b)", words):
        return 'pause'
    if re.match(r"^(?:please\s+)?(?:stop|pause|cancel)(?:[.!?]|$|\s+(?:now|here|this task|the task|working|coding|implementation)\b)", words):
        return 'pause'
    if re.match(r"^(?:please\s+)?(?:continue|resume)(?:[.!?]|$|\s+(?:now|this task|the task|the approved task|working)\b)", words):
        return 'resume'
    return None


def add_words(state: dict, n: int, text: str, kind: str):
    """Retain the full answer, including restrictions; oversized answers cannot be clipped into consent."""
    words = clean(re.sub(r'\s*\(recommended\)\s*$', '', text, flags=re.I) if kind == 'answer' else text)
    state['users'].append([n, words[:16000], len(words) > 16000, kind])
    state['last_words'] = (state['last_words'] + ' . ' if state['last_user'] == n else '') + words[:4000]
    state['last_user'] = n
    task = state['tasks'][-1][0] if state['tasks'] else '*'
    state['user_tasks'][str(n)] = task
    intent = control_intent(words)
    if intent == 'pause':
        state['paused_tasks'][task] = n
    elif intent == 'resume':
        state['paused_tasks'].pop(task, None)
        state['paused_tasks'].pop('*', None)


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


def feed(state: dict, entry: dict, raw: str, cwd: str):
    """Fold one transcript entry into the state."""
    n = state['n']
    state['n'] += 1
    content = (entry.get('message') or {}).get('content')
    if entry.get('type') == 'attachment':  # recorded by the host from this hook's own output, not by the agent
        hook = entry.get('attachment') or {}
        if hook.get('type') == 'hook_additional_context' and hook.get('hookEvent') in ('PostToolUse', 'UserPromptSubmit') \
                and not entry.get('isSidechain'):
            for mark, path, sha in FINGERPRINT.findall('\n'.join(str(line) for line in hook.get('content') or [])):
                found = TASK_REVIEW.fullmatch(path) or TASK_REVIEW.match(path)
                if found:
                    rows = state['replies' if mark == REPLY_MARK else 'fingerprints'].setdefault(found.group(1), {})
                    rows[found.group(2).lower()] = (rows.get(found.group(2).lower(), []) + [[n, sha]])[-50:]
        return
    if entry.get('type') == 'user':
        typed = content if isinstance(content, str) else '\n'.join(
            str(b.get('text', '')) for b in content or [] if isinstance(b, dict) and b.get('type') == 'text')
        typed = re.sub(r'<system-reminder>.*?</system-reminder>', ' ', typed, flags=re.S)
        state['active'] = state['active'] or (not entry.get('isMeta') and bool(TYPED.search(typed)))
        text = user_text(entry)
        if text is not None:
            for a, b in TASK_NAMED.findall(slash(text)):
                set_task(state, a or b, n)
            if '<command-name>' in text:
                state['last_user'] = n  # a slash command: its arguments are not consent
                args = re.search(r'<command-args>(.*?)</command-args>', text, re.S)
                state['last_words'] = clean(args.group(1))[:4000] if args else ''
            else:
                add_words(state, n, text, 'msg')
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
                at, origin, questions = asked
                for question, value in result['answers'].items():
                    if question in questions:
                        # A matched host answer establishes that this question was actually delivered.
                        # The question alone, a cancelled tool or thinking never presents/approves anything.
                        present_reports(state, question, at, origin)
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
            state['asks'][block['id']] = [n, origin, questions]
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
                set_task(state, found.group(1), n)
        elif name in SHELLS:
            for kind, where, _ in shell_writes(str(data.get('command', '')), str(entry.get('cwd') or cwd),
                                               name == 'PowerShell'):
                for task in TASK_PATH.findall(where + '/') if kind == 'path' else []:
                    set_task(state, task, n)


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


def checkpoint(plan: str) -> str:
    found = re.search(r'^##\s+Current checkpoint\s*$(.*?)(?=^##\s|\Z)', plan, re.M | re.S | re.I)
    return found.group(1) if found else plan


def lightweight_files(text: str, root: str) -> set[str]:
    files = set()
    for found in LIGHT_LINE.finditer(text):
        listed = re.split(r'\s+(?:—|–|--|-)\s+', found.group(1), maxsplit=1)[0]
        for name in re.split(r'[,\s]+', listed):
            name = slash(name.strip('`"\'')).removeprefix('./')
            if name:
                files.add(key(relative(absolute(name, root), root) if is_absolute(name) else name))
    return files


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
CONTINUES = re.compile(r'\b(?:continue|resume)\b')
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
        stopped = [n for n, words in later if control_intent(words) == 'pause']
        if stopped and not any(n > stopped[-1] and control_intent(w) == 'resume' for n, w in later) \
                and not any(CONTINUES.search(w) for _n, w, _t, _k in (current or {}).get('users', [])):
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
    if NEGATIVE.search(marker) or not POSITIVE.search(marker):
        return f'does not approve a revision (`{line[:160]}`)'
    reports = tuple(re.findall(r'([\w.-]+\.html)\b', line))
    revisions = revision_numbers(line)
    other_revisions = [r for other in text.splitlines() if other.strip() != found.group(0).strip()
                       for r in revision_numbers(other)]
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
    if any(clean(q) in {'no', 'nope', 'not yet', 'not now', 'nee', 'niet', 'decline', 'hold off',
                       'pending', 'awaiting', 'proposed', 'not waived', 'not given'}
           or REVOKED.search(clean(q)) or WAITING_APPROVAL.search(q)
           or REFUSED_APPROVAL.search(q) for q in quotes):
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


def scope_problem(target: tuple[str, str, str], root: str, folder: Path, reports: list[str]) -> str | None:
    """The approved report's explicit `write_paths` (render_report.py manifest) bound file writes; reports without
    them keep approval-only behaviour. Git and unresolved shell writes are not path-checked."""
    kind, where, label = target
    if kind != 'path' or not reports:
        return None
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
            return (f"workflow-axa: {label} cannot be checked against the approved plan: {name} lists its write paths in "
                    "an unreadable form. Re-render the plan with explicit `write_paths` and ask the owner to approve it.")
        allowed += [p.strip() for p in listed]
    if not allowed:
        return None  # an older report without write paths: approval-only, as before
    rel = key(relative(where, root))
    if any(rel == key(p.rstrip('/')) or (p.endswith('/') and rel.startswith(key(p))) for p in allowed):
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
    if len(state['tasks']) > 1 and changed_at > state['last_user']:
        return (f"workflow-axa: {label} was stopped because the current task changed to {task} after the user's last "
                "message. Tell the user which task this change belongs to and let them answer before you edit.")
    plan = Path(root or '.') / 'docs' / 'plans' / task / 'PLAN.md'
    try:
        text = checkpoint(plan.read_text(encoding='utf-8', errors='replace'))
    except OSError:
        return (f"workflow-axa: {label} needs the current task's approval, but the current task {task} has no PLAN.md in "
                f"this worktree ({root}). Record the task there, or name the task this change belongs to.")
    if kind == 'path' and key(relative(where, root)) in lightweight_files(text, root):
        return None
    problem = report_problem(plan.parent, text)
    if problem:
        return (f"workflow-axa: {label} needs implementation approval, but the current task {task} has {problem}. "
                "Approval needs the HTML plan from workflow-specify. For a change with no behavior a user or caller can "
                "notice, record a `- Lightweight edit: <files> — <why>` line in the checkpoint instead.")
    used: list[str] = []
    problem = approval_problem(text, state, task, transcript, project.cwd, plan.parent, used)
    if not problem:
        return scope_problem(target, root, plan.parent, used)
    return (f"workflow-axa: {label} needs implementation approval, and the current task {task} does not have it: the "
            f"Approval line in {slash(str(plan))} {problem}. Loading a phase grants nothing by itself. Agree the behavior "
            "(workflow-clarify), approve the plan (workflow-specify), and record the user's answer in quotes on the "
            "`- Approval:` line before requesting the edit. For an older record, use resume-task to reconcile the "
            "original report, complete answer and scope; ask only where that evidence is insufficient. "
            "Do not edit or disable the hook to bypass this block. Task records, .artifacts and the report stay writable.")


# Report guides (round v3), unchanged

REPORT_GUIDES = ('codebase-map/TASK-REPORT.md', 'simple-english/SKILL.md')
UI_GUIDE = 'codebase-map/UI-FLOW.md'


def unread_report_guides(path: Path) -> list[str]:
    """Report guides not read whole in this context, when specify or deliver loaded (round v3: in all four
    worktrees the report was rendered before its writing rules were read). Reuses plain_reply's read test."""
    import importlib.util
    spec = importlib.util.spec_from_file_location('plain_reply', Path(__file__).with_name('plain_reply.py'))
    reply = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(reply)
    missing = reply.unread_files(path)
    wanted = REPORT_GUIDES + (UI_GUIDE,)
    return sorted({rel for phase in ('workflow-specify', 'workflow-deliver') for rel in missing.get(phase, ())
                   if rel in wanted})


def deny(reason: str) -> int:
    print(json.dumps({'hookSpecificOutput': {'hookEventName': 'PreToolUse', 'permissionDecision': 'deny',
                                             'permissionDecisionReason': reason}}))
    return 0


def judge(event: dict) -> int:
    transcript = str(event.get('transcript_path') or '')
    command = str((event.get('tool_input') or {}).get('command', '')) if event.get('tool_name') in SHELLS else ''
    if 'render_report.py' in command and '--help' not in command and transcript:
        try:
            unread = unread_report_guides(Path(transcript))
        except (OSError, ValueError, AttributeError):
            unread = []
        if unread:
            return deny("workflow-axa: read these whole before rendering the report, because they set its content and "
                        f"wording: {', '.join(unread)} (under the workflow-axa skills folder). Then render.")
    project = Project(str(event.get('cwd') or ''))
    targets = [t for t in targets_of(event)
               if t[0] != 'path' or (project.contains(t[1]) and not RECORD.match(relative(t[1], project.root_of(t[1]))))]
    if not targets or not transcript:
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
    task = state['tasks'][-1][0] if state['tasks'] else '*'
    if task in state.get('paused_tasks', {}) or '*' in state.get('paused_tasks', {}):
        return deny("workflow-axa: the user stopped, paused or cancelled this task. Do not start another write. "
                    "Record the handoff only; implementation needs an explicit continuation request.")
    if state['rules']:
        targets = [t for t in targets if t[0] != 'path' or not RULE_FILE.search(t[1])]  # D20: rule-maker writes rules
    for target in targets:
        if target[0] == 'ambiguous':
            return deny(f"workflow-axa: {target[2]} is relative to a folder set by a shell variable the gate cannot "
                        "resolve, so it cannot tell whether this is a task record. Use an explicit path (or set the "
                        "variable in the same command) and retry.")
        problem = authority_problem(target, state, project, path)
        if problem:
            return deny(problem)
    return 0


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
