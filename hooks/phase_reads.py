"""PostToolUse hook on Skill: when a workflow phase skill loads, name the files it requires, with full paths.

Retros in seven design-loop rounds found agents skipping the files a phase says to read first (grilling,
ui-design, design.md, VERIFY.md, tdd). A note right after the skill loads, with exact paths and the helper
command, is harder to skip than a sentence inside the skill. Never blocks; always exits 0.
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path
import sys

UI = ('ui-design/SKILL.md', 'rule-maker/rules/design.md')
READS = {
    'workflow-clarify': ('grilling/SKILL.md',) + UI,
    'workflow-specify': UI + ('codebase-map/TASK-REPORT.md', 'codebase-map/UI-FLOW.md', 'simple-english/SKILL.md'),
    'workflow-execute': ('tdd/SKILL.md', 'code-review/SKILL.md') + UI + ('ui-design/VERIFY.md',),
    'workflow-deliver': ('simple-english/SKILL.md', 'codebase-map/TASK-REPORT.md', 'codebase-map/UI-FLOW.md'),
}


def main() -> int:
    try:
        event = json.load(sys.stdin)
    except ValueError:
        return 0
    name = str((event.get('tool_input') or {}).get('skill', '')).split(':')[-1]
    # Typed form, or the <command-name> form some modes send (round 8: plan mode never matched).
    typed = re.search(r'(?:^\s*|<command-name>\s*)/(?:workflow-axa:)?(workflow(?:-clarify|-specify|-execute|-deliver)?)(?![\w-])',
                      str(event.get('prompt', '')))
    if event.get('hook_event_name') == 'UserPromptSubmit' and typed:
        # A typed slash command expands the skill without a Skill tool call, so PostToolUse never sees it.
        event, name = {'tool_name': 'Skill'}, typed.group(1)
    event_name = 'UserPromptSubmit' if typed else 'PostToolUse'
    if event.get('tool_name') == 'Skill' and name == 'workflow':
        # Round 8: the router asked a design question itself, so no task folder existed to save it in.
        note = ("workflow-axa router: find or create the task and check rules (ask only the readiness choice if they "
                "stop you). Then your next action is invoking the phase skill the router's section 3 picks "
                "(usually workflow-clarify). Ask no behavior or design question from the router; the phase skill "
                "saves questions with the task.")
        print(json.dumps({'hookSpecificOutput': {'hookEventName': event_name, 'additionalContext': note}}))
        return 0
    if event.get('tool_name') != 'Skill' or name not in READS:
        return 0
    root = Path(os.environ.get('CLAUDE_PLUGIN_ROOT') or Path(__file__).resolve().parents[1]) / 'skills'
    files = [str(root / rel) for rel in READS[name]]
    helper = root / 'ui-design/scripts/class_rules.py'
    extra = {
        'workflow-clarify': " For any copied element, also run `class_rules.py <root> --match <tag> <classes>` before "
                            "you name it: another existing element must have exactly that tag and class list.",
        'workflow-deliver': " Deliver never fixes: a gap the reconciliation finds goes back to execute, and after any fix "
                            "run the reconciliation again in a fresh subagent before writing the delivery. Screen cards use "
                            "the narrow capture (`-narrow.png`), not the desktop one. Write nothing in the task folder until "
                            "the reconciliation reports. Rewrite plan-time wording (\"will\", \"not yet\") in the past tense.",
        # Round 13: specify offered to skip the plan report for cost and recommended skipping it.
        'workflow-execute': " Hand every ticket to a fresh worker, even a two-line edit; record who built it. Start a "
                            "ticket only after the tickets it depends on are verified on the current files. Re-review "
                            "every repair. For each new UI element run `class_rules.py <root> --match <tag> <classes>`: "
                            "another existing element must have exactly that tag and class list. Quote counts exactly as "
                            "the check output states them (passed and failed).",
        'workflow-specify': " Run `class_rules.py <root> --match <tag> <classes>` for each copied element and cite "
                            "the element it finds. Screen cards use the narrow capture (`-narrow.png` from screenshot_report.py); a full-width "
                            "page shrinks to unreadable size in a card. Always build the HTML plan report, one-line changes included; never offer or recommend "
                            "skipping it for cost or size. Only the owner's own unprompted \"no report\" skips it.",
    }.get(name, '')
    note = (f"workflow-axa {name}: read these whole before you act (rules for this step live there): "
            + '; '.join(files) + '. The ui-design and design.md files apply when anything a user sees changes; '
            f"for each copied element run `python -X utf8 -I \"{helper}\" <project-root> <classes>` and "
            "`--compare <from-parent> <into-parent>`. If a copy would look different in any way where it goes "
            "(layout, spacing, a heading's bold), it is not a match: ask exactly \"I couldn't find a matching style "
            "for [element]. Is there an existing element I should mimic?\", offer same-tag options, recommend none. "
            "Name only files you actually opened in the records." + extra)
    print(json.dumps({'hookSpecificOutput': {'hookEventName': event_name, 'additionalContext': note}}))
    return 0


if __name__ == '__main__':
    sys.exit(main())
