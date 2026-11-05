# Audit fixes: approvals, recovery, verification and less repeated work

## Current checkpoint
- Status: delivered as complete 2026-11-04 (see Outcome; reviews/delivery-r3.html); waiting for owner acceptance
- Owner: this Claude Code session (workflow-axa-ff); ownership: active
- Updated: 2026-11-04
- Repository / branch / worktree: D:\workflow-axa, main, main worktree. Commits up to 9e8338e are local; everything after is uncommitted (owner, 2026-11-03).
- Task identity: new, separate task. Source: the owner's ChatGPT audit prompt (2026-11-03). Related: `2026-11-02-modular-engineering-workflow` (the package build); this task fixes defects found in it. Sibling: `2026-11-03-ui-evidence-engine`.
- Rules readiness: READY. The repository's own CLAUDE.md, the package tests and the shared rules 1.8.0 cover it (`rules_stamp.py`: NONE, the package has no project line).
- Agreement: revision r1 agreed by the owner 2026-11-03: "Yes to both".
- Approval: revision r1 approved by the owner 2026-11-03: "Yes to both" (report `reviews/plan-r1.html`, all tickets, the exclusions in Approach and Boundaries).
- Current understanding / evidence: FINDINGS.md E1-E23. Reproduced: E1-E6, E11-E14, E16-E18, E20-E23. Measured: E10, E19. E7 settled by V-E7. Limit or risk: E8, E15.
- Next safe action: the owner accepts the delivery and reviews D7-D10; then the follow-up simplification review, proposal only.

## Goal and acceptance
Fewer unauthorised actions, clearer recovery and less repeated work. Not more instructions or a bigger test count.

- A1: After `/workflow`, application code edits and git writes are allowed only when the current task's Approval line approves the current revision, and the user's words it quotes appear in a real user message. Loading clarify or specify allows only task records and the report.
- A2: Negated or quoted "lightweight" wording grants nothing. A lightweight edit needs a recorded line that names its files.
- A3: Another task's approval does not authorise the current task. A valid approval survives resumption; a changed scope does not inherit it.
- A4: Reading a phase SKILL.md whole counts as loading that phase, as the router documents.
- A5: The gate also runs for the PowerShell tool and MCP write tools, and catches common shell writes (redirection, tee, cp, mv, Set-Content, git apply/checkout/reset). The docs say plainly that command-text filtering is advice, not a security boundary.
- A6: An interrupted record write leaves the old file intact; a concurrent change is refused, never silently lost.
- A7: "Stop" ends implementation: no review loop, no return to execute. Paused, blocked, cancelled and partial each have one clear route, and the handoff names what changed, what was verified, what remains and the next safe action.
- A8: A failure counts as existing only when the same test fails the same way. Five existing failures becoming four existing plus one new is reported as one new failure.
- A9: A baseline is reused only while its command, commit, diff and environment still match. The required checks run again after the last repair.
- A10: A small change (one ticket, named files, no interface, data, dependency or security change) uses one builder and one independent review. It leaves that route when it turns risky. No second review of an unchanged diff.
- A11: Words that carry uncertainty, permission or a proposal keep their meaning. The wording check runs before the report is written, never blocks a valid report, and covers every report kind. An approved or presented report is never overwritten: a report counts as presented once the task records name it.
- A12: The test suite passes in a path with spaces and under POSIX.
- A13: One current verification summary, tied to a commit and environment, and generated where practical. The other documents point to it.
- A14: A release package is built from an explicit include list, without Git internals, caches, secrets or evaluation output.

## Agreement
Revision r1, agreed by the owner 2026-11-03: "Yes to both". It covers acceptance A1-A14 above and the approach below, with the owner's answers D1-D5: approval needs the Approval line plus the user's real words (A1), the small route (A10), an MIT licence and a release tool now (A14), and at most 8 live Claude runs plus useful Codex runs (T9).

## Approach and scope
- Package files only: hooks, scripts, skills and docs of workflow-axa, plus tests. No application repository changes. No global settings or permission changes. No automatic commits.
- Keep: the four phases, grilling, grounded planning, both gates, task reuse, history, shared rules, artifact protections, pinned specialist methods, the D14 UI rule and the approved report design.
- Each confirmed defect gets a regression test that fails before the fix.
- Order by impact: T1 approvals, T2 records, T3 stop and recovery, then T4 baselines, T5 reports and wording, T6 proportional agents, T7 portability, T8 docs and release, T9 live acceptance.
- Budgets: this nine-ticket task is not a small route; the main session and parallel workers build tickets with separate files. T1, T2 and T3 each get one fresh reviewer; the others get one combined review at the end. Full package suite once per ticket and once at the end. Live runs: at most 8 Claude runs plus Codex runs where useful (D5), none repeated without a reason.
- Enforcement honesty: the hook can block explicit edit tools it sees. It cannot see every shell write, edits outside Claude Code, or prove that a record is truthful beyond matching the user's words in the transcript. Codex gets no hooks. The docs will say so.

## Approval
Revision r1, `reviews/plan-r1.html`, approved by the owner 2026-11-03 together with the agreement: "Yes to both".


## Outcome

Delivered as complete on 2026-11-04 (fresh reconciliation, `reviews/delivery-r3.html`; `delivery-r2.html` is the earlier partial snapshot, kept as history).

- Asked: fix the ChatGPT audit's findings (approvals, recovery, verification, less repeated work, writing, records, docs and release). Agreed and approved: r1, "Yes to both" (2026-11-03), with D1-D5; D11 widened the live-run limit.
- Built: all nine tickets T1-T9 (FINDINGS V1-V11), plus the live-loop fixes (install guard, unreviewed-code check, report location, consent wording) and a baseline-input checker (`scripts/baseline_state.py`).
- Verified: all 14 acceptance items A1-A14 and AC11. Final runs on the final state: Windows, a checkout path with spaces and WSL, 763 tests OK each; validate PASS. Live: 8 rounds in Hooqd, Mulcol-app2, PletrixV2 and Altinstar; a PowerShell-tool write denied before approval; a write-enabled Codex run that changed nothing. Reviews: fresh reviews for T1, T2, T3/T4/T6, the whole feature (V9) and the baseline helper (V11); the fixes from V9 and V11 were checked by tests and the final runs, not by a second review.
- Not run on this host: symlink and POSIX file-mode cases. Codex results show model behaviour, not enforcement (Codex has no hooks).
- Decisions made for the owner (by: agent): D7-D10, to review.
- Not committed or pushed (owner, 2026-11-03). Release zip: `.artifacts/release/workflow-axa-2.8.0-rc.1.zip` (SHA-256 e2f4d7ce…). Gate cache: `%TEMP%\workflow-axa-gate` (pruned after 14 days).
- Next safe action: the owner accepts the delivery and reviews D7-D10; then the follow-up simplification review (proposal only, waiting for approval).
