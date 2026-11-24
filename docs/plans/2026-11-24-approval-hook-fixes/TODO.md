# Tickets

## Overview

| Ticket | What needs to happen | Status | Dependencies |
|---|---|---|---|
| T1 | Host messages never count as the owner narrowing or withdrawing | Verified | none |
| T2 | Read-only offer commands pass; derive checked from the gate's parse | Verified | T1 (same files) |
| T3 | The refusal leads with the live offer's real reason | Verified | T2 (same files) |
| T4 | Builder briefs require verbatim test lines and file:line claims | Verified | none |
| T5 | Copy the tested candidate into hooks/ (owner's OK at that moment) | Verified | T1, T2, T3 |

## Tickets

### T1 — Host messages never count as the owner narrowing or withdrawing
Status: Verified
Evidence: V2, V5, V7, V8

What needs to happen: in hooks/phase_gate.py human_words, recognise T3's real delegated-result shape and treat the context-handoff and restart notices as host text, judging only a `User message:` inside them; bump the parse caches.

What should work:
- A1: an approved offer stays approved after a delegated result, a restart note wrapping one, a handoff wrapping a restart note, a task notification and an AskUserQuestion result whose question says "only … confirm".
- A handoff whose `User message:` is "stop" still stops; the owner's own "only…"/"I revoke" still narrow or withdraw.
- A2: read-only replay of the paperclip transcript shows #5/#6 approved with no host restrict/revoke fact.

Technical details:
- Files: hooks/phase_gate.py (DELEGATE_REPORT, human_words, STATE_VERSION 28), hooks/approval.py (ENTRIES_VERSION 3, facts-9), tests/test_approval_hook.py. Built in .artifacts/2026-11-24-approval-hook-fixes/candidate/.
- Test seam: the hook as a process on synthetic transcripts with the real shapes (existing harness); misses live host formats not yet seen. TDD: yes.

Documents: tests/README.md (a section for the new tests of T1-T3)

How to verify:
- `python -X utf8 -m unittest discover -s tests -p "test_approval_hook.py"` in the candidate; red before, green after.
- Replay script in the scratchpad against a copy of the transcript, cache dir in the scratchpad.

Verification: passed (V2, V5, V7, V8)

References:
- Supports: R1, A1, A2. Rules: AGENTS.md (hooks in isolation). Evidence: E1-E3.

### T2 — Read-only offer commands pass; derive checked from the gate's parse
Status: Verified
Evidence: V3, V7, V8

What needs to happen: phase_gate's record.py branch reports the task folder for offer write verbs and nothing for --help/present/show/list; derive's label carries the parent id with its reader beside it; an unresolvable derive yields a target approval refuses; scan skips offer-command targets for set_task; approval drops OFFER_COMMAND, offer_command_targets and the DERIVE regex.

What should work:
- A4: both real commands from E5 pass; `$R offer derive` refused with an unapproved/withdrawn parent, an unset folder variable or no parent id, allowed with an approved parent; derive --help passes; a read-only offer command with a redirect into a protected path is refused; an offer write leaves the legacy current task unchanged.

Technical details:
- Files: hooks/phase_gate.py, hooks/approval.py, tests/test_approval_hook.py (the derive case at ~1257 that relied on the gap is removed from the generic test), tests/test_hook_speed.py if it pins the old regex.
- Test seam: hook process; TDD: yes.

How to verify:
- test_approval_hook.py and test_hook_speed.py in the candidate.

Verification: passed (V3, V7, V8)

References:
- Supports: R3, A4. Decisions: D1, D2. Evidence: E5.

### T3 — The refusal leads with the live offer's real reason
Status: Verified
Evidence: V4, V6, V7, V8

What needs to happen: approval.no_offer builds from (offer, reason) pairs: no superseded/revoked, session task first then newer task folders, newest id first within a task, failed live offers before approved ones for other files, "no current offer" when all are terminal.

What should work:
- A3: superseded #1-#3, suspended #4, approved #5 for another file: refusal leads with #4's reason and never names #1-#3.

Technical details:
- Files: hooks/approval.py, tests/test_approval_hook.py. TDD: yes.

How to verify:
- test_approval_hook.py in the candidate.

Verification: passed (V4, V6, V7, V8)

References:
- Supports: R2, A3. Evidence: E4.

### T4 — Builder briefs require verbatim test lines and file:line claims
Status: Verified
Evidence: V8

What needs to happen: one sentence in skills/workflow-execute/SKILL.md "Briefs".

How to verify:
- full suite and tools/validate.py (word budgets, repeated paragraphs).

Verification: passed (V8: validate.py PASS, full suite)

References:
- Supports: R4, A5. Evidence: E6.

### T5 — Copy the tested candidate into hooks/
Status: Verified
Evidence: V8, D5

What needs to happen: after the full suite and tools/validate.py pass in the candidate, ask the owner; on their OK copy the changed files into D:\workflow-axa in one step and run the suite there.

How to verify:
- `python -X utf8 -I tools/validate.py` and the full suite in D:\workflow-axa.
- Human check: the owner's OK before the copy.

Verification: passed (V8)
Owner acceptance: owner OK before the copy, 2026-11-24 ("Copy now (Recommended)", DECISIONS D5), V8

References:
- Supports: A5. Rules: AGENTS.md "Installation, cache replacement, global settings and live-session changes require explicit approval".
