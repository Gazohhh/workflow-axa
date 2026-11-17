# TODO

## Overview

| Ticket | What needs to happen | Status | Dependencies |
|---|---|---|---|
| T1 | Let an offer approval by button or by `/approve <N>` lift the session pause | Verified | none |

## Tickets

### T1 — Let an offer approval by button or by `/approve <N>` lift the session pause
Status: Verified

What needs to happen: `paused()` in hooks/approval.py lifts a pause only on a typed message that `control_intent` reads as "continue" (a typed "approve" or "go ahead"). An approval by the question tool's button, or typed as `/approve <N>`, approves the offer but leaves the pause, so every write stays refused (FINDINGS E1, E2). Count both as "continue", like a typed approval.

What should work:
- "Do not implement until I approve", then the offer presented in the question tool, then "Approve from this summary" (with or without "(Recommended)"): writes the offer covers are allowed.
- The same with a typed `/approve <N>` after a text presentation: allowed.
- A button "Approve" on a question that carries no offer lifts nothing.
- "Change something", "Show review.html first", a qualified answer or an unanswered question lift nothing.
- A "stop" after the approval still pauses all writes; a later typed "continue" or a new offer approval lifts it, as today.
- A withdrawal ("I revoke that") still ends the approval; lifting the pause never revives a withdrawn approval.

Technical details:
- May change: hooks/approval.py (`paused()` reads `answer` events of questions that carry an offer presentation, and typed `/approve <N>`), tests/test_approval_hook.py, skills/workflow/VISUAL-REVIEW.md ("Read the answer": an approval of a presented offer also continues after a stop). Must not change: `control_intent`'s vocabulary in phase_gate.py, the offer model, decide()'s approval rules.
- Test seam: the hook process with synthetic transcripts (the existing ApprovalHookCase); catches the refusal after a button or `/approve <N>` approval and any over-broad lifting; misses live host behaviour (checked once live: this session).
- TDD: yes.

References:
- Supports: the owner's request (D1 of this task), FINDINGS E1-E5.
- Depends on: none.
- Rules: AGENTS.md (hooks change in isolation; never weaken checks).

Documents: skills/workflow/VISUAL-REVIEW.md "Read the answer".

How to verify:
- `cd tests && python -X utf8 -m unittest test_approval_hook`, new cases red first, then green; the full suite; `python -X utf8 -I tools/validate.py`.
- Live: in this session, after the fix is in the worktree, the pause no longer blocks once a button approval follows it. (The session loads hooks from D:\workflow-axa, the main checkout, so the live check happens only after the release; until then it is NOT VERIFIED live.)
- Review of the code and the docs by GPT-6 Astra until it agrees.

Evidence: FINDINGS V-lines.; V3 and Review 3 in FINDINGS; full suite at delivery
