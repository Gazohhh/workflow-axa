"""PreToolUse hook: in a session that started the workflow router, block code edits and git commit/push/merge
until a phase skill has run.

Hooqd retro (2026-11-03): the router investigated a bug, offered "start the fix as a workflow task", the user
answered "Let's do that, push when done", and the agent edited code and pushed to the release branches without
loading any phase. There was no task folder, agreement, plan report, fresh review or delivery record, and no check
noticed because the other hooks only look at phases that were loaded.

Allowed without a phase: task records and output (docs/plans, .artifacts), anything outside the project folder
(scratch, host folders), and a lightweight edit the agent declared in chat first ("Lightweight edit: ..."), as the router defines it. Exits 0 on bad input.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

PHASES = ('workflow-clarify', 'workflow-specify', 'workflow-execute', 'workflow-deliver')
EDIT_TOOLS = ('Edit', 'Write', 'MultiEdit', 'NotebookEdit')
GIT_WRITE = re.compile(r'\bgit\s+(?:-C\s+\S+\s+|-c\s+\S+\s+)*(?:commit|push|merge)\b')
# Hooqd edited source with sed -i and a Python heredoc; r24 with sed -i. The Edit tool alone missed both.
SHELL_EDIT = re.compile(r'\bsed\s+-i|\bperl\s+-p?i|\.write_(?:text|bytes)\(|\bopen\([^)]*,\s*[\'"][wa]b?[\'"]')
RECORDS = re.compile(r"(?:^|[/\s\"'=])(?:docs/plans|\.artifacts)/", re.I)
CD = re.compile(r'(?:^|[;&|]\s*)cd\s+(?:"([^"]+)"|\'([^\']+)\'|(\S+))')


def norm(path: str) -> str:
    """Lower-case forward-slash path; Git Bash /d/x becomes d:/x."""
    path = path.replace('\\', '/').rstrip('/').lower()
    return re.sub(r'^/([a-z])/', r'\1:/', path + '/')


def in_project(path: str, cwd: str) -> bool:
    """Task records and output are free; other paths inside the project folder need a phase. Outside it
    (scratch, host folders) they are free, wherever the project itself lives (r24: a project under Temp)."""
    candidate = norm(path)
    if RECORDS.search(candidate):
        return False
    if not re.match(r'^([a-z]:/|/)', candidate):  # relative: inside the project
        return True
    return bool(cwd) and candidate.startswith(norm(cwd))
TYPED = re.compile(r'<command-name>\s*/(?:workflow-axa:)?(workflow(?:-clarify|-specify|-execute|-deliver)?)\s*</command-name>'
                   r'|^\s*/(?:workflow-axa:)?(workflow(?:-clarify|-specify|-execute|-deliver)?)(?![\w-])', re.M)
LIGHTWEIGHT = re.compile(r'\blightweight edit\b', re.I)


def session_state(path: Path) -> tuple[bool, bool, bool]:
    """(router loaded, a phase loaded, lightweight edit declared in chat)."""
    router = phase = light = False
    for line in path.read_text(encoding='utf-8', errors='replace').splitlines():
        try:
            entry = json.loads(line)
        except ValueError:
            continue
        content = (entry.get('message') or {}).get('content')
        names = []
        if entry.get('type') == 'user':
            text = content if isinstance(content, str) else json.dumps(content)
            names += [a or b for a, b in TYPED.findall(text)]
        elif entry.get('type') == 'assistant' and isinstance(content, list):
            for block in content:
                if not isinstance(block, dict):
                    continue
                if block.get('type') == 'tool_use' and block.get('name') == 'Skill':
                    names.append(str((block.get('input') or {}).get('skill', '')).split(':')[-1])
                if block.get('type') == 'text' and LIGHTWEIGHT.search(block.get('text', '')):
                    light = True
        router = router or 'workflow' in names
        phase = phase or any(name in PHASES for name in names)
    return router, phase, light


def gated(event: dict) -> str | None:
    """What the call would do, when it needs a phase; None when it is always allowed."""
    tool, data, cwd = event.get('tool_name'), event.get('tool_input') or {}, str(event.get('cwd') or '')
    if tool == 'Bash':
        command = str(data.get('command', ''))
        found = GIT_WRITE.search(command)
        if found:
            return f'`{found.group(0)}`'
        edit = SHELL_EDIT.search(command)
        if not edit or RECORDS.search(command.replace('\\', '/')):
            return None
        targets = [a or b or c for a, b, c in CD.findall(command)] or [cwd or '.']
        return f'an in-place edit (`{edit.group(0)}`)' if any(in_project(t, cwd) for t in targets) else None
    if tool in EDIT_TOOLS:
        path = str(data.get('file_path') or data.get('notebook_path') or '')
        return f'editing {path}' if path and in_project(path, cwd) else None
    return None


def main() -> int:
    try:
        event = json.load(sys.stdin)
    except ValueError:
        return 0
    action = gated(event)
    if not action:
        return 0
    try:
        router, phase, light = session_state(Path(event.get('transcript_path', '')))
    except OSError:
        return 0
    if not router or phase or light:
        return 0
    reason = (f"workflow-axa: this session started /workflow, but no phase skill has run, so there is no task folder, "
              f"agreement or approved plan for {action}. Invoke workflow-clarify now: it writes the task folder and, "
              "for a small settled change, asks both gates in one message. A reply like \"do it\" or \"push when done\" "
              "after an investigation starts clarify; it is not approval of an unseen plan. Only for a lightweight edit "
              "as the router defines it (no behavior a user or caller can notice): say \"Lightweight edit:\" and why in "
              "chat first, then retry.")
    print(json.dumps({'hookSpecificOutput': {'hookEventName': 'PreToolUse', 'permissionDecision': 'deny',
                                             'permissionDecisionReason': reason}}))
    return 0


if __name__ == '__main__':
    sys.exit(main())
