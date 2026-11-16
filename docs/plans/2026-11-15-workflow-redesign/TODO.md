# Tickets

**Order:** tickets run strictly in the order listed. A ticket starts only after the previous one is `done`, which requires both verdicts (Opus and Astra: Agree) recorded in FINDINGS. Dependencies are listed for clarity, not to allow reordering.
**Every ticket's acceptance includes:** its targeted tests; `python -X utf8 -I tools/validate.py` exit 0; and, at the end of each checkpoint, the full suite. A ticket changes its own manifest entries, affected tests and the docs that describe what it changed, so the package validates after every ticket and no independent protection is removed without its replacement in the same ticket.

State: todo / doing / review (waiting for Astra) / done.

## Checkpoint 1: contracts, fixtures, baseline
| ID | Ticket | Depends | Acceptance | State |
|---|---|---|---|---|
| T1 | Session fixtures: minimal sanitised reproductions of the session failures (P1 "no need for report", P3 missing revision, N4 record write switching task) as hook-input fixtures | — | fixtures load in a test that reproduces each failure against rc.39's phase_gate; no private paths, secrets or real names | done (tests/test_session_failures.py) |
| T2 | `digest_sessions.py`: counts of approval messages, denials by reason and process-only turns; baseline metrics from up to 15 local rc.39 sessions (counts only, no content) in FINDINGS | — | unit tests on a synthetic transcript; baseline table recorded | done (FINDINGS V2) |
| T3 | Contract IDs for the redesign in docs/RULE-CONTRACTS.md; P1–P10, N1–N6, G1–G5 each mapped to a fixture/test or a "not testable offline" note | T1 | every finding mapped; docs_check passes | done (RULE-CONTRACTS "Redesign contracts") |

## Checkpoint 2: validator and tooling
| ID | Ticket | Depends | Acceptance | State |
|---|---|---|---|---|
| T4 | validate.py reads registered skills from plugin.json (G2); per-file word budgets advisory with one default ceiling (G5); hand-kept inventories removed **together with** the independent contract suite `tests/test_package_contract.py` (skills, hook registrations and scripts, LICENSE folders, renderer assets, key tests) | T3 | adding a dummy skill touches only plugin.json + folder (+ stated counts); deleting a key test or skill fails the contract suite | done |
| T5 | verification_summary.py: non-zero exit when a check failed (G1); imported logs bound to commit + dirty hash, marked stale on mismatch; `--check` separate from `--write` (no `--write` run) | T4 | tests for failure exit, stale detection | done |
| T6 | One shared required-read parser (G3) with `paths=` applicability, used by docs_check and the gate | T5 | docs_check and gate tests pass; `paths=` cases | done |

## Checkpoint 3: quick relief in today's gate
| ID | Ticket | Depends | Acceptance | State |
|---|---|---|---|---|
| T7 | phase_gate: report waiver from any owner message in the task (P1, interim); quote composition (P2); one pending plan → missing revision doesn't block (P3); exact refusal reasons (N1); record writes never switch the current task (N4); P5, P10 | T6 | session-fixture outcomes (a) "Agree no need for report…" then "Approve" → 0 extra owner messages; (b) r4 without revision then "approve r4, no report" → 0 extra; (c) other task's record write then authorised commit → 0 extra; no new regex families | done |
| T8 | N2: on a no-report route the report guides are not required reads (conditional-read fix); plain_reply never adds punctuation complaints | T7 | regression tests for both | done |

## Checkpoint 4: recipes, fallbacks, classification, rules pass
| ID | Ticket | Depends | Acceptance | State |
|---|---|---|---|---|
| T9 | `skills/workflow/flows/`: INDEX.md (only place for signals), TEMPLATE.md, 9 recipes with the adopted pstack/Pocock principles; validator index check; labelled classification prompts per recipe (`tests/behavioral/`) and one behavioural fixture each | T8 | index↔files, `uses` registered, template excluded; prompts and fixtures present | done |
| T10 | `skills/workflow/FALLBACKS.md` (13 named fallbacks, one-line format, what may pause work); workflow SKILL.md classification (three fields, "not sure" rule, one question, Inspect/Other); gate-compatible text only (§14 transition rule) | T9 | behavioural cases; no backend case loads UI files | done |
| T11 | Rules library pass: full module checklist (FINDINGS table); CORE comment rules 1–4 and defaults; CSS copies → one pointer to the shared DESIGN.md contract; OPERATIONS diagnostic allowance; POLICY protection vs preference; READINESS / START / POLICY / rule-maker SETUP+SKILL / workflow RULES / resume / child handoff readiness text (ask/skip parts candidate-only until cutover); version.json, CHANGES, SHA manifest | T10 | checklist covers all 29 files; rules tests and manifest pass | done |

