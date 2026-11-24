# Spar: approval-hook fixes

## Current position
Revision 1, 2026-11-24. Is the fix agreement in docs/plans/2026-11-24-approval-hook-fixes/PLAN.md correct and as simple as it can be? Recommendation S3 (coordinator's synthesis of S2 plus both debaters' last amendments; not re-checked by the debaters, budget spent). Owner chose the label route for derive and "Turn this into a workflow plan". Next move: agree the revised agreement in workflow-clarify.

## Intent and boundaries
Owner: a quick spar with GPT to see whether the plan is correct, ending in a small, easy summary of what changes and where. Success criteria: real root causes; fixes in the owning code with nothing extra; nothing missing; no protection weakened; small and explainable. Quick effort, 6 launches, A: GPT-6.2 Sol, B: Claude Opus 5.5, conversation only (this file written for the handoff).

## Evidence
- Facts: task FINDINGS E1-E6. Read-only scan of every transcript under ~/.claude/projects: 4 "Context handoff" messages carry a `User message:`; each inner message is new (appears nowhere else), so it is the delivered turn, not a replay.
- B: `add()` (hooks/phase_gate.py:660) drops a target that still holds `$`, so a naive parse-once derive would skip the parent check for `offer derive "$T" 5`.
- A: tests/test_approval_hook.py:1257 expects a derive with parent `offer.json` to pass; it relied on the old gap.
- Assumption: offer writes calling set_task would change legacy checker selection (phase_gate.py:1343, approval.py:1149).

## Options considered
- Derive check by widened text regex (B's opening): one line; still guesses spelling (`"$R"`, `${R}`, `cd`). Rejected by the owner.
- Derive from the gate's parse (A): handles `$R` and `cd`; removes text matching. Chosen by the owner.
- Parent id carried in the write label read back by one phase_gate function (B, coordinator) vs a separate data field (A). Owner chose the label.
- Dropping a whole context handoff (A's opening worry) vs judging its inner `User message:` (B): evidence favours B; A withdrew the objection.

## What changed our thinking
- The handoff scan settled the unwrap question.
- B's `$` drop finding made "fail closed" part of the derive design.
- A's legacy finding kept offer writes out of scan's set_task.
- Both added phase_gate STATE_VERSION to the cache bumps.

## Owner decisions
- Derive from the gate's own parse, not a regex (answered after the coordinator's comparison).
- Label route for the parent id (answered at the conclusion).
- Turn this into a workflow plan.

## Open questions and dissent
- A prefers a data field over the label; owner chose the label. Mitigation: a test pins the label round trip.
- Known limit, unchanged: `R` set in an earlier Bash call can't be expanded; no derive check runs then.
- Unreviewed: S3 as a whole was not re-checked by the debaters.

## Handoff brief
S3:
- R1 hooks/phase_gate.py human_words: DELEGATE_REPORT allows " in child thread <id>"; messages starting "Context handoff (" or "Note: the T3 server restarted," are host text, only the part after the first "\n\nUser message:\n" is judged (recursively), else None.
- R2 hooks/approval.py no_offer: structured (offer, reason); no superseded/revoked; session task first, then newer task folders; newest id first within a task; failed live offers before approved ones for other files; "no current offer" when all are terminal.
- R3 hooks/phase_gate.py record.py branch: offer write verbs report the task folder; --help, present, show, list report nothing; derive's label carries the parent id, wording and reader in one phase_gate function; unresolved derive is refused (fail closed); scan skips offer-command targets for set_task. approval.py: OFFER_COMMAND, offer_command_targets and DERIVE removed; derive_problem reads the gate's targets. The test at tests/test_approval_hook.py:1257 drops its derive case.
- Caches: ENTRIES_VERSION 3, facts-9, STATE_VERSION 28.
- R4 skills/workflow-execute/SKILL.md Briefs: verbatim runner summary line(s) and file:line for claims about existing behaviour.
- Checks: real-shape tests, full suite, tools/validate.py, read-only replay of the paperclip transcript (#5/#6 stay approved).
- Copy into hooks/ only with the owner's explicit OK at that moment.
