# A button approval lifts a plan-only pause

## Current checkpoint
- Updated / phase: 2026-11-17; T1 verified; delivery after the full suite (with the /spar task); shipped in 2.9.0-rc.3 (2026-11-17, docs/plans/2026-11-17-release-rc3)
- Rules: READY (AGENTS.md project rules; shared START, CORE, READINESS)
- Recipe: bug; plus Compatibility: stops and withdrawals in existing sessions keep working — the approval hook refuses work the owner approved with a button; scope: the task; classification question: not asked
- Agreement (gate one): not required — one-ticket offer (D2)
- Offer: #1 approved (D3)
- Implementation: not started
- Verification / owner acceptance: not run
- Blockers: the owner's answer to offer #1
- Changed files: none. Worktree: D:\workflow-axa-redesign (detached at c5e954b); the main checkout stays untouched until release

## Goal

Owner, 2026-11-17: "That bug needs fixing" (FINDINGS F1 of docs/plans/2026-11-17-spar-skill). When the owner writes "Do not implement until I approve that plan" and later approves the offer with the question tool's "Approve from this summary" button, the hook keeps refusing every write ("the owner stopped the work in this session"). A typed approval lifts that pause; a button approval doesn't.
