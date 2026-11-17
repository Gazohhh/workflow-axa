# TODO

Each ticket is built test first: its new tests fail before the change and pass after. Order: T0 (sort every mention, before any edit), then T1 (the rule set), then T3 (the hooks), then T2 (change the sorted mentions and add the search test, which can only pass once the hooks changed); T4 to T9 after T1 in any order; T10 last.

| Ticket | What | Status | Depends on |
|---|---|---|---|
| T0 | Sort every mention of the old file, before any edit | Verified | — |
| T1 | One rule set in WRITING.md | Verified | T0 |
| T2 | Change the sorted mentions, and the search test | Verified | T1, T3 |
| T3 | The report-read hooks point to WRITING.md (built in a temporary copy) | Verified | T1 |
| T4 | Word swaps and contractions become suggestions wherever they are enforced | Verified | T1 |
| T5 | The places that write for a person point to WRITING.md | Verified | T1 |
| T6 | Owner questions: meaning first, codes only as references | Verified | T1 |
| T7 | Rewrite requests use the rules (pstack L5) | Verified | T1 |
| T8 | A change only counts as small after it names what depends on it (pstack L6) | Verified | — |
| T9 | /spar: the start card offers the launches left; a new cap is above those used | Verified | — |
| T10 | Test entry point, reviews and live checks | Not started | T0-T9 |

### T0 — Sort every mention of the old file, before any edit
Status: Verified
Evidence: FINDINGS V0: 49 search hits at bcb76ec, each sorted into kind (i) or (ii) before any other file changed

What needs to happen: R3's sort. Search `SIMPLE-ENGLISH` over R3's paths (tracked text files only) and record each line in FINDINGS as kind (i), changes to WRITING.md, or kind (ii), stays, with the reason. `SIMPLE-ENGLISH.LICENSE` lines are kind (ii).

What should work: no mention in those paths is left unsorted.

Technical details: records only; no other file changes.

How to verify: the FINDINGS list has one entry per search hit at the start commit.

### T1 — One rule set in WRITING.md
Status: Verified
Evidence: FINDINGS V1; test_simple_english 10 OK, test_task_report 45 OK, validate PASS

What needs to happen: R1 and R6. Move SIMPLE-ENGLISH.md's twelve Document rules, The Reply, the Self-Check and the tells into WRITING.md under "Documents and reports" and the existing sections; reduce SIMPLE-ENGLISH.md to its modes, ASD-STE100 references, use-cases.md routing, word-swaps.md, licence and credit, and make it point to WRITING.md. The check keeps the name "Unslop" (D3). R6: WRITING.md's Unslop section names the full scope it runs on (new or changed tickets, PLAN, FINDINGS, DECISIONS, offers, reports, SPAR.md, docs and chat) and the text it never changes (history, quoted owner answers, already-presented approvals).

What should work: WRITING.md is the only file that states a common writing rule; "keep the meaning" comes first; "one word, one meaning" stays a rule; SIMPLE-ENGLISH.md points to WRITING.md; the Unslop scope covers R6's list and its preservation exceptions.

