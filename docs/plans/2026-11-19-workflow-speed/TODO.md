# Tickets

All paths are relative to the worktree D:\workflow-axa-speed (branch speed/2.10 from main 1a0d523). Test output: .artifacts/2026-11-19-workflow-speed/ in the worktree. Commit after each green round (D2); no push or merge.

## Overview

| Ticket | What needs to happen | Status | Dependencies |
|---|---|---|---|
| T0 | Measuring script, baseline numbers and a baseline pilot | Verified | none |
| T1 | Approval hook: early exit, incremental transcript cache, one process | Verified | T0 |
| T2 | After-call hook: not on Read, old-task code loaded only when needed | Verified | T0 |
| T3 | Reading load: slim router, on-demand files, one owner per rule | In progress | T0 |
| T4 | Fewer stops: one-ticket agreement, one-round grilling, two-answer lightweight offer | Verified | T1, T3 |
| T5 | Review and checks: one reviewer for small diffs, reproducible findings, docs_check less often | Verified | T3 |
| T6 | Execution: recipe steps into the todo list, the brief is the whole bar, fresh context per ticket | Verified | T5 |
| T7 | Release notes and docs | Verified | T1, T2, T4, T5, T6 |
| T8 | After-measurement and live pilot comparison | Verified | T7 |
| T9 | Approval refusals give the real reason (Hooqd bug report) | Verified | none |

Parallel rounds: T1 + T2 + T3 (separate files), then T4 + T5, then T6, then T7, then T8. Each worker gets its ticket, the rules (AGENTS.md, CORE.md, tests/README.md), its exact files and the line "the bar in this brief is the whole bar".

## Tickets

### T0 — Measuring script, baseline numbers and a baseline pilot
Status: Verified

What needs to happen: add tools/measure_speed.py that reports (a) words the agent must read per path (router always-reads, bug path, lightweight path), (b) hook milliseconds for a read-only Bash call, a Read and an Edit on synthetic transcripts of 1k, 5k and 20k events, (c) owner stops in the bug path; record the baseline; run one live bug-fix pilot on today's version.

Technical details:
- Files: tools/measure_speed.py, tests/test_measure_speed.py (new). Must not change hooks/ or skills/.
- Test seam: the script's command line on a fixture tree; misses real host timing, covered by the pilot. TDD: yes.
- Pilot: throwaway fixture repo from tools/create_fixture.py under .artifacts/2026-11-19-workflow-speed/pilot/, live-pilot recipe, --max-budget-usd 5 per run, total cap 50 USD (D5).

How to verify:
- python -X utf8 -m unittest tests.test_measure_speed; python -X utf8 -I tools/measure_speed.py --json, saved as .artifacts/2026-11-19-workflow-speed/baseline.json

Verification: passed (V2, V5, V9, V10)

References:
- Supports: A1, A2, A5, A6
- Depends on: none
- Evidence: FINDINGS V9-V12; commits 122b2aa..3972094 on speed/2.10

### T1 — Approval hook: early exit, incremental transcript cache, one process
Status: Verified

What needs to happen: in hooks/approval.py, compute write targets first and return before read_events when there are none (item 1); cache the parsed transcript by file and byte offset so a call parses only new lines (item 2); start no second Python process for old tasks when no old pre-offer task exists (item 4).

What should work: every allow/refuse decision stays the same; a read-only Bash call's time no longer grows with transcript length; a corrupt or truncated cache is ignored and rebuilt; on any error writes are still refused.

Technical details:
- Files: hooks/approval.py, tests/test_approval_hook.py, tests/test_hook_speed.py (new). Must not change hooks/phase_gate.py, offers.py or hooks.json.
- Test seam: approval.py's hook protocol on synthetic transcripts. Characterisation first: record the decisions of existing fixtures before the change. The cache lives outside task records. TDD: yes.

How to verify:
- tests: test_approval_hook, test_hook_speed, test_shadow_comparison, test_session_failures, test_gate_regressions; measure_speed hook timings.

Verification: passed (V1, V2, V7, V9)

References:
- Supports: R1, A2, A3, A4
- Depends on: T0
- Evidence: FINDINGS V9-V12; commits 122b2aa..3972094 on speed/2.10

