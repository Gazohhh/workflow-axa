# Optional prompt help — compatibility entry

Describe the goal in ordinary language. The workflow owns the investigation, questions, records and approval procedure; repeating that procedure in a long prompt is unnecessary. Use the command your installation actually exposes. A prepared prompt does not replace code inspection or approve an unseen plan.

## Handoff message

When the user has to pass status to another agent session, another machine, a person or a tracker, don't make them write it. Generate it from the checkpoint and TODO, ready to paste, in this shape:

```text
For: <recipient: session name, machine, person or tracker>
Task: <task folder> — <one-line goal>
State: <agreed / approved / implementing / delivered / blocked / paused / stopped / cancelled / partial>; next safe action: <step>
Pull: <branch and commit, or "local changes on <machine>, not pushed">
Changed files: <paths, or none>
Done (with evidence): <ticket — V-ID, one line each>
Not tested: <scope and reason, or nothing>
Open: <ticket — what blocks it>
Don't touch: <files or areas another session owns>
Needs from you: <the exact question or human step, or "nothing">
```

Only facts in the records go in; say "unknown" rather than guessing. For a tracker, post this as one update when the user asks; the records stay the source.
