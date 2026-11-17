# An approval covers only the session's own worktree

## Current checkpoint
- Updated / phase: 2026-11-17; execute: T1 test first
- Rules: READY (AGENTS.md project rules; shared START, CORE, READINESS)
- Recipe: bug (fix something broken); plus Security: an approval must never authorise writes in a checkout it wasn't given for — an offer approved in the main checkout lets edits and git commands through in a linked worktree; scope: the task; classification question: not asked (the owner named it a bug fix)
- Agreement (gate one): not required — one-ticket offer, behaviour decided by the owner (D1)
- Offer: #1 approved (D3)
- Implementation: not started
- Verification / owner acceptance: not run
- Blockers: none
- Changed files: none. Worktree: D:\workflow-axa-redesign (detached at c5e954b); the main checkout stays untouched until release

## Goal

FINDINGS F4 of docs/plans/2026-11-17-approval-button-unpause, found by /spar pilot run 1: an offer approved in the main checkout also allows writes in a linked worktree of the same repository, including certain git command forms. Reproduced against the released 2.9.0-rc.2 hook.

Fix before 2.9.0-rc.3 with a fail-closed guard: a project write whose target lies in a different worktree than the session's is refused, with a message that says how to continue. The full per-worktree lookup (F2: such writes become allowed with that worktree's own offer) comes after the release.
