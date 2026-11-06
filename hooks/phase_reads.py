"""Point to phase-owned guidance without copying its procedure into every tool result.

Conditional reads are reminders, not a reliable UI/TDD classifier or an approval grant.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import sys

UI = ('ui-design/SKILL.md', 'rule-maker/rules/design.md', 'ui-design/VERIFY.md', 'codebase-map/UI-FLOW.md')
TDD = 'tdd/SKILL.md'
CODE_REVIEW = 'code-review/SKILL.md'
READS = {
    'workflow-clarify': ('grilling/SKILL.md',) + UI[:2],
    'workflow-specify': ('codebase-map/TASK-REPORT.md', 'simple-english/SKILL.md', 'codebase-map/FLOWCHART-DESIGN.md') + UI[:2] + (UI[3],),
    'workflow-execute': ('workflow/AUDIT.md', TDD, CODE_REVIEW) + UI[:3],
    'workflow-deliver': ('simple-english/SKILL.md', 'codebase-map/TASK-REPORT.md', 'codebase-map/FLOWCHART-DESIGN.md', UI[3]),
}


def main() -> int:
    try:
        event = json.load(sys.stdin)
    except ValueError:
        return 0
    if not isinstance(event, dict):
        return 0
    data = event.get('tool_input') or {}
    if not isinstance(data, dict):
        return 0
    name = str(data.get('skill', '')).split(':')[-1]
    typed = re.search(r'(?:^\s*|<command-name>\s*)/(?:workflow-axa:)?(workflow(?:-clarify|-specify|-execute|-deliver)?)(?![\w-])',
                      str(event.get('prompt', '')))
    kind = event.get('hook_event_name', 'PostToolUse')
    if kind == 'UserPromptSubmit':
        if not typed:
            return 0
        name = typed.group(1)
    elif event.get('tool_name') != 'Skill':
        return 0
    root = Path(os.environ.get('CLAUDE_PLUGIN_ROOT') or Path(__file__).resolve().parents[1]) / 'skills'
    if name == 'workflow':
        note = ('workflow-axa: check readiness and find/reuse the task, then invoke the phase selected by '
                'workflow/SKILL.md. Ask no behavior or design question from the router; ask only a blocking '
                'readiness choice there. Loading a skill grants no implementation permission.')
    elif name in READS:
        always = [rel for rel in READS[name] if rel not in UI and rel not in (TDD, CODE_REVIEW)]
        conditional = [rel for rel in READS[name] if rel in UI or rel in (TDD, CODE_REVIEW)]
        note = f'workflow-axa {name}. Read once in the current context: ' + '; '.join(str(root / rel) for rel in always)
        if conditional:
            note += '. Only when applicable (UI / TDD / code review respectively): ' + '; '.join(str(root / rel) for rel in conditional)
        note += ('. The phase SKILL.md owns the procedure, including the small route and stop behavior. '
                 'Existing valid reads count until their contents or context change. '
                 'Do not load UI files for backend-only work or TDD for a documentation-only ticket. '
                 'Record only files actually read. Follow applicable instructions even when a transcript heuristic misses them.')
    else:
        return 0
    print(json.dumps({'hookSpecificOutput': {'hookEventName': kind, 'additionalContext': note}}))
    return 0


if __name__ == '__main__':
    sys.exit(main())