### T2 — After-call hook: not on Read, old-task code loaded only when needed
Status: Verified

What needs to happen: remove Read from the PostToolUse matcher (item 3); phase_gate.py's hook entry returns early without loading its full module when the project has no old pre-offer task and the event needs no fingerprint or style note.

Technical details:
- Files: hooks/hooks.json, hooks/phase_gate.py, tests/test_gate_notes.py, tests/test_phase_gate_hook.py, and tests/test_cutover.py and tests/test_package_contract.py only where they pin the matcher. Must not change approval.py.
- Test seam: hook command line plus hooks.json content; first prove by search that nothing depends on a Read fingerprint. TDD: yes.

How to verify:
- tests: test_gate_notes, test_phase_gate_hook, test_cutover, test_package_contract, test_required_reads.

Verification: passed (V1, V2, V9; Read kept in the matcher, E7)

References:
- Supports: R1, A2, A3
- Depends on: T0
- Evidence: FINDINGS V9-V12; commits 122b2aa..3972094 on speed/2.10

### T3 — Reading load: slim router, on-demand files, one owner per rule
Status: In progress

What needs to happen: the router reads SKILL.md, flows/INDEX.md and one recipe; the rare sections of TASK-FOLDER.md, VISUAL-REVIEW.md, SETUP.md, AUDIT.md and WRITING.md move into on-demand files with a one-line "read when" pointer (item 5); RULES.md no longer re-reads START.md and CORE.md (item 6); each repeated rule stays in its owner file per CONTEXT.md and other copies become one-line links (item 7); rules a script already checks shrink to one line naming the check (item 8). Phase skills stop pulling the whole "Always" list.

