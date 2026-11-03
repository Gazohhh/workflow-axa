# Audit fixes: approvals, recovery, verification and less repeated work

## Current checkpoint
- Status: plan written, waiting for the owner's answers and approval
- Owner: this Claude Code session (workflow-axa-ff); ownership: active
- Updated: 2026-11-03
- Repository / branch / worktree: D:\workflow-axa, main, main worktree. Local commits up to 0b4e4b4 are not pushed.
- Task identity: new, separate task. Source: the owner's ChatGPT audit prompt (2026-11-03). Related: `2026-11-02-modular-engineering-workflow` (the package build); this task fixes defects found in it. Sibling: `2026-11-03-ui-evidence-engine`.
- Rules readiness: READY. The repository's own CLAUDE.md, the package tests and the shared rules 1.8.0 cover it (`rules_stamp.py`: NONE, the package has no project line).
- Agreement: proposed revision r1, not agreed. Questions Q1-Q5 in DECISIONS.md are open.
- Approval: proposed revision r1, not approved. Report: `reviews/plan-r1.html`.
- Current understanding / evidence: FINDINGS.md E1-E23. Reproduced: E1-E6, E11-E14, E16-E18, E20-E23. Measured: E10, E19. Unknown: E7. Limit or risk: E8, E15.
- Next safe action: the owner answers Q1-Q5 and says yes to the agreement and plan, or asks for changes. No package code changes before that.

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
Proposed revision r1, not agreed. It covers acceptance A1-A14 above and the approach below, with Q1-Q5 open. If Q1 is (b), A1 drops the quoted-words check. If Q5 is (c), T9 is dropped and only static and helper tests are reported.

## Approach and scope
- Package files only: hooks, scripts, skills and docs of workflow-axa, plus tests. No application repository changes. No global settings or permission changes. No automatic commits.
- Keep: the four phases, grilling, grounded planning, both gates, task reuse, history, shared rules, artifact protections, pinned specialist methods, the D14 UI rule and the approved report design.
- Each confirmed defect gets a regression test that fails before the fix.
- Order by impact: T1 approvals, T2 records, T3 stop and recovery, then T4 baselines, T5 reports and wording, T6 proportional agents, T7 portability, T8 docs and release, T9 live acceptance.
- Budgets: the main session builds each ticket (small route). T1, T2 and T3 each get one fresh reviewer; the others get one combined review at the end. Full package suite once per ticket and once at the end. Live runs only as approved in Q5.
- Enforcement honesty: the hook can block explicit edit tools it sees. It cannot see every shell write, edits outside Claude Code, or prove that a record is truthful beyond matching the user's words in the transcript. Codex gets no hooks. The docs will say so.

## Approval
Not yet given.
