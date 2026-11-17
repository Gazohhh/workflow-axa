# An approval answer is lost when the question ends in a line break

## Current checkpoint
- Updated / phase: 2026-11-17; T1 verified; delivery with the other rc.3 tasks
- Rules: READY (AGENTS.md project rules; shared START, CORE, READINESS)
- Recipe: bug; plus Compatibility: answers in existing transcripts keep their meaning; scope: the task; classification question: not asked
- Agreement (gate one): not required — one-ticket offer (D1)
- Offer: #1 approved (owner, question tool, 2026-11-17)
- Implementation: T1 verified (FINDINGS V1, V2, S2, S3)
- Verification / owner acceptance: not run
- Blockers: none
- Changed files: hooks/approval.py (answer_to and the call questions on answer events), skills/workflow/scripts/offers.py (present --question), tests/test_approval_hook.py, tests/test_offers.py. Worktree: D:\workflow-axa-redesign (detached at c5e954b); the main checkout stays untouched until release

## Goal

Owner, 2026-11-17: "This is a bug btw, I did [answer]; find out why and spar with GPT while also fixing this problem." The owner approved offer #9 of docs/plans/2026-11-17-spar-skill with the question tool's "Approve from this summary" button. The question text was the output of `record.py offer present --question`, which ends in a line break. T3 Code returned the answer keyed by the question without that line break, so Claude Code told the agent "The user did not answer the questions", and hooks/approval.py, which looks the answer up by the exact question text, recorded no approval (FINDINGS F1).

## Fix

- `offer present --question` prints no surrounding whitespace, so the question text and the host's key agree.
- hooks/approval.py finds an answer by the question text with surrounding whitespace removed, at every lookup, through one helper; any other difference still finds nothing.
- Test first: a transcript whose answer key is the question without its final line break approves; a key that differs in anything else does not; the `--question` output ends without whitespace.
