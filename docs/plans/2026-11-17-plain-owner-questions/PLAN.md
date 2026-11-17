# Owner questions in plain words, and one writing rule set

## Current checkpoint
- Updated / phase: 2026-11-17; the plan is written and GPT is checking it; you approve it once GPT and the coordinator both accept it; shipped in 2.9.0-rc.3 (2026-11-17, docs/plans/2026-11-17-release-rc3)
- Rules: READY (AGENTS.md project rules; shared START, CORE, READINESS)
- Recipe: feature; modifiers none. It changes how every skill writes what a person reads and how it asks the owner to decide. Scope: the task. Classification question: not asked
- Agreement (gate one): proposed. The design was agreed in a spar (FINDINGS S1, both models accepted S7) and the owner chose to turn it into this plan (D4); the owner approves the plan once GPT and the coordinator both accept it (D5)
- Offer: #1 approved (owner, question tool, 2026-11-17); approving it also approved the plan
- Implementation: T0-T9 verified; T10's checks, reviews and live checks done (FINDINGS V11-V13): all five live checks pass after the V13 fix
- Verification / owner acceptance: full suite 1532 OK, validate PASS; reviews by GPT-6.1 Sol and a fresh Claude passed after round 2; live checks and owner acceptance not run
- Blockers: none
- Changed files: none. Work happens on D:\workflow-axa main; hook changes are first built in a temporary separate copy (T3)

## Goal

The owner, 2026-11-17, after run 5:

> "Some questions I get are like: 'Do you accept S2 with the decisions of T2?' I have no idea what that is. I need to see what S2 and T2 are; I need this to be simplified. The tickets are made, yes, but present it to me humanly without talking in tickets. You can of course refer to the ticket, but when it comes to me making a decision based on that, I don't want to see that the reference is important, but plain English: unslop it, no slop. Also the writing in tickets and documents all needs to be unslopped, and the SPAR.md as well. Also check that it uses the grilling skill: it asked me no questions besides the spar questions, and I see decisions for me not in grilling style."

And: "If you could do this test yourself internally after we are done merging." And: "Unslop is meant for everything and simplification of language in general, not just spar." And: "Is unslop and simple English not the same? Can't that be one instead of two?"

The owner also chose to fix pstack's two weak live results before the rc.3 release (rc3-merge D4).

## What changes for the owner

- Every question you answer reads plainly. It says what is going on and what each answer does. A code like "D31" or "T6" may appear only at the end, as a reference, and the question still makes sense without it.
- Every decision reaches you in the same form: numbered, two to four lettered choices, and a recommendation with its trade-off. A plain factual question ("where is the file?") stays a plain question.
- Everything the skills write for a person follows one rule set in one file, `skills/workflow/WRITING.md`. Its check keeps the name "Unslop" (D3).
- Fixed word swaps (always "make sure that" for "verify", no contractions) become suggestions. Keeping the meaning comes first (D2 Q3).
- When you ask for a piece of writing to be rewritten or simplified, without a code change, the same rules are used, and no plan or ticket is made (D2 Q2).
- A change only counts as "small" after it says what else depends on it.

## Agreement

Agreed design: S7, accepted word for word by GPT-6.1 Sol and Claude Opus 5.5 (FINDINGS S1). In short:

