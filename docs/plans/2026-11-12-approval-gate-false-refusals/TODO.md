# Tickets (r1)

All hook tickets are built in an isolated candidate: a Git worktree of this repository at `.artifacts/2026-11-12-approval-gate-false-refusals/candidate` on branch `gate-rc38` (created by T0). Running sessions load hooks from the plugin cache, but AGENTS.md asks for a separate candidate location before hook changes. The candidate is merged into main only in T8.

## Overview

| Ticket | What needs to happen | Status | Dependencies |
|---|---|---|---|
| T0 | Prerequisite: create the isolated candidate worktree and record its baseline | Not started | none |
| T1 | The gate finds the checkpoint under any "Current checkpoint" heading | Not started | T0 |
| T2 | Code changes wait for a recorded agreement | Not started | T1 |
| T3 | Bulk deletes of test output are refused | Not started | T2 |
| T4 | Notes on new CSS and on new tags or classes in a small change | Not started | T3 |
| T5 | A clear message when a linked worktree's PLAN copy differs | Not started | T4 |
| T6 | Regression pins for the reproduced Altinstar cases | Not started | T5 |
| T7 | Documents and version 2.8.0-rc.38 | Not started | T6 |
| T8 | Merge, verify, publish, reinstall and check in a fresh session | Not started | T7 |

## Tickets

### T0 — Prerequisite: create the isolated candidate worktree and record its baseline
Status: Not started

What needs to happen: after approval, commit this task's records on main by explicit paths (never the staged 2026-11-11 records), then `git worktree add .artifacts/2026-11-12-approval-gate-false-refusals/candidate -b gate-rc38` from that commit, so the candidate holds the task's PLAN with its Approval line. Records are updated only on main; the candidate never edits or commits files under docs/plans/. Run validate.py and the full suite in the candidate as the baseline. Enables T1-T7.

What should work:
- An edit in the candidate passes the gate (its PLAN copy carries the approval).
- The candidate passes validate.py and the suite before any change, or each failure is recorded by name.
- The main checkout's staged 2026-11-11 records stay staged and untouched.

Technical details:
- May change: the records commit on main (this task folder only), the new worktree and branch. TDD: no (setup).

Documents: none

How to verify:
- `git worktree list`; `git -C <candidate> log -1`; baseline logs in .artifacts/2026-11-12-approval-gate-false-refusals/

Verification: not run

References:
- Supports: agreement 1 "built in a separate copy"; plan review finding T0/T8
- Depends on: none

### T1 — The gate finds the checkpoint under any "Current checkpoint" heading
Status: Not started

What needs to happen: `checkpoint()` in hooks/phase_gate.py accepts a Markdown heading of any level whose text starts with "Current checkpoint" (`### Current checkpoint (D4)`, `## Current checkpoint (2026-10-09)`) and stops at the next heading of the same or higher level. Without such a heading it behaves as today.

What should work:
- `### Current checkpoint (D4)` plus an old "approved r7" later in the PLAN: the current approval decides (E2).
- `## Current checkpoint (date)` (used by 2026-10-09-workflow-v2 and 2026-10-30-rules-audit-design-kit): only the checkpoint section is read (pinned).
- `## Current checkpoint`: unchanged.

Technical details:
- May change: hooks/phase_gate.py (checkpoint), tests/test_gate_regressions.py. Must not change: other hooks.
- Test seam: the gate script fed a synthetic transcript and an Edit event (existing harness). Misses live host differences; covered by T8.
- TDD: yes.

Documents: none

How to verify:
- `python -X utf8 -m unittest discover -s tests -p "test_gate_regressions.py"` in the candidate, red then green.

Verification: not run

References:
- Supports: agreement 1 item 4; FINDINGS E2
- Depends on: T0

### T2 — Code changes wait for a recorded agreement
Status: Not started

What needs to happen: on the full route, after the approval check passes, the gate refuses the writes it already checks (project files and git writes) when the task uses the two-gate checkpoint (an `Approval (gate two)` line) and its Agreement line (`Agreement (gate one):` or plain `Agreement:`) is missing or does not say agreed, waived, legacy or "not required". "pending", "proposed", "not agreed" and "not approved" count as missing. Tasks with an old single-gate `Approval:` line or a legacy approval are not checked. Lightweight edits and the small change route are not checked. A combined "yes to both" answer is recorded on both lines by workflow-clarify; the check reads the Agreement line only. The refusal names the missing line and says to record the owner's agreement answer (workflow-clarify step 4).