Technical details: skills/workflow/WRITING.md, skills/workflow/SIMPLE-ENGLISH.md, skills/workflow/simple-english/*; tests/test_simple_english.py (rewritten to the new owner, no assertion deleted to get a pass).

How to verify: R9's "only WRITING.md defines the common rules" test with its mutation fixture; a new test that fails until WRITING.md's Unslop scope names every R6 text kind and each preservation exception, and until SIMPLE-ENGLISH.md points to WRITING.md; test_simple_english.

### T2 — Change the sorted mentions, and the search test
Status: Verified
Evidence: FINDINGS V2; test_writing_mentions OK with its planted-mention test; nine related test files OK; validate PASS

What needs to happen: R3, after T1 and T3. Using T0's sorted list, change every kind-(i) line to WRITING.md (wait-what's read limit, its RULE-CONTRACTS row and tests/test_new_skills.py:129 together; CONTEXT.md owner row and glossary entry; RULE-CONTRACTS rows; WRITING.md:59; TASK-REPORT.md:22; word-swaps.md:56; render_report.py:1042 and 1047; README.md:35 and 59; writing-for-agents' tells pointer; tests/test_simple_english.py:100; tests/test_task_report.py:627-634).

What should work: a new search test fails on any `SIMPLE-ENGLISH` line in those paths that is not on its per-line keep-list (the test holds the list, including the `SIMPLE-ENGLISH.LICENSE` lines; the pattern is written so the test does not match itself; only tracked text files are searched).

Technical details: the files above; a new test in tests/test_simple_english.py or its own file.

How to verify: the search test fails on a planted extra mention and passes on the sorted tree.

### T3 — The report-read hooks point to WRITING.md
Status: Verified
Evidence: FINDINGS V3; built in a separate copy; test_phase_gate_hook 97 OK and test_read_evidence OK there and on main

What needs to happen: R3's hook part. hooks/phase_gate.py REPORT_GUIDES and hooks/read_evidence.py require a full read of WRITING.md (and SIMPLE-ENGLISH.md only where Strict or CHECK mode is used) before specify and deliver write reports.

What should work: a report written without reading WRITING.md is refused as today's gate refuses one written without SIMPLE-ENGLISH.md.

Technical details: this session loads hooks from D:\workflow-axa, so under AGENTS.md the change is built and tested in a temporary separate checkout and lands on main only after the hook tests pass; the copy is then removed. tests/test_phase_gate_hook.py (231, 235, 253, 265, 1303) moves to WRITING.md, each assertion keeping its purpose.

How to verify: test_phase_gate_hook and the read-evidence tests in the copy, then on main.

### T4 — Word swaps and contractions become suggestions
Status: Verified
Evidence: FINDINGS V4; test_task_report 46 OK with the mutation test; test_simple_english 11 OK

What needs to happen: R2 in every enforcing place: the moved Document rules 6 and 8, the moved Self-Check, The Reply, task_report.py (contractions and "ensure" become notes), rule-catalog.md in Plain-mode CHECK (Strict mode unchanged), and tests/test_task_report.py:277, 614, 633 rewritten.

What should work: a report with a contraction and "ensure" opens with no plain-English problem; a Plain-mode CHECK reports no violation for a contraction or "verify"; a Strict-mode CHECK still does.

Technical details: skills/codebase-map/scripts/task_report.py, render_report.py, skills/workflow/simple-english/rule-catalog.md, WRITING.md, tests/test_task_report.py.

How to verify: R9's report and CHECK fixtures, each with a mutation that brings a ban back and fails.

### T5 — The places that write for a person point to WRITING.md
Status: Verified
Evidence: FINDINGS V5; test_writing_mentions 4 OK; seven related test files OK; validate PASS

What needs to happen: R4. Record the list in CONTEXT.md as "Places that write for a person"; add a one-line pointer where one is missing (spar SKILL.md section 5 and SPAR-FILE.md, interrogate, rule-maker AUDIT.md and DIAGNOSE.md, resume, workflow-execute, ui-design, workflow/SKILL.md route notices, TASK-FOLDER.md, VISUAL-REVIEW.md, domain-modeling, no-comments); keep the existing ones.

What should work: every listed place points to WRITING.md and restates no rule.

Technical details: CONTEXT.md and the skill files named.

How to verify: R9's inventory test fails when a pointer is removed.

### T6 — Owner questions: meaning first, codes only as references
Status: Verified
Evidence: FINDINGS V6; test_owner_questions 4 OK; test_offers OK; test_approval_hook 144 OK

What needs to happen: R5. Grilling "How to ask" states the meaning-first rule and that a question must stand without its ids, keeping its exceptions; offers.py's presentation and question change together so the generated question leads with the meaning; /spar's conclusion and handoff ask owner decisions through grilling (no "O1-O5" lists whose meaning depends on codes).

What should work: an offer question and a /spar decision read plainly with every id removed.

Technical details: skills/grilling/SKILL.md, skills/workflow/scripts/offers.py, skills/spar/SKILL.md and SPAR-FILE.md, tests/test_offers.py, tests/test_spar.py.

How to verify: R9's id-at-start lint on generated fixtures, with a trailing-reference positive control.

### T7 — Rewrite requests use the rules (pstack L5)
Status: Verified
Evidence: FINDINGS V7; test_owner_questions 6 OK; five related test files OK; validate PASS

What needs to happen: R7: the workflow description trigger, the router row (read only, load WRITING.md, no task records, no offer), and the comparison with the source.

What should work: "rewrite this paragraph simpler" loads WRITING.md and keeps "may" as "may".

Technical details: skills/workflow/SKILL.md (description and router), WRITING.md, tests/test_flows.py or the router tests.

How to verify: the trigger and row tests; the lost-uncertainty fixture; the live check in T10.

### T8 — A change only counts as small after it names what depends on it (pstack L6)
Status: Verified
Evidence: FINDINGS V8; test_owner_questions 8 OK; five related test files OK

What needs to happen: R8: the lightweight rule in workflow/SKILL.md, the minimal offer's one-line assumption in workflow-specify, and code-review step 4b's new example.

What should work: replacing a private helper that other code calls is not called lightweight; a docs fix only tests read still is.

Technical details: skills/workflow/SKILL.md, skills/workflow-specify/SKILL.md, skills/code-review/SKILL.md, their tests.

How to verify: text tests for the rule, the minimal-offer line and the example; the live check in T10.

### T9 — /spar budget on the start card
Status: Verified
Evidence: FINDINGS V9; test_spar 34 OK; SKILL.md 1298 words

What needs to happen: the start card offers caps within the launches the owner has left, and a new cap given through "Continue sparring" must be above the launches already used.

What should work: run 5's card would have offered at most the owner's remaining 20, not 30.

Technical details: skills/spar/SKILL.md (SKILL.md must stay under 1,300 words), tests/test_spar.py.

How to verify: test_spar.

### T10 — Test entry point, reviews and live checks
Status: Not started

What needs to happen: one command that runs every R9 check; the full suite and validate; a review of the whole change by GPT-6.1 Sol and a fresh Claude until both pass; then R10's live checks, each batch only after the owner's OK and within a cap the owner sets, including the internal test the owner asked for.

How to verify: the review verdicts and live results recorded in FINDINGS.
