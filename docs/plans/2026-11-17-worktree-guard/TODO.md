# TODO

## Overview

| Ticket | What needs to happen | Status | Dependencies |
|---|---|---|---|
| T1 | Refuse every project write whose target is in another worktree than the session's | Verified | none |

## Tickets

### T1 — Refuse every project write whose target is in another worktree than the session's
Status: Verified

What needs to happen: in `rest_of_call()` (hooks/approval.py), before offers are looked up, refuse any file target or git target whose worktree (`project.root_of`) differs from the session's worktree (`project.root`). Today such a target is checked against offers from the session's worktree, so the main checkout's approval leaks into linked worktrees (F4 of docs/plans/2026-11-17-approval-button-unpause).

What should work:
- Session in the main checkout, offer approved there: an edit in the main checkout is allowed, as today.
- The same session edits the same file in a linked worktree: refused, the message names both folders and says to start or move the session into that worktree.
- A git write aimed at the linked worktree, with an offer that lists that git operation: refused the same way; in the session's own worktree: allowed, as today.
- One call that writes in both checkouts: refused as a whole.
- Session started inside the linked worktree: writes there work with that worktree's offer; a write into the main checkout is refused.
- Task records (docs/plans/…) and output (.artifacts) stay writable as today; the pause, the rules question and the CSS check keep working.

Technical details:
- May change: hooks/approval.py (one check in rest_of_call before the offer lookup), tests/test_approval_hook.py (cases with a real linked worktree, built from the /spar probe), docs/RULE-CONTRACTS.md and skills/workflow/VISUAL-REVIEW.md only if they describe offer scope across worktrees.
- Must not change: covers(), the offer model, decide(), Project.contains() or root_of() in phase_gate.py.
- Test seam: the hook process with synthetic transcripts and a real linked worktree (ApprovalHookCase); catches cross-worktree allows for edits and git commands, and over-refusal in the session's own worktree; misses live host behaviour until the release.
- TDD: yes.

References:
- Supports: D1 (the owner's decisions), F4 of docs/plans/2026-11-17-approval-button-unpause, O1 of docs/plans/2026-11-17-spar-skill.
- Depends on: none.
- Rules: AGENTS.md (hooks change in isolation; never weaken checks); Security modifier.

Documents: docs/RULE-CONTRACTS.md if it states offer scope; CHANGELOG at release (separate step).

How to verify:
- `cd tests && python -X utf8 -m unittest test_approval_hook`, new cases red first, then green; the full suite; `python -X utf8 -I tools/validate.py`.
- The /spar probe is refused.
- Review of the code by GPT-6 Astra until it agrees.
- Live: not verified until the release (this session loads hooks from the main checkout).

Evidence:FINDINGS V1-V8; Reviews 1-8 (Astra review 8 passed under D5); known limits recorded
