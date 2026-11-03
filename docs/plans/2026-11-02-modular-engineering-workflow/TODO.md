# Work state

This is the research/approval checkpoint, not the detailed implementation backlog. The user chose agreement approval before detailed planning (DECISIONS D3).

- [x] P1 — Inspect task history, current source, policy/report contracts, specialist routing and verification infrastructure. Evidence: FINDINGS E1–E5. Source inspection, not execution proof.
- [x] P2 — Independently evaluate engineering and writing sources with Codex and Claude Opus 5.5. Evidence: FINDINGS E6–E8. Initial disagreements are recorded.
- [x] P3 — Reconcile substantive objections and confirm the shared writing recommendation against the same actual candidates. FINDINGS E10 records agreement, corrections and detailed-plan conditions; user approval remains pending.
- [x] G1 — R1 accepted by the user's instruction to finish/review/test everything (D5). Evidence: DECISIONS D5.
- [x] P4 — Detailed specification, ticket order and verification seams recorded in PLAN. Preserve the implementation overview before code; exact runtime provider availability remains a verification condition. Evidence: PLAN "Implementation specification R1"; reviews/implementation-r1.html.
- [x] G2 — Additional approval pause explicitly waived for this task by D5. This is a task exception, not removal of the product gate. Evidence: DECISIONS D5.
- [x] P5 — Implemented, reviewed by both agents (R1, Codex R2/R3, final Claude review), behavior runs on both repos, retro, repairs. Evidence: FINDINGS E11–E20, V1–V3.
- [x] P6 — Delivered (partial): PLAN Outcome, VALIDATION.md, `reviews/delivery-r2.html` (r1 kept). Evidence: FINDINGS E21–E25, V7.

## Implementation tickets

| Ticket | Work and owner | Depends on | Acceptance / verification |
|---|---|---|---|
| T1 | Parent: capture baseline, protect owner edits and historical artifacts | None | R8/R9: observed baseline results retained; exact source identity known |
| T2 | Claude implementer: four phase skills, lightweight router, shared agreement/question/writing contracts and resume/status integration | T1 | R1–R6/R10: independent entry guards, two gates, scoped change handling, ticket and delivery procedures; static and actual scenario checks |
| T3 | Parent: optional central report content/helper and public renderer regression tests | T1 | R3/R7/R8/R10: sourced narrative/ticket/check/acceptance content, separate authority, unsafe/contradictory inputs rejected, old input output preserved |
| T4 | Parent: registration, package metadata, setup/release docs and verification scenario integration | T2,T3 | R1/R5/R9: twelve discoverable package skills; no accidental external dependency; coherent docs and required checks |
| T5 | Parent plus bounded evaluators: package, browser/visual when available, standalone and complete behavior checks | T4 | R2–R10: observe actual outcomes; separate tested/blocked/not verified; preserve original tests and references |
| T6 | Independent Claude reviewer and parent: review, repair and affected rechecks | T5 | R5/R9: actionable Standards and Spec findings resolved or explicitly limited, final worktree attribution inspected |
| T7 | Parent: final delivery record and central HTML snapshot | T6 | R7/R10: each criterion, ticket, change, check and review accounted for, limitations visible |

## Ticket states (2026-11-02, final)

| Ticket | State | Evidence |
|---|---|---|
| T1 Baseline and preservation | verified | PLAN "Baseline and attribution"; FINDINGS E9, E11 |
| T2 Phase skills, router, agreement and writing rules | verified | FINDINGS E12–E20 (behavior runs E1–A4; reviews) |
| T3 Central report content and reader-first layout | verified | `tests/test_task_report.py` (red→green); screenshots `.artifacts/.../checks/report-readability/after-*.png`; FINDINGS E15 |
| T4 Registration, metadata, docs | verified | V3: validator PASS (twenty skills); README/SETUP/UPGRADE/CHANGELOG updated (E19–E20) |
| T5 Package, browser and behavior checks | verified with limits | V1–V3; behavior runs E12–E18 and VALIDATION.md; browser suites NOT RUN (no Playwright); native host discovery not tested |
| T6 Independent reviews and repairs | verified | Claude R1 + final; Codex R1–R3; all findings applied except two recorded deferrals (E20) |
| T7 Delivery record and snapshot | verified | PLAN Outcome; VALIDATION.md; `reviews/delivery-r1.html` |
| Added by the user during the task | | |
| D6 Matt-style rewrite + reader-first report | verified | E15, E17 |
| D7/D10 Vendored skills as separate skills, one owner per rule | verified | E19, E20; `tests/test_vendored_specialists.py` |
| E16 Retro fixes (open_items, state line, handoff, parallel, …) | verified (static) | `tests/test_open_items.py`, `test_retro_findings_stay_fixed`; state line observed live in A2–A4 |
| D8 Both gates in one message | implemented, live run not triggered | A4 found an open choice, so the shortcut correctly did not apply |