What should work:
- `Approval (gate two): r1 approved ...` + `Agreement (gate one): pending`: refused with that message.
- Same with `Agreement (gate one): agreed ...` or plain `- Agreement: agreed ...`: allowed as today.
- Single-gate `- Approval:` task (for example 2026-11-03-audit-hardening) or legacy approval: allowed as today.
- Lightweight line or small change: unaffected.

Technical details:
- May change: hooks/phase_gate.py (one check next to the APPROVAL/NEGATIVE patterns, extending NEGATIVE with "not agreed"), tests/test_phase_gate_hook.py and tests/test_gate_regressions.py helpers (add a default `Agreement (gate one): agreed` line so existing allowed cases stay allowed; keep no-Agreement cases only where a test expects the refusal), and any test in test_followup_boundaries.py, test_rc3_reliability.py, test_session_recovery.py that builds a two-gate PLAN through those helpers. Must not change: the approval quote rules (Q6 c).
- Test seam: as T1. Misses whether the recorded agreement covers the work (instructions only).
- TDD: yes, one test per case above.

Documents: docs/RULE-CONTRACTS.md (in T7)

How to verify:
- test_gate_regressions.py, test_phase_gate_hook.py, test_followup_boundaries.py, test_rc3_reliability.py, test_session_recovery.py: red for the new cases first, then all green.

Verification: not run

References:
- Supports: agreement 1 item 1; Q7b a; plan review findings T2
- Depends on: T1

### T3 — Bulk deletes of test output are refused
Status: Not started

What needs to happen: in an active gate session (after the transcript scan and the active check in `judge`, using all targets before the `.artifacts` exemption filter), the gate refuses `git clean` (except `git clean -n` / `--dry-run`), a delete of the `.artifacts` folder itself, and a delete with a wildcard under `.artifacts`. A delete of named files or named folders under `.artifacts` stays allowed (ARTIFACTS.md cleanup). The message says to delete named items and follow ARTIFACTS.md.

What should work:
- Refused: `git clean -fdx`, `rm -rf .artifacts`, `rm -rf ./.artifacts/`, `rm -rf D:/workflow-axa/.artifacts`, `rm .artifacts/*`, `rm -rf .artifacts/task/*.png`, `Remove-Item .artifacts\* -Recurse`, `cd .artifacts && rm *`.
- Allowed: `rm .artifacts/task/a.txt`, `rm -rf .artifacts/task/old-run`, `git clean -n`.

Technical details:
- May change: hooks/phase_gate.py (reuse shell_writes' REMOVERS/DELETING parsing; one check in judge), tests/test_gate_regressions.py.
- Test seam: as T1 with Bash and PowerShell events. Misses deletes the parser cannot see (scripts, aliases): documented limit.
- TDD: yes.

Documents: skills/workflow/SETUP.md hook table (in T7)

How to verify:
- test_gate_regressions.py new cases, red then green.

Verification: not run

References:
- Supports: agreement 1 item 3; Q9 a
- Depends on: T2

### T4 — Notes on new CSS and on new tags or classes in a small change
Status: Not started

What needs to happen: in an active session, the existing PostToolUse output of phase_gate.py (the `additionalContext` note it already prints) adds one line when an Edit, Write or MultiEdit of an application file adds a style cue from `skills/ui-design/scripts/review_ui_diff.py` PATTERNS (stylesheet rule, `<style>`, `style=`): ask DESIGN.md rule 4's question or name the existing class. On the small change route it also notes a new tag or class attribute in a listed file. "Adds" means present in the new text and absent from the replaced text (Edit/MultiEdit: old_string vs new_string; Write: the file's committed version, or none if new). Application file: any project file except Markdown, docs/plans, .artifacts and test files (tests/, test/, *.test.*, *.spec.*). It never refuses.

What should work:
- Edit adding `.btn { color: red }` to a .scss file or `style="..."` to a .html/.tsx file: one note line.
- Edit of a .md file or a test file, or an edit that keeps an existing style unchanged: no note.

Technical details:
- May change: hooks/phase_gate.py (PostToolUse branch), tests (a new test file allowed). Must not change: hooks.json registrations (the existing PostToolUse registration already covers Edit|Write|MultiEdit).
- Test seam: phase_gate.py fed a PostToolUse event; asserts the note or its absence. Misses CSS-in-JS and computed styles (cues only). Timing: runs inside the existing 5-second hook timeout; the test measures a large-file case.
- TDD: yes.