- R1 One rule set. WRITING.md owns every common writing rule and the check: who reads, order, cut, keep the meaning (it wins over every other rule), plain words, the tells, owner questions, the cold-reader check, which state, and a "Documents and reports" section with SIMPLE-ENGLISH.md's twelve Document rules, The Reply, the Self-Check and the tells. "One word, one meaning" stays a rule. SIMPLE-ENGLISH.md keeps only the strict and CHECK modes, the ASD-STE100 references, the use-cases.md routing, word-swaps.md as a suggestion list, its licence and its credit; it defines no common rule and points to WRITING.md.
- R2 Suggestions, not bans (Q3), everywhere they are enforced: rule 8's fixed swaps and rule 6's contraction ban in the moved Document rules; the moved Self-Check ("fix each hit" becomes "consider each hit"); The Reply's "No contractions"; skills/codebase-map/scripts/task_report.py (a contraction and "ensure" become notes, not problems, so `--open` and `--validate-input` no longer fail on them); Plain-mode CHECK through simple-english/rule-catalog.md (rule 4.2 and the Word Choice entries become suggestions, like modals already are; Strict mode keeps them as rules); and the tests that expected the bans (tests/test_task_report.py:277, 614, 633), rewritten, not deleted. A swap that changes the meaning is never made.
- R3 Nothing points at the old place. Every mention of `SIMPLE-ENGLISH` in skills/, hooks/, tests/, tools/, docs/ (outside docs/plans and docs/archive), CONTEXT.md, README.md, AGENTS.md and VENDORED-SKILLS.md is sorted before any edit: it relies on a moved rule, so it changes to WRITING.md; or it concerns what stays (modes, ASD-STE100, use-cases.md, word-swaps.md, the credit, the LICENSE and UNSLOP.LICENSE), so it stays. Named in advance: wait-what's read limit with its contract row and test (changed together so wait-what may read WRITING.md); the report-read hooks hooks/phase_gate.py REPORT_GUIDES and hooks/read_evidence.py; the hook tests in tests/test_phase_gate_hook.py; tests/test_simple_english.py; tests/test_task_report.py:627-634; CONTEXT.md's owner row and glossary entry for the tells; docs/RULE-CONTRACTS.md's rows; WRITING.md:59; skills/codebase-map/TASK-REPORT.md:22; simple-english/word-swaps.md:56; render_report.py:1042 and 1047; README.md:35 and 59; writing-for-agents' tells pointer. A test searches those paths for `SIMPLE-ENGLISH` and fails on any line not on its keep-list; the keep-list is per exact line, lives in the test, and lists `SIMPLE-ENGLISH.LICENSE` explicitly.
- R4 Where the rules are referenced (Q1): only the places that write something a person reads, listed once in CONTEXT.md as "Places that write for a person", each pointing to WRITING.md without restating it. The list: grilling "How to ask"; spar's start card, frame line, progress line, conclusion and handoff, and SPAR-FILE.md; wait-what; resume status and handoff; rule-maker AUDIT.md proposals and DIAGNOSE.md results; ui-design kit findings and plan/report content (application UI copy stays excluded); interrogate's three lists; code-review's report and BLAST-RADIUS.md's impact report; plan-review findings; codebase-map SKILL.md, TASK-REPORT.md and render_report.py; workflow-clarify's agreement request; workflow-specify's tickets, offer and question, and offers.py's generated text; workflow-execute's progress and ticket summaries; workflow-deliver's records and reply; workflow/SKILL.md route notices, TASK-FOLDER.md records and handoffs, VISUAL-REVIEW.md; writing-for-agents' tells pointer; domain-modeling glossary and ADR prose; no-comments' final report.
- R5 Owner questions. Every decision question follows grilling "How to ask": numbered, two to four lettered options, a recommendation with its trade-off; the title and first sentence carry the meaning; an id appears only after the meaning, as a reference, and the question stays answerable with every id removed. Grilling's exceptions stay: a fact or access request is asked plainly, and DESIGN.md rule 4's question keeps its exact wording with no recommendation; both must also make sense without ids. Offers keep their exact generated text for approval: offers.py's presentation and its question change together, never by hand. A delivery with no decision asks none.
- R6 Records. The check runs on new or changed prose: tickets, PLAN, FINDINGS, DECISIONS, offers, reports, SPAR.md, docs and chat. History, quoted owner answers and already-presented approvals stay word for word.
- R7 Rewrite requests (Q2, pstack L5). The workflow's description gains a trigger with an object ("write, rewrite or simplify text a person reads"), and the router gains a row: read only, load WRITING.md, return the text, no task records, no offer. No reminder hook. The rewrite is compared with the source for who acts, conditions, obligations, results, exceptions and uncertainty: "may skip" must not become "are skipped".
- R8 The safety step (pstack L6). Before an edit is called lightweight, its one-line why states what outside the diff reads what changes, or "nothing", checked against code-review step 4b's trigger list; if the trigger fires, the edit is not lightweight. A docs fix whose text only tests read stays lightweight, and its check runs those tests. The trigger list gains one example: deleting or replacing a function its callers use, private ones included. The minimal offer shows the one-line assumption; step 4b proves it.
- R9 Tests. One test entry point holds: only WRITING.md defines the common rules (it fails on a numbered writing rule outside it, Strict and CHECK modes excepted, with a mutation fixture); every place in R4's list points to WRITING.md; an id-at-start lint on generated offer and question fixtures, with a valid trailing reference as a positive control; a lost-uncertainty fixture (pstack's L5 sentence) with a meaning-keeping rewrite as a positive control; a report field with a contraction and "ensure" gets no plain-English problem, and bringing either ban back fails; a Plain-mode CHECK of a sentence with a contraction and "verify" reports no rule violation while a Strict-mode CHECK still does; the R3 search test; the new description trigger, router row, step-4b example and minimal-offer line exist. Each negative fixture, when mutated, makes its check fail. CONTEXT.md's owner rows and RULE-CONTRACTS.md name WRITING.md for the common rules.
- R10 Live checks, capped and approved by the owner before they run: a rewrite request loads WRITING.md and creates no task files; ordinary chat does not start the workflow; replacing a private helper with callers is not called lightweight; a /spar conclusion and an offer reach the owner in grilling form with no code-dependent wording; the internal test the owner asked for (a workflow task and a short /spar, read by the coordinator against R5).

Also in this task, not part of the spar (from the coordinator's earlier plan; the owner saw it listed there): the /spar start card offers the launches the owner has left, and a new cap must be above the launches already used.

### Stays the same
- What each skill does; only how it writes for a person and how it asks.
- Old records, quoted owner answers and approved offers.
- Application UI copy, error messages and translations.
- Strict mode (ASD-STE100) keeps its rules.

### Not included
- Rewriting old task records or archives.
- A hook that judges writing.
- The worktree-guard follow-ups (per-worktree approvals, read-only shell commands, links in record folders, removing a named worktree, offer operation names); they stay recorded for later.

### Acceptance
- Every R9 check exists, each failed before its change, and passes after.
- The full suite and validate pass on main.
- A review by GPT-6.1 Sol and a fresh Claude passes.
- The R10 live checks pass, or each failure is recorded and decided by the owner.