"""Read evidence from a host transcript: which files were read whole, in this context, and which phases loaded.

A library, not a hook (T20 of docs/plans/2026-11-15-workflow-redesign): phase_gate.py's ReadEvidence uses
scan_reads for the required-read and report-guide checks that approval.py keeps. The functions are the ones the
removed Stop hook (plain_reply.py) held, unchanged; the per-phase READS table came from the removed phase_reads.py.
"""
from __future__ import annotations

import ast
import functools
import json
import os
import re
import shlex
from pathlib import Path

EDIT_TOOLS = ("Edit", "Write", "MultiEdit", "NotebookEdit")

UI = ('ui-design/SKILL.md', 'rule-maker/rules/DESIGN.md', 'ui-design/VERIFY.md', 'codebase-map/UI-FLOW.md')
TDD = 'tdd/SKILL.md'
CODE_REVIEW = 'code-review/SKILL.md'
READS = {
    'workflow-clarify': ('grilling/SKILL.md',) + UI[:2],
    'workflow-specify': ('codebase-map/TASK-REPORT.md', 'workflow/WRITING.md', 'codebase-map/FLOWCHART-DESIGN.md') + UI[:2] + (UI[3],),
    'workflow-execute': ('workflow/AUDIT.md', TDD, CODE_REVIEW) + UI[:3],
    'workflow-deliver': ('workflow/WRITING.md', 'codebase-map/TASK-REPORT.md', 'codebase-map/FLOWCHART-DESIGN.md', UI[3]),
}


GATE_LOAD_ERRORS = (SyntaxError, ImportError, OSError, AttributeError)