Documents: docs/RULE-CONTRACTS.md, skills/workflow/SETUP.md (in T7)

How to verify:
- The new tests red then green.

Verification: not run

References:
- Supports: agreement 1 item 2; Q8 a
- Depends on: T3

### T5 — A clear message when a linked worktree's PLAN copy differs
Status: Not started

What needs to happen: when a write in a linked worktree is refused and the main checkout's PLAN.md for the same task differs from the worktree's copy, the refusal says the two copies differ and that approval is read from this worktree's own records, instead of asking the owner to approve again. The refusal itself is unchanged.

What should work:
- Linked worktree with a differing PLAN copy: refused; message names both paths and says they differ.
- Identical copies: message as today.

Technical details:
- May change: hooks/phase_gate.py (the worktree refusal message), tests/test_gate_regressions.py.
- Test seam: as T1 with a temporary repository and a linked worktree. TDD: yes.

Documents: none

How to verify:
- test_gate_regressions.py new case, red then green.

Verification: not run

References:
- Supports: agreement 1 item 5; FINDINGS E4
- Depends on: T4

### T6 — Regression pins for the reproduced Altinstar cases
Status: Not started

What needs to happen: tests only. Pin today's behaviour for E3a (a report named only inside an answered approval question counts as presented, rc.4) and E1 ("R7" in a requirements table and "D4-R6" are not revisions). If a pin fails, stop and report it to the owner as a new defect.

Technical details:
- May change: tests/test_gate_regressions.py. TDD: no (characterization of agreed current behaviour).

Documents: none

How to verify:
- test_gate_regressions.py.

Verification: not run

References:
- Supports: agreement 1 item 6; FINDINGS E1, E3
- Depends on: T5

### T7 — Documents and version 2.8.0-rc.38
Status: Not started

What needs to happen: docs/RULE-CONTRACTS.md (agreement check, delete refusal and CSS notes now have hooks; candidates 1 and 6 stay instructions only by owner decision; known gaps), the `description` in hooks/hooks.json, skills/workflow/SETUP.md hook table, docs/ARCHITECTURE.md if it lists hook checks, CHANGELOG.md rc.38, UPGRADE.md, README.md version, tests/README.md, version fields (plugin.json, rules version.json package_version, render_report.py RENDERER_VERSION, tests/behavioral/*.json candidate_version). Rules stay 1.8.8 unless a rules file changes.

Technical details:
- May change: the files listed. TDD: no (docs).

Documents: listed above

How to verify:
- validate.py PASS; docs_check . 0 blocking.

Verification: not run

References:
- Supports: agreement 1 release line; plan review finding T7
- Depends on: T6

### T8 — Merge, verify, publish, reinstall and check in a fresh session
Status: Not started

What needs to happen: full suite and validate.py in the candidate; whole-feature review (code-review, fresh subagent); commit the candidate's code on gate-rc38; merge gate-rc38 into main (fast-forward when possible, else a merge commit; the candidate never touched docs/plans, so records do not conflict; the staged 2026-11-11 records stay staged); `verification_summary.py --run --write VALIDATION.md`; commit by explicit paths and push workflow-axa; update the Claude plugin from the gazohhh marketplace and replace the 21 Codex skill folders from a fresh GitHub clone; remove the candidate worktree and branch after acceptance.

What should work:
- All checks pass on main; the installed plugin equals GitHub.
- Human check: in a fresh Claude Code session after the restart, in a throwaway fixture repository from tools/create_fixture.py (not this repository), a code write is refused while the fixture task's Agreement line is pending and allowed once it says agreed.

Technical details:
- May change: VALIDATION.md, task records; main via merge. Must not change: application repositories.
- Steps that need the owner's OK (AGENTS.md), asked for with this plan's approval: worktree and branch creation, commits in the candidate and on main, the merge into main, verification_summary.py --run --write, the push, and the reinstall.
- TDD: no (verification).

Documents: VALIDATION.md

How to verify:
- python -X utf8 -I tools/validate.py; python -X utf8 -m unittest discover -s tests -p "test_*.py"
- Human check: the fresh-session fixture check, after the reinstall.

Verification: not run

References:
- Supports: agreement 1 release line; plan review finding T8
- Depends on: T7