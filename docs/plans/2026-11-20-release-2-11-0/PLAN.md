# Release 2.11.0: the /spar rework

## Current checkpoint
- Updated / phase: 2026-11-20; closed (released 2.11.0, origin/main 7b4798b)
- Rules: READY (AGENTS.md project rules; shared START, CORE, READINESS)
- Recipe: none (release); modifiers none. Commit, merge main (2.10.0), release records and push of the delivered task docs/plans/2026-11-20-spar-rework. Scope: the task. Classification question: not asked
- Agreement (gate one): not required — one-ticket offer (the owner: "just push and release it don't forget to include the docs")
- Offer: #3 approved (owner, question tool, 2026-11-20; #1 and #2 superseded: operation names in backticks did not match the checker)
- Implementation: implemented (commits e859f80, 76cab3c, 7b4798b; pushed)
- Verification / owner acceptance: validate PASS, suite 1706 OK (V1); push verified (V2)
- Blockers: none
- Changed files: none
- Next safe action: the owner updates D:/workflow-axa (git pull --ff-only), the Claude plugin and the Codex copies, then runs one T3 /spar

## Working context
- Owner: Cem. Worktree D:/workflow-axa-spar, branch spar/architecture-review (3972094 plus the uncommitted rework). origin/main = main = 8a56c42 (2.10.0).
- The installed Claude plugin reads D:/workflow-axa, so the release goes live there only when that checkout's main moves. That is a write in another worktree and needs its own offer there.

## Goal and acceptance
- The rework reaches origin/main as 2.11.0, with its docs and records.
- validate and the full suite pass on the release tree.

## Outcome

Released 2026-11-20 as workflow-axa 2.11.0: origin/main is at 7b4798b (FINDINGS V2).

- Docs: CHANGELOG, UPGRADE, README title, docs/DESIGN.md note, VALIDATION.md (1706 tests OK, validate PASS; V1).
- Not done:
  - The local checkout D:/workflow-axa, which the installed Claude plugin reads, still sits at 8a56c42. The owner updates it with `git -C D:/workflow-axa pull --ff-only`, then `claude plugin marketplace update gazohhh` and `claude plugin update workflow-axa@gazohhh`, and starts new sessions.
  - The Codex skill copies are refreshed from the release ZIP (`tools/build_release.py`).
  - A T3 cross-model spar on the installed release is still untested.
- Next safe action: the owner updates the local checkout and the installs, then runs one real T3 /spar.