@functools.lru_cache(maxsize=1)
def gate_module():
    """phase_gate.py, loaded once per process: it owns the typed-command, task-path and shell-write parsing.
    phase_gate passes itself to scan_reads instead, so its own process never loads it twice. Raises one of
    GATE_LOAD_ERRORS when the file is missing or broken; main() then stays silent."""
    import importlib.util
    spec = importlib.util.spec_from_file_location('phase_gate_stop', Path(__file__).with_name('phase_gate.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@functools.lru_cache(maxsize=1)
def package_skills() -> frozenset[str]:
    """The bare names of this plugin's skills: the folders under <plugin root>/skills that hold a SKILL.md."""
    root = Path(os.environ.get('CLAUDE_PLUGIN_ROOT') or Path(__file__).resolve().parents[1]) / 'skills'
    try:
        return frozenset(p.parent.name for p in root.glob('*/SKILL.md'))
    except OSError:
        return frozenset()


def own_skill(name: str) -> str | None:
    """The bare name when a Skill call names one of this package's skills: `workflow-axa:<name>`, or a bare name
    without any plugin prefix (another plugin's `x:workflow` is not ours). None otherwise."""
    if name.startswith('workflow-axa:'):
        return name[len('workflow-axa:'):]
    return name if ':' not in name and name in package_skills() else None


def phase_reads_table() -> tuple[dict, set]:
    """The package files each phase names as its references (moved here from phase_reads.py at T20)."""
    return READS, set(UI)


READ_VERB = re.compile(r"^\s*(?:cat|type|get-content|gc|more|less|bat)\b", re.I)


def printed_python_reads(source: str) -> list[str]:
    """Recognise literal whole-file prints, never execute or interpret arbitrary Python."""
    try:
        body = ast.parse(source).body
    except (SyntaxError, ValueError):
        return []
    paths = []
    for statement in body:
        if isinstance(statement, ast.ImportFrom) and statement.module == 'pathlib' \
                and all(a.name == 'Path' and not a.asname for a in statement.names):
            continue
        if isinstance(statement, ast.Import) and all(a.name == 'pathlib' and not a.asname for a in statement.names):
            continue
        if not isinstance(statement, ast.Expr) or not isinstance(statement.value, ast.Call):
            return []
        call = statement.value
        if not isinstance(call.func, ast.Name) or call.func.id != 'print' or len(call.args) != 1 or call.keywords:
            return []
        read = call.args[0]
        if not isinstance(read, ast.Call) or not isinstance(read.func, ast.Attribute) or read.args:
            return []
        opened = read.func.value
        if not isinstance(opened, ast.Call) or not opened.args or not isinstance(opened.args[0], ast.Constant) \
                or not isinstance(opened.args[0].value, str):
            return []
        name = ast.unparse(opened.func)
        if read.func.attr == 'read_text' and name in ('Path', 'pathlib.Path') and len(opened.args) == 1 \
                and not opened.keywords:
            options = read.keywords
        elif read.func.attr == 'read' and name == 'open' and not read.keywords \
                and (len(opened.args) == 1 or (len(opened.args) == 2 and isinstance(opened.args[1], ast.Constant)
                                             and opened.args[1].value == 'r')):
            options = opened.keywords
        else:
            return []
        if any(k.arg not in ('encoding', 'errors') or not isinstance(k.value, ast.Constant) for k in options):
            return []
        paths.append(opened.args[0].value)
    return paths


def whole_reads(block: dict) -> str:
    """Candidate paths from narrow complete reads. unread_files also checks identified calls' results."""
    data = block.get("input") or {}
    if block.get("name") == "Read":
        return "" if data.get("limit") or data.get("offset") else str(data.get("file_path", "")).replace("\\", "/")
    if block.get("name") not in ("Bash", "PowerShell"):
        return ""
    lexer = shlex.shlex(str(data.get('command', '')), posix=True, punctuation_chars=';&|<>\n')
    lexer.whitespace = ' \t\r'
    lexer.escape = ''  # Windows paths are literal; this is not a shell interpreter.
    try:
        tokens = list(lexer)
    except ValueError:
        return ''
    if any(token in ('&&', '||') for token in tokens):
        return ''  # a successful combined result does not prove a conditional read ran
    segments, current = [], []
    for token in tokens + [';']:
        if token in (';', '&&', '||', '\n'):
            if current:
                segments.append(current)
            current = []
        else:
            current.append(token)
    paths = []
    for words in segments:
        if words[0].lower() not in ('python', 'python3', 'py', 'cd', 'set-location', 'echo', 'pwd') \
                and not READ_VERB.fullmatch(words[0]):
            return ''  # compound/control commands need a dedicated read with its own result
        if any(re.fullmatch(r'[|&<>]+', word) for word in words):
            return ''  # piped, background or redirected output is not a whole displayed file
        if words[0].lower() in ('python', 'python3', 'py'):
            args = words[1:]
            while args and args[0] in ('-I', '-B', '-X'):
                width = 2 if args[0] == '-X' else 1
                if width == 2 and (len(args) < 2 or args[1] != 'utf8'):
                    break
                args = args[width:]
            if len(args) == 2 and args[0] == '-c':
                paths.extend(printed_python_reads(args[1]))
        elif READ_VERB.fullmatch(words[0]):
            args, valid, i = [], True, 1
            while i < len(words):
                word = words[i]
                if word.lower() == '-encoding':
                    i += 2
                    continue
                if word.startswith('-'):
                    if word.lower() not in ('--', '-n', '-raw', '-path', '-literalpath'):
                        valid = False
                        break
                else:
                    args.append(word)
                i += 1
            if valid:
                paths.extend(args)
    return '\n'.join(paths).replace('\\', '/')


def complete_result(entry: dict, result: dict) -> bool:
    """Reject explicit tool failures/truncation; content is never treated as owner consent."""
    details = entry.get('toolUseResult')
    if result.get('is_error') or entry.get('isSidechain') or entry.get('isMeta'):
        return False
    if isinstance(details, dict) and (details.get('exitCode', details.get('exit_code', 0)) != 0
                                     or details.get('stderr') or details.get('truncated') or details.get('isTruncated')):
        return False
    file = details.get('file') if isinstance(details, dict) else None
    if isinstance(file, dict) and (file.get('startLine', 1) != 1 or
                                  isinstance(file.get('numLines'), int) and isinstance(file.get('totalLines'), int)
                                  and file['numLines'] < file['totalLines']):
        return False
    content = result.get('content', '')
    text = content if isinstance(content, str) else '\n'.join(
        str(b.get('text', '')) for b in content if isinstance(b, dict)) if isinstance(content, list) else ''
    return bool(result.get('content')) and not re.search(
        r'^(?:Warning:\s*)?(?:(?:output|content)\s+(?:was\s+)?truncated|truncated output|'
        r'\[truncated\]|\d+\s+characters truncated)|^<persisted-output>', text, re.I | re.M)


def scan_reads(path: Path, entry_required: bool = True, gate=None) -> dict:
    """One pass over the transcript: the phases loaded, read evidence and the visible/TDD/code signals.
    `inputs` is the package-guide evidence, where legacy ID-less calls still count. `complete` holds the paths of
    calls with an ID whose own result is successful and complete. Both restart at compaction.
    `entered` (H2, 2026-11-11) turns true once the session started a workflow (a typed router or phase command, or a
    Skill call of one) or wrote a task record. A path that merely contains "workflow-axa" starts nothing.
    With `entry_required` (this Stop hook), a whole Read of a router or phase SKILL.md loads the phase only after
    that, and only for the package's copy (phase_gate.package_skill_read). phase_gate passes False for its own
    report-guide and declared-read checks, which keep the old rule: any whole read loads the phase, and passes
    itself as `gate` so it is not loaded a second time.
    `session` (agreement R12) is wider than `entered`: it also counts a Skill call of any package skill and typed
    text naming one ("workflow-axa:"). It decides whether the Stop checks apply at all. The old match of
    "workflow-axa" anywhere in a tool input, such as a path, no longer counts."""
    reads, _ui = phase_reads_table()
    gate = gate or gate_module()
    entered = session = False
    loaded: set[str] = set()
    inputs: list[str] = []
    complete: list[str] = []
    pending: dict[str, tuple[str, str]] = {}
    visible = False
    tdd = False
    code = False
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            entry = json.loads(line)
        except ValueError:
            continue
        if not isinstance(entry, dict):
            continue  # a valid JSON line that is not an entry
        content = (entry.get("message") or {}).get("content")
        if entry.get("type") == "system" and entry.get("subtype") == "compact_boundary":
            inputs = []  # the summary does not carry the files' text
            complete = []
            pending = {}
        if entry.get('isSidechain'):
            continue
        queued = gate.queued_text(entry) if entry.get("type") == "attachment" else None
        if queued is not None and gate.TYPED.search(queued):
            entered = True
        if entry.get("type") == "user":
            for result in content if isinstance(content, list) else []:
                if not isinstance(result, dict) or result.get('type') != 'tool_result':
                    continue
                read, loads = pending.pop(result.get('tool_use_id'), ('', False))
                if read and complete_result(entry, result):
                    inputs.append(read)
                    complete.extend(read.splitlines())
                    if loads:
                        loaded.update(phase for phase in reads if read.endswith(f'/{phase}/SKILL.md'))
            if not entry.get('isMeta') and not any(isinstance(b, dict) and b.get('type') == 'tool_result'
                                                  for b in (content if isinstance(content, list) else [])):
                text = json.dumps(content)
                for name in reads:
                    if f"/workflow-axa:{name}" in text or f"/{name}<" in text:
                        loaded.add(name)
                typed = content if isinstance(content, str) else '\n'.join(
                    str(b.get('text', '')) for b in content or [] if isinstance(b, dict) and b.get('type') == 'text')
                typed = re.sub(r'<system-reminder>.*?</system-reminder>', ' ', typed, flags=re.S)
                if gate.TYPED.search(typed):
                    entered = True
                if 'workflow-axa:' in typed:
                    session = True
        if entry.get("type") != "assistant" or not isinstance(content, list):
            continue
        for block in content:
            if not isinstance(block, dict) or block.get("type") != "tool_use":
                continue
            data = block.get("input") or {}
            if block.get("name") == "Skill":
                skill = own_skill(str(data.get("skill", "")).lstrip("/"))
                session = session or skill is not None
                entered = entered or skill == "workflow" or skill in gate.PHASES
                if skill in reads:
                    loaded.add(skill)
            # E5: the router's fallback, "or read its SKILL.md in full", loads the phase too. For the Stop hook only
            # in a session that already started a workflow or wrote a task record (H2).
            loads = block.get("name") == "Read" and (not entry_required or (entered and gate.package_skill_read(data)))
            if loads and not block.get('id'):
                read = whole_reads(block)
                loaded.update(name for name in reads if read.endswith(f"/{name}/SKILL.md"))
            if block.get("name") in EDIT_TOOLS:
                entered = entered or bool(gate.TASK_PATH.search(
                    str(data.get("file_path") or data.get("notebook_path") or "").replace("\\", "/") + "/"))
            elif block.get("name") in ("Bash", "PowerShell"):
                entered = entered or any(kind == 'path' and gate.TASK_PATH.search(where + '/') for kind, where, _ in
                                         gate.shell_writes(str(data.get('command', '')), str(entry.get('cwd') or ''),
                                                           block.get("name") == "PowerShell"))
            # Detect explicit task metadata, not the mere presence of "screen_change": "not-needed".
            plain = json.dumps(block.get("input", {})).replace('\\"', '"')
            if re.search(r'"screen_change"\s*:\s*"visible"|"ui_review"\s*:\s*\{', plain):
                visible = True
            if re.search(r'"tdd"\s*:\s*(?:true|"yes")|\bTDD:\s*yes\b', plain, re.I):
                tdd = True
            target = str((block.get("input") or {}).get("file_path", "")).replace("\\", "/")
            if block.get("name") in ("Edit", "Write", "MultiEdit", "NotebookEdit") and target \
                    and not re.search(r'(?:^|/)(?:docs/plans|\.artifacts)/', target) \
                    and Path(target).suffix not in ('.md', '.txt', '.html', '.json'):
                code = True
            read = whole_reads(block)
            if block.get('id'):
                pending[block['id']] = (read, loads)
            else:
                inputs.append(read)  # legacy ID-less transcripts: best-effort call evidence only
    return {'loaded': loaded, 'inputs': inputs, 'complete': complete, 'visible': visible, 'tdd': tdd, 'code': code,
            'entered': entered, 'session': session or entered}


def unread_files(path: Path, found: dict | None = None) -> dict[str, list[str]]:
    """For each workflow phase loaded in the session, the required files not opened in the current context.
    A read counts from the last compaction on, also before the phase loaded (round 22: the router's reads were
    demanded again). UI files count only when the session worked on a visible change (round 17)."""
    reads, ui_files = phase_reads_table()
    found = found if found is not None else scan_reads(path)
    loaded, visible, tdd, code = found['loaded'], found['visible'], found['tdd'], found['code']
    missing = {}
    opened = '\n'.join(found['inputs']).splitlines()
    for phase in loaded:
        needed = [rel for rel in reads[phase]
                  if (visible or rel not in ui_files)
                  and (tdd or rel != 'tdd/SKILL.md')
                  and (code or rel != 'code-review/SKILL.md')]
        gone = [rel for rel in needed if not any(name == rel or name.endswith('/' + rel) for name in opened)]
        if gone:
            missing[phase] = gone
    return missing