## Checkpoint 5: offer model and CSS switch
| ID | Ticket | Depends | Acceptance | State |
|---|---|---|---|---|
| T12 | `settings.py`: single reader (missing/invalid → off) and `css on/off`; global_policy adds the settings line and creates the file only if missing (code only, no `--apply`) | T11 | malformed/unknown → off; reinstall keeps value | done |
| T13 | record.py `offer`: create, present (canonical rendering + hash, CSS display line excluded), approve (decision reference), supersede, revoke, derive (child subset), presentation decision `asked/html-first/chat` | T12 | offer lifecycle tests (§11) | done |
| T14 | `hooks/approval.py` offer checker: presentation evidence, answer forms (button, `/approve <id>`, `/report <id>`, fixed list), qualified answers → narrowed offer, `/wait-what` non-answer, provenance re-validation, fail closed; kept safeguards (git, installs, bulk delete); live CSS check; settings protection bound to the exact Yes; rules question pause | T13 | all §11 adapter, CSS and settings negative cases | done |
| T15 | Shadow comparison against phase_gate on the session fixtures and the gate regression corpus; every difference classified | T14 | no unexpected difference | done (tests/test_shadow_comparison.py) |
| T16 | **Pre-cutover host gate:** first the minimum offer-producing instructions in the candidate (workflow-specify produces the offer + the one question, VISUAL-REVIEW offer contract, ui-design CSS-switch text), then live observations in isolated host configurations (candidate loaded with `--plugin-dir` / a separate T3 thread; the owner's installed environment untouched): presentation event, three answer forms, child task, adapter failure recovery, settings loading, and a legacy `Approval:` task; within decision B | T15 | observations recorded as observations; any failure fixed before T17 | done (FINDINGS "T16 host observations"; D4–D6) |
| T17 | Cutover: hooks.json registers approval.py, which dispatches tasks with legacy `Approval:` lines to the repaired phase_gate checking from the first moment; offer/CSS/skip text activated (T10/T11/T16 candidate parts) | T16 | legacy-task case passes at cutover; no active file still requires Approval lines, forbids all CSS or recommends comments (the run-17 conflicts: VISUAL-REVIEW, router, RULES.md, AUDIT.md); the offer text defines operations as protected actions only (git writes, MCP tools); full suite; validate | done (FINDINGS T17, V10) |

## Checkpoint 6: remove machinery
| ID | Ticket | Depends | Acceptance | State |
|---|---|---|---|---|
| T18 | Completion-evidence check moved from plain_reply into workflow-deliver (script or checklist) with tests | T17 | tests | done (completion_check.py; FINDINGS T18) |
| T19 | Retained legacy checker (scope corrected with Astra: all 109 phase_gate functions are reachable and ~30 are shared helpers of approval.py, so nothing is deleted or renamed): phase_gate.py header as the retained legacy checker and shared library; ownership map of every check in RULE-CONTRACTS; a regression that the offer route never calls legacy approval logic; the retirement condition (two releases plus diagnostics) in RULE-CONTRACTS and UPGRADE | T18 | ownership map complete; regression passes; suite | done |
| T20 | Remove plain_reply, phase_reads, truncated_read with their tests; duplicate_skills diagnose-only | T19 | suite; validate | done (FINDINGS T20, V11) |

## Checkpoint 7: skills packaging
| ID | Ticket | Depends | Acceptance | State |
|---|---|---|---|---|
| T21 | `resume` skill (status / continue / handoff) replacing task-status and resume-task; workflow-doctor → rule-maker `diagnose`; plugin.json, tests, README/UPGRADE mapping in the same ticket | T20 | package and contract suite | done (FINDINGS T21) |
| T22 | Unregister implement-spec, retro, simple-english (archived with LICENSE; digest_sessions and simple-english reference kept); VENDORED-SKILLS | T21 | licences intact | done (joint gate with T23; FINDINGS) |
| T23 | New `/interrogate`, `/no-comments`, `/wait-what`; code-review checks (comments, reader load, blast radius); 19 registered | T22 | package tests; one observed interrogate run on a seeded-bug fixture; joint gate with T22: validate PASS, full suite 0 failures, Opus and Astra agree on both | done (joint gate with T22; observed run unmet pending the owner's run budget) |
| T24 | Phase skills simplified further: clarify, specify, execute, deliver (remaining gaps); VISUAL-REVIEW and ui-design trimmed beyond the T16 minimum; TASK-FOLDER without task switching | T23 | behavioural cases | done (FINDINGS T24, V14) |

## Checkpoint 8: docs, pilot
| ID | Ticket | Depends | Acceptance | State |
|---|---|---|---|---|
| T25 | Docs: README, ARCHITECTURE, RULE-CONTRACTS, CONTEXT glossary, EVALUATION, docs/DESIGN, CHANGELOG, UPGRADE (old names, rollback, legacy approvals), VALIDATION (source-bound only); version 2.9.0-rc.1 | T24 | docs tests; validate | done (FINDINGS T25, V15) |
| T26 | Pilot: candidate against worktrees of D: repos (no installs, no commits), offline hook scenarios plus live runs within decision B; matched measurements against the T2 baseline | T25 | results in FINDINGS | done (contextual pilot; FINDINGS T26, V16) |

## Release handoff (not part of implementation; owner-only)
Commit, push, reinstall and `global_policy.py --apply` are not done. Delivery reports separately: what's implemented, verification gaps, and these unperformed release actions.

## Cleanup
Pilot worktrees are removed only when they're explicitly disposable and task-owned, their evidence is retained in FINDINGS, `git status` shows no changes worth keeping, and nothing else uses them.