Technical details:
- Files: skills/workflow/**, the "read shared policies" lines of the four phase skills, skills/rule-maker/rules/READINESS.md, CONTEXT.md, tools/validate.py word ceilings if needed, and the text tests that pin moved sentences (test_simple_english, test_writing_mentions, test_flows, test_owner_questions, test_rules, test_engineering_rules, test_new_skills). A moved sentence keeps its test, pointed at its new file; no assertion is dropped.
- Test seam: validate.py, the text tests and measure_speed word counts. TDD: no (text moves; the existing tests are the characterisation).

How to verify:
- validate.py; full suite; measure_speed bug path at most 10k words.

Verification: failed: bug path before code is 17,858 words, target 10,000 (V10); tests pass (V9)

References:
- Supports: R2, A1, A3
- Depends on: T0
- Evidence: none

### T4 — Fewer stops
Status: Verified

What needs to happen: one-ticket work with nothing open records Agreement "not required" without asking (item 9); grilling names one round with a recommendation per question (item 10); the lightweight offer prints as one short message and its question has two answers, Approve and Change something, and the hook accepts that question (item 15, D1).

Technical details:
- Files: skills/workflow-clarify/SKILL.md, skills/grilling/SKILL.md, skills/workflow-specify/SKILL.md, skills/workflow/VISUAL-REVIEW.md (gate part), skills/workflow/scripts/offers.py, hooks/approval.py (answer recognition only), tests/test_offers.py, tests/test_approval_hook.py, tests/test_owner_questions.py.
- Test seam: offers.py present output and the hook on synthetic transcripts with the two-answer question; a three-answer offer keeps working. TDD: yes.

How to verify:
- tests: test_offers, test_approval_hook, test_owner_questions, test_shadow_comparison; measure_speed: one approval question for a one-ticket bug.

Verification: passed (V3, V9)

References:
- Supports: R3, A4, A6
- Depends on: T1, T3
- Evidence: FINDINGS V9-V12; commits 122b2aa..3972094 on speed/2.10

### T5 — Review and checks
Status: Verified

What needs to happen: code-review uses one reviewer covering both axes for a one-ticket diff without a blast-radius trigger, two otherwise (item 11); a finding counts only with a reproducing command or a concrete line and failure (item 12); docs_check keeps its readiness run, clarify and delivery check only changed files (item 13).

Technical details:
- Files: skills/code-review/SKILL.md, skills/workflow/AUDIT.md (review part), skills/workflow-execute/SKILL.md, skills/workflow-deliver/SKILL.md, the docs_check line of skills/workflow-clarify/SKILL.md, tests/test_new_skills.py, and completion_check.py with tests/test_completion_check.py if it must accept one reviewer.
- TDD: yes for completion_check; text tests for the rest.

How to verify:
- tests: test_new_skills, test_completion_check; validate.py.

Verification: passed (V3, V9)

References:
- Supports: R4, A3
- Depends on: T3
- Evidence: FINDINGS V9-V12; commits 122b2aa..3972094 on speed/2.10

### T6 — Execution
Status: Verified

What needs to happen: workflow-execute copies the recipe's steps into the todo list; every subagent brief starts with "the bar in this brief is the whole bar: add no check, gate or review round above it"; each ticket of multi-ticket work runs in a fresh subagent or after /clear (items 14, 16).

Technical details:
- Files: skills/workflow-execute/SKILL.md, skills/workflow/flows/*.md (step wording only), skills/workflow/SPECIALISTS.md, tests/test_flows.py.
- TDD: no (instruction text); text tests prove the wording.

How to verify:
- tests: test_flows; validate.py.

Verification: passed (V6, V9)

References:
- Supports: R5, A3
- Depends on: T5
- Evidence: FINDINGS V9-V12; commits 122b2aa..3972094 on speed/2.10

### T7 — Release notes and docs
Status: Verified

What needs to happen: CHANGELOG entry for an unreleased 2.10.0 candidate, a tests/README.md section, docs/ARCHITECTURE.md and docs/RULE-CONTRACTS.md where hooks or gates changed, README.md counts if they changed. No version bump and no VALIDATION.md rewrite.

How to verify:
- validate.py; full suite.

Verification: passed (V8, V9)

References:
- Supports: A3
- Depends on: T1, T2, T4, T5, T6
- Evidence: FINDINGS V9-V12; commits 122b2aa..3972094 on speed/2.10

### T8 — After-measurement and live pilot comparison
Status: Verified

What needs to happen: rerun measure_speed; run the same live bug-fix pilot on the candidate; compare with T0 in FINDINGS (time, tokens, cost, tool calls, hook time, stops, result); report the pilot total against 50 USD.

How to verify:
- A1, A2, A5 and A6 numbers in FINDINGS; the pilot fixture's tests green in both runs.

Verification: passed (V10, V11)

References:
- Supports: A1, A2, A5, A6
- Depends on: T7
- Evidence: FINDINGS V9-V12; commits 122b2aa..3972094 on speed/2.10


### T9 — Approval refusals give the real reason (Hooqd bug report)
Status: Verified

What needs to happen: when a git operation or MCP tool is refused and an offer of the project lists that operation but is not usable, the refusal names that offer and the reason validated() already found (not presented, presentation not the end of the reply, no owner answer after it, a "/approve N" with extra text), instead of "no approved offer lists …". The phrase "or ask them for this one step" goes (D11); the refusal says how to present: the question tool with the `record.py offer present <task> <id> --question` output as the question, or the exact `offer present` text at the end of the reply. A "/approve N" that starts a longer message still approves nothing, and the reason says to send it alone or click the button (D10). workflow-specify step 5 and VISUAL-REVIEW.md say the question tool is the default where the host has one, and that a host message tool (such as send_to_user) is not a presentation.

Technical details:
- Files: hooks/approval.py, tests/test_approval_hook.py, skills/workflow-specify/SKILL.md, skills/workflow/VISUAL-REVIEW.md, docs/RULE-CONTRACTS.md if a contract sentence changes.
- Test seam: the hook process on synthetic transcripts replaying the Hooqd steps 1-5. TDD: yes, a failing test per step first.

How to verify:
- test_approval_hook, test_shadow_comparison, test_session_failures, test_gate_regressions, test_hook_speed, test_owner_questions; validate.py.

Verification: passed (V9, V12)

References:
- Supports: D9-D11, A3, A4
- Depends on: none
- Evidence: FINDINGS E15; FINDINGS V9-V12; commits 122b2aa..3972094 on speed/2.10
