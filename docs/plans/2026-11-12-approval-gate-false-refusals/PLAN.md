# Approval gate: false refusals and new hook checks

## Current checkpoint
- Updated / phase: 2026-11-12; closed
- Agreement (gate one): agreed 2026-11-12, agreement 1: "a) Agree (Recommended)"
- Approval (gate two): r1 approved, 2026-11-12, no report: "Approve r1, no report"
- Implementation: implemented and verified (T1-T8); T0 superseded (D1, D2)
- Verification / owner acceptance: passed (V2-V19); owner accepted 2026-11-12: "yes accepting it" (D3)
- Blockers: none
- Changed files: hooks/phase_gate.py, hooks/hooks.json (description), tests/test_gate_regressions.py, tests/test_phase_gate_hook.py, tests/test_gate_notes.py (new), docs/RULE-CONTRACTS.md, docs/ARCHITECTURE.md, skills/workflow/SETUP.md, CHANGELOG.md, UPGRADE.md, README.md, tests/README.md, version fields (plugin.json, rules version.json package_version, render_report.py, tests/behavioral/*.json); records; also the renamed audit record altinstar-proposed-AGENTS.txt
- Next safe action: none for this task. Later hook candidates 7 and 8 (docs/RULE-CONTRACTS.md)

## Working context
- Owner: Gazoh; repository D:\workflow-axa, branch main. Staged 2026-11-11 records stay untouched.
- Task identity: follow-up 3 of task 2026-11-12-owned-skills-and-repo-test-run; the owner asked for all six hook candidates (Q4 c), then narrowed them (Q6 c, Q7b a, Q8 a, Q9 a).
- Rules: READY / AGENTS.md (hook candidates are built and tested in an isolated copy first), tests/README.md
- Test output folder: .artifacts/2026-11-12-approval-gate-false-refusals/

## Goal and acceptance
Owner's words (2026-11-12): "Alright do all the follow-ups as well". Follow-up 3: the gate refused the owner's own report waiver, and the Altinstar retro reported approval failures.

## Agreement
Agreement 1, agreed 2026-11-12 (owner via question tool: "a) Agree (Recommended)").

What changes (Claude Code hook `hooks/phase_gate.py`, only in sessions where the gate is active):
1. Agreement check (Q7b a): a code change is refused while the task's checkpoint `Agreement (gate one)` line is not agreed, waived, legacy or "not required". A single answer that says yes to both gates counts. Lightweight edits and the small change route are not affected (they need no agreement). The refusal says which line is missing.
2. CSS and small-change warnings (Q8 a): when an edit to an application file adds a stylesheet rule, a `<style>` block or `style=""`, the gate adds a note for the agent: ask DESIGN.md rule 4's question or name the existing class. On the small change route it also notes a new tag or class in a listed file. It never refuses these edits.
3. Bulk deletes of test output (Q9 a): `git clean`, deleting `.artifacts` itself and wildcard deletes under `.artifacts` are refused. Deleting a single named file stays allowed.
4. Bug found in the reproduction (E2): the gate finds the checkpoint only under the exact heading `## Current checkpoint`. A heading such as `### Current checkpoint (D4)` makes it read the whole PLAN, so an old "approved r7" can override the current approval. The gate will accept any heading that starts with "Current checkpoint".
5. Clearer message (E4): in a linked worktree whose PLAN copy is older than the main checkout's, the refusal names the stale copy instead of asking the owner to approve again.
6. Regression tests for the reproduced cases: checkpoint heading variant, a report named only inside the approval question (keeps rc.4 behaviour), the new agreement check, the delete rule, the warnings.

Not changed (owner decisions): the report and plan waiver wording stays as it is (Q6 c, candidates 1 and 6); the 90 goal-stop blocks come from Claude Code's own /goal feature, not this package (E5).

How it is built and released: in an isolated candidate copy first (AGENTS.md), then into this repository, full suite, review, release 2.8.0-rc.38, commit and push, reinstall Claude Code and Codex from Git, then a check in a fresh session.

Assumptions (owner may reject):
- A task whose Approval line says legacy passes the agreement check even without an Agreement line (old single-gate tasks).
- "Application file" means any project file except Markdown, docs/plans, .artifacts and test files; those never trigger the CSS note.
- "Code change" in item 1 means the writes the gate already checks (project files and git writes). Tasks with an old single-gate Approval line are not checked.
- Item 3 refuses git clean (not its dry run), deleting .artifacts itself and wildcard deletes under it; deleting named files or folders there stays allowed.
- Codex gets no hook (unchanged); docs/RULE-CONTRACTS.md and the CHANGELOG are updated to say which candidates now have a hook.

## Approach and scope

Tickets in TODO.md (r1). T0 (worktree) superseded by D1 and D2: hook code was built in a plain copy under .artifacts and written into hooks/ as a finished file; T8 has no merge. Excluded: waiver wording (Q6 c), Codex hooks, application repos.

## Approval

r1 approved 2026-11-12 (owner via question tool): "Approve r1, no report". Includes T0 to T8 as in TODO.md r1, and the owner's OK for: worktree and branch creation, commits in the candidate and on main, the merge into main, verification_summary.py --run --write, the push and the reinstall. Excludes waiver wording (Q6 c), Codex hooks, application repositories.

## Outcome

Delivered 2026-11-12 as release 2.8.0-rc.38 (commit c7147e8, pushed; Claude plugin and Codex skills reinstalled from GitHub, V15). Partial until owner acceptance.
- Asked: follow-up 3 "do all the follow-ups"; agreed: agreement 1 (items 1-6); approved: r1, no report.
- Built: T1 checkpoint heading; T2 agreement check; T3 bulk-delete refusal; T4 styling and small-change notes; T5 worktree copy note; T6 pins; T7 docs and rc.38. T0 superseded (D1, D2) after the worktree could not carry the approval (E11) and a half-written live hook broke every write (E12, restored by the owner).
- Checks: full suite 1223 ran, 0 failed (V14, VALIDATION.md); validate.py PASS; fresh-session refusal while the agreement is pending observed by the owner (V17). Not observed live: the allowed case after "agreed" (tests only).
- Reviews: V8/V10 code review of T1-T6 (independent, both axes, findings fixed or documented); V13 whole feature (fixed); V18 reconciliation.
- Verdicts: items 1-6 verified; assumptions A1 and A2 partial (one untested case each); release line partial (allowed case live, owner acceptance).
- Not changed by owner decision: waiver wording (Q6 c). New hook candidates: 7 (E8/E9 approval wording in the same message, bold answers) and 8 (E10/E11 worktree and subagent approvals) in docs/RULE-CONTRACTS.md.
- Kept until acceptance: the fixture C:\Users\Cem\gate-fixture-rc38, the working copy .artifacts/2026-11-12-approval-gate-false-refusals/work, logs in that folder, the scratchpad backup of the rc.37 Codex skills.

- 2026-11-12: owner acceptance: "yes accepting it" (D3). A1/A2 tests added (V19). Fixture and working copy removed after acceptance.
