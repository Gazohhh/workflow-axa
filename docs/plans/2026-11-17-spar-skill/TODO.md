# TODO

## Overview

| Ticket | What needs to happen | Status | Dependencies |
|---|---|---|---|
| T1 | Save and read the default debate depth | Verified | none |
| T2 | Let grilling keep questions in the conversation when there are no task records | Verified | none |
| T3 | Add the /spar skill and plug it into the workflow | Verified | T1, T2 |
| T4 | Stage the process scenarios and pin the rules they rely on | Verified | T3 |
| T5 | Update the package documents for the new skill | Verified | T3 |
| T6 | Observe /spar live: one real decision and the staged scenarios | In progress | T3, T4, T5 |
| T7 | Save a standalone debate so /workflow can continue from it | Verified | T3 |
| T8 | Fix what the pilot runs showed | Verified | T3 |
| T9 | Bounded extra exchange, exact verdicts, selective continuation | Verified | T3 |
| T10 | End every debate with a usable result | Verified | T7, T8, T9 |
| T11 | Rebuild /spar around SPAR.md | Verified | T10 |
| T12 | Start card, until agreement, strict agreement | Verified | T11 |

Revision 2 of this plan (2026-11-17): plan-review findings (FINDINGS S5) and the owner's D10 (agreement 3) applied.

## Tickets

### T1 — Save and read the default debate depth
Status: Verified

What needs to happen: `settings.py` learns one more setting, `spar.default_depth`, so the owner can set the depth `/spar` uses when the command names none (D8). The command's own depth overrides it without saving.

What should work:
- `settings.py spar depth <quick|normal|thorough|N>` saves it (standard and deep are read as normal and thorough; until agreement is chosen per run, never saved: agreement 7); `settings.py show` prints it; the css switch and any unknown keys stay unchanged.
- A missing value reads as `standard`; an invalid saved value reads as `standard` with a notice; an invalid value on the command line is refused with the allowed values; N is a whole number from 1 upward.

Technical details:
- May change: skills/workflow/scripts/settings.py, tests/test_settings.py. Must not change: the css rules, the hook.
- Test seam: settings.py's command line and its read function; catches lost keys, bad values and the default; misses how /spar uses the value (T3's contract check names the override-without-saving rule).
- TDD: yes.

References:
- Supports: R5, A2.
- Depends on: none
- Rules: AGENTS.md (Python writes keep LF with newline='').

Documents: settings.py usage text.

How to verify:
- `python -X utf8 -m unittest discover -s tests -p "test_settings.py"`, new cases red first, then green.

Evidence: FINDINGS V-lines under "Execution".; FINDINGS V1, V6; Reviews S1-S3

### T2 — Let grilling keep questions in the conversation when there are no task records
Status: Verified

What needs to happen: grilling says to save questions in FINDINGS and record choices in DECISIONS without exception. Add the case it misses: with no task records, or when writes aren't allowed (Inspect, a /spar without a task), the exact questions, options, recommendations, answers and sources stay in the conversation (FINDINGS S4 C3, S5).

What should work:
- Grilling inside a task records exactly as today.
- Grilling without task records creates no files; "Record answers" and the `by: agent` DECISIONS line both name the conversation instead.

Technical details:
- May change: skills/grilling/SKILL.md, tests/test_owned_skills.py, the grilling row of docs/RULE-CONTRACTS.md. Must not change: grilling's rounds, question format or stop rules; its LICENSE and credit (VENDORED-SKILLS.md stays as is).
- Test seam: the skill text; catches the rule going missing; misses model compliance (observed only in T6).
- TDD: yes (contract test first).

References:
- Supports: R8, A3.
- Depends on: none
- Rules: AGENTS.md; VENDORED-SKILLS.md.

Documents: docs/RULE-CONTRACTS.md (grilling row).

How to verify:
- `python -X utf8 -m unittest discover -s tests -p "test_owned_skills.py"`; `python -X utf8 -I tools/validate.py`.

Evidence: FINDINGS V-lines under "Execution".; FINDINGS V2; Reviews S1-S3

### T3 — Add the /spar skill and plug it into the workflow
Status: Verified

What needs to happen: create the small user-invoked skill that owns only the debate and the one reference it reads, then connect it where the workflow lists its specialists and where clarify writes the agreement.

What should work:
- `skills/spar/SKILL.md` (`disable-model-invocation: true`) runs agreement 3's steps 1-8: frame; foundations sorted into verified fact, unverified assumption and contradiction, scaled to the decision's complexity and risk (R3, R12, R13); owner questions through grilling, only when research can't settle them (R8); the blind opening by a fresh Claude subagent and GPT (R4); exchanges with the objection ledger; the active coordinator (R11); the endings in order (R6); the result; the handoff (R1).
- It reuses the bundled siblings by path (`../grilling/SKILL.md`, `../workflow-clarify/SKILL.md` step 1, `../codebase-design/SKILL.md`, `../domain-modeling/SKILL.md`) and the optional external specialists `research` and `diagnosing-bugs` by their qualified names, only when installed and read-only, as SPECIALISTS.md separates them. It copies none of their rules (R2).
- `skills/spar/T3.md` (kept apart so the steps stay short; read on every run): the capability check and its three answers (GPT listed, not listed, check failed) with the owner question for the last two (R9), the debater brief, the ledger format, one new task per exchange, `task_cancel` on stop.
- `skills/spar/agents/openai.yaml` with `allow_implicit_invocation: false`; `.claude-plugin/plugin.json` registers `./skills/spar`.
- SPECIALISTS.md: a /spar row (owner-started, recommended for high-stakes choices, never run by the workflow); workflow-clarify step 3: the agreement may carry an Approach part from /spar; CONTEXT.md: the term "Spar"; docs/RULE-CONTRACTS.md: a /spar row.

Technical details:
- May change: skills/spar/ (new), .claude-plugin/plugin.json, skills/workflow/SPECIALISTS.md, skills/workflow-clarify/SKILL.md, CONTEXT.md, docs/RULE-CONTRACTS.md (the /spar row), tests/test_spar.py (new), tests/test_package.py and tests/test_package_contract.py (the registered skill list and the count 19 to 20; historical release counts stay).
- Must not change: hooks, the offer model, workflow-specify, plan-review, interrogate.
- Necessity check (AUDIT.md): one skill and one reference; no script, helper module or setting beyond T1.
- Contract checks in tests/test_spar.py, each tied to its requirement: user-invoked in both hosts (R1, A1); WHAT and WHY only, never implements (R1); the reuse paths and qualified names (R2); the three premise classes and "tests don't prove architecture" (R12); scaling independent of depth (R13); blind opening and fresh debaters (R4); the depth names, counting after the opening and the override without saving (R5, D8); the progress rule, the owner-question check before "stalled" and the outcome order (R6); same-version agreement and the mixed-version rule (R7); owner as third participant: research objective facts, ask only owner-level points, revise after answers (R8); the capability answers and the owner question when GPT is missing (R9); no-task means no files (R10); the active coordinator (R11); technical disagreement vs owner decision (R14); every result field (agreement step 7).
- Test seam: the skill files, plugin.json, validate.py; catches missing rules, wrong flags, a missing registration or row; misses how a model follows the text (T6).
- TDD: yes (contract tests first).

References:
- Supports: R1-R14, A1, A2, A3.
- Depends on: T1, T2
- Rules: AGENTS.md; writing-for-agents for the skill text.

Documents: SPECIALISTS.md, CONTEXT.md, workflow-clarify, docs/RULE-CONTRACTS.md.

How to verify:
- `python -X utf8 -m unittest discover -s tests -p "test_spar.py"` and `-p "test_package*.py"`; `python -X utf8 -I tools/validate.py` passes with 20 skills.
- Review of the skill text by GPT-6 Astra and a fresh Opus until both agree.

Evidence: FINDINGS V-lines and review outcomes under "Execution".; FINDINGS V3, V6, V7; Reviews S1-S4 (S3 Astra and Opus passed)

### T4 — Stage the process scenarios and pin the rules they rely on
Status: Verified

What needs to happen: write the live scenarios that test the decision process, not conclusions (A5, D10), and an offline test that every scenario exists, is well formed and names a skill rule that appears in the skill text. Offline coverage is authored coverage only; nothing here counts as observed behaviour.

What should work: `tests/behavioral/spar.json`, every scenario `mode: live-host`, `result: NOT_RUN` until observed, each with a staged situation, the process checks to observe and an explicit "no prescribed answer":
- uncertainty about priorities or acceptable risk: the skill asks the owner a relevant question instead of guessing, uses the answer, and each side revises or defends its position with reasons;
- an objective fact in dispute: the skill researches or checks it and asks the owner nothing about it;
- false consensus: both debaters agree on a version without evidence; the coordinator challenges it; "agreed" is reported only once the gap is closed with evidence, otherwise the gap stays an open objection under another outcome (needs the owner, stalled or limit reached);
- stagnation: a repeated argument; the coordinator first checks whether an owner question could unblock it, asks it if so, otherwise reports "stalled" with both positions;
- unresolved objections: each is classed as a technical disagreement (both positions and evidence reported) or an owner decision (asked);
- missing GPT: capability shows no GPT, and separately the check fails: the skill says so and asks the owner how to proceed; no silent substitution;
- questionable existing architecture: a staged premise the code contradicts is reported as a contradiction with the evidence and alternatives; the owner is involved when the choice changes scope; nothing is refactored;
- no codebase or task: no files written; cancel mid-run: delegates cancelled, no restart.
- A test in tests/test_spar.py checks the shape, that every scenario above exists, that none prescribes a recommended answer, and that each named rule appears in the skill text.

Technical details:
- May change: tests/behavioral/spar.json (new), tests/test_spar.py.
- Test seam: the scenario file and the skill text; catches a missing scenario, a prescribed answer or a rule that went missing; misses actual behaviour (T6).
- TDD: yes.

References:
- Supports: A5, A2.
- Depends on: T3

Documents: none here (tests/README.md belongs to T5).

How to verify:
- `python -X utf8 -m unittest discover -s tests -p "test_spar.py"`.

Evidence: FINDINGS V-lines under "Execution".; FINDINGS V4; scenarios staged NOT_RUN; Reviews S3

### T5 — Update the package documents for the new skill
Status: Verified

What needs to happen: the README, the architecture doc and the tests guide describe /spar, and the current skill counts say 20.

What should work: README lists /spar with the other user commands and says 20 skills; docs/ARCHITECTURE.md places /spar before workflow-clarify's agreement (WHAT and WHY) and workflow-specify after it (HOW); tests/README.md names tests/test_spar.py and tests/behavioral/spar.json and says the scenarios are live-only. The CHANGELOG entry is written at release, not here.

Technical details:
- May change: README.md, docs/ARCHITECTURE.md, tests/README.md.
- Test seam: validate.py's count and link checks; misses wording quality (review).
- TDD: no (documents).

References:
- Supports: A1.
- Depends on: T3

Documents: these three.

How to verify:
- `python -X utf8 -I tools/validate.py`; the full suite passes.

Evidence: FINDINGS V-lines under "Execution".; FINDINGS V5, V8

### T6 — Observe /spar live: one real decision and the staged scenarios
Status: In progress

What needs to happen: observe how a model follows the skill. First one real decision the owner picks (A4), then the staged scenarios from T4. Each records what was observed against its own process checks, or "not provoked"; nothing unobserved is claimed.

What should work:
- Where the candidate runs: the work happens in an isolated worktree (the main checkout D:\workflow-axa feeds the installed plugin and stays untouched until release). For each run, a disposable project outside every checkout (under a new folder D:/workflow-axa-spar-pilot/<run>/) gets the candidate's 20 skill folders in `.claude/skills/`, copied from a ZIP built by tools/build_release.py; a T3 thread opened on that project loads them. Recorded per run: the snapshot id of the source worktree the ZIP was built from (skills/interrogate/scripts/snapshot.py id) and the transcript line showing /spar loaded from that project's `.claude/skills/spar/`, not the installed plugin.
- The real decision (A4), quick depth: the frame, the foundation check, a blind opening by a fresh Claude and GPT, one exchange, the questions it asked and why, one outcome, no files outside a task.
- Each staged scenario is checked only against its own T4 process checks.

Technical details:
- Runs and their cap (debater launches; each run is also one coordinator session):
  1. the real decision: 4;
  2. unclear priorities (asks, uses the answer, revises): 4;
  3. a disputed objective fact, outside any task (researches, asks nothing about it, writes no files): 4;
  4. false consensus: 4;
  5. stagnation, standard depth so repetition can happen: 6;
  6. questionable architecture, on a small sample repository with a contradicted premise: 4;
  7. missing GPT: a Claude Code CLI session in the pilot project, where no T3 tool exists: 0 (it must ask how to proceed);
  8. cancel during run 2's exchange: no extra launches.
  Unresolved-objection classing is read from runs 4-6. The "capability check failed" variant can't be staged safely and stays NOT VERIFIED unless it happens naturally.
- Total cap: 26 debater launches and 8 coordinator sessions; no research agents; no retry without the owner's OK; subscription limits apply. Each batch runs only after the owner's OK right before it, and the owner may stop after any batch.
- The pilot folders are owned by this task; after the evidence is recorded they are removed, except a run kept as evidence of a failure (its path, reason and removal condition in FINDINGS), per the shared artifact policy.

References:
- Supports: A4, A5.
- Depends on: T3, T4, T5

Documents: FINDINGS (observations), tests/behavioral/spar.json (results).

How to verify:
- Human check: the owner OKs each batch and answers the questions /spar asks in it; I read each transcript and record per scenario: observed (with the quote), not provoked, or failed.

Evidence: FINDINGS "Live observations".


Revision 3 of this plan (2026-11-17): agreement 4 additions R15-R24, A6 (D16) add T7-T9; T6's remaining runs use the revised candidate.

### T7 — Save a standalone debate so /workflow can continue from it
Status: Verified
Evidence: FINDINGS V9-V14; Reviews S5-S10 (Astra S8 and Opus S10 passed)

What needs to happen: R15-R17. A new skills/spar/SAVE.md holds the mechanics (the question, the folder through TASK-FOLDER.md and record.py, what goes in PLAN/FINDINGS/DECISIONS, the last message); SKILL.md section 8 points to it. workflow-clarify step 3 names a saved /spar PLAN as the Approach source.

What should work:
- A standalone debate that ends (agreed, stalled, limit, unavailable) asks the three-answer question once; after the owner's stop it doesn't ask.
- "Save …" writes PLAN.md, FINDINGS.md and (only with a material owner choice) DECISIONS.md through record.py; no TODO, no offer.
- "Save and continue now" then starts workflow-clarify on that task; nothing is approved.
- Inside an existing task: no question, records as today.
- The last message names the PLAN, the outcome, `/workflow continue from <path>` and "implementation is not approved".

Technical details: may change skills/spar/ (SKILL.md, SAVE.md, T3.md), skills/workflow-clarify/SKILL.md, tests/test_spar.py, docs/RULE-CONTRACTS.md (the spar row). SKILL.md stays under 1,300 words. TDD: contract pins first.

### T8 — Fix what the pilot runs showed
Status: Verified
Evidence: FINDINGS V9-V14; Reviews S5-S10 (Astra S8 and Opus S10 passed)

What needs to happen: R18-R20, R22, R23: the frame line as a required check before any launch; owner priorities asked as soon as named; one complete unavailable menu (helpers, stop, try again later) in T3.md; a safety, security or data-loss finding told at once; coordinator checks under bug.md's standing diagnostic allowance, reconciling "no code, tests" in SKILL.md.

What should work: each rule pinned by a test phrase; the pilot observations O1 and O7 map to a rule each.

Technical details: may change skills/spar/SKILL.md, T3.md, tests/test_spar.py. TDD: pins first.

### T9 — Bounded extra exchange, exact verdicts, selective continuation
Status: Verified
Evidence: FINDINGS V9-V14; Reviews S5-S10 (Astra S8 and Opus S10 passed); live scenarios wait for T6

What needs to happen: R21, R24; A6: tests/test_spar.py's scenario check accepts recorded results (NOT_RUN, OBSERVED, FAILED or NOT_PROVOKED, each non-NOT_RUN with an evidence pointer); tests/behavioral/spar.json gains the save, continue-from-saved, early-owner-question and extra-exchange scenarios.

What should work: the extra-exchange offer appears once, only with unjudged versions, with its cost; verdicts name ids; the result says what would change the recommendation; a continued debate re-checks only what changed.

Technical details: may change skills/spar/, tests/test_spar.py, tests/behavioral/spar.json, tests/README.md. TDD: yes.

How to verify T7-T9: `cd tests && python -X utf8 -m unittest test_spar test_owned_skills test_settings`; the full suite; tools/validate.py; review by GPT-6 Astra and a fresh Claude until both pass; live: the remaining T6 runs on a new candidate snapshot.


Revision 4 of this plan (2026-11-17): agreement 5 additions R25-R30, A7 (D21) add T10; T6's remaining runs use the revised candidate.

### T10 — End every debate with a usable result
Status: Verified
Evidence: FINDINGS V15, V16; Reviews S12-S13 (Astra and Opus passed S13)

What needs to happen: R25-R30. SKILL.md (sections 1, 5-7) and the support files: the closure check of owner choices after every round, the closing assessment of fixed proposals, the handoff state and the owner's selection question, the compact result first and the save question after it, the frame as one plain bold line, the exact final texts in the saved FINDINGS. Detail goes to T3.md and SAVE.md; SKILL.md stays under 1,300 words.

What should work:
- No consequential owner choice is left as a to-do: each is answered, explicitly deferred or reported as blocking, asked in batches of at most 4 per round, with attributed recommendations.
- The final check judges named proposals; an amendment never replaces one; a failed check ends in explicit disagreement.
- The result names the outcome and the handoff state; with competing approaches still open, the owner sees them and is asked once to take one or leave it open.
- The compact result is shown before the save question; "Not saved yet" outside a task; the PLAN link first after a save.
- The frame is a normal **Spar:** line, once.

Technical details: may change skills/spar/ (SKILL.md, T3.md, SAVE.md), tests/test_spar.py, tests/behavioral/spar.json (a scenario for the closing outcome and the owner's selection), tests/README.md if the scenario list changes. TDD: pins first.

How to verify: `python -X utf8 -m unittest discover -s tests -p "test_spar.py"`; test_owned_skills; the full suite; review by GPT-6 Astra and a fresh Claude until both pass; live: a T6 run on a new snapshot (A7).


Revision 5 of this plan (2026-11-17): agreement 6 (D24) rebuilds /spar around SPAR.md; T11 replaces the text of T7-T10 where it conflicts; T6's remaining runs use the rebuilt candidate.

### T11 — Rebuild /spar around SPAR.md
Status: Verified
Evidence: FINDINGS V17-V24; Reviews S15-S20 (Astra passed S18; Opus's last finding fixed with its own wording, V24); live check A8 waits for T6

What needs to happen: R31-R40. Rewrite skills/spar/SKILL.md around the flow understand → explore → challenge → decide, SPAR.md as the record and the four-way handoff. Keep T3.md's debaters, menu and briefs (opening and exchange briefs adapted: framing challenge, focus on outcome-changing disagreements); replace SAVE.md and RESULT.md with one support file for SPAR.md (its sections, when it is updated, the conclusion, the handoff). workflow-clarify step 3 takes the Approach from a SPAR.md Handoff brief. CONTEXT.md, docs/RULE-CONTRACTS.md (spar row), README.md and tests/README.md follow.

What should work:
Revised by D26, D28, D30 and D31: SPAR.md lives in docs/spar/, keeping it is the owner's choice, and the plan handoff splits outside and during a task.

- At the start /spar asks once "Keep a SPAR.md" · "Conversation only" (unless the command says which); a kept SPAR.md is `docs/spar/<date>-<topic>/SPAR.md` with the R32 sections, updated after each meaningful step; a conversation-only spar writes nothing until the owner picks the plan handoff.
- The owner is asked only when an answer changes the direction; no list of decisions at the end.
- The coordinator may recommend, labelled apart from each debater's assessment and the owner's decision.
- Effort budgets with a launch limit; a spent budget still gives a conclusion and a next move.
- The conclusion comes before the one handoff question with its four answers; "Turn this into a workflow plan" writes SPAR.md if it wasn't kept, then outside a task starts a new task in docs/plans/ linking it, and during a task continues that task's workflow-clarify (the checkpoint changes only then).
- The approval hook counts only a plain `docs/spar/<folder>/SPAR.md` (no link on its way, no second hard link) as a record.
- With one model, the session still works and is labelled as such.

Technical details: may change skills/spar/ (all files; SAVE.md and RESULT.md may be removed or merged), skills/grilling/SKILL.md, hooks/phase_gate.py (SPAR_RECORD and plain_file only, D26), tests/test_approval_hook.py, skills/workflow-clarify/SKILL.md, CONTEXT.md, docs/RULE-CONTRACTS.md, README.md, tests/test_spar.py (rewritten for agreement 6), tests/behavioral/spar.json (scenarios rewritten for the new flow, earlier results kept as history), tests/README.md, skills/workflow/scripts/settings.py only if the depth names change. SKILL.md under 1,300 words. TDD: contract pins first.

How to verify: test_spar, test_owned_skills, test_settings, the full suite; GPT-6 Astra and a fresh Claude review until both pass; live: a T6 run on the rebuilt candidate (A8).

Revision 6 of this plan (2026-11-17): agreement 7 (D35) adds the start card, until agreement and a strict "agreed"; T12 changes T11's text where it conflicts.

### T12 — Start card, until agreement, strict agreement
Status: Verified
Evidence: FINDINGS V25 S22 S23 S24; test_spar test_settings test_owned_skills OK; full suite 1492 run, only the 4 known VALIDATION.md 19-local-skills counts fail; Astra and Opus PASS (round 3)
Depends on: T11

What needs to happen: R41-R44. In skills/spar/SKILL.md and T3.md: one start card for the missing effort, debaters and record; an until-agreement effort with the owner's cap; "agreed" only for the same proposal id and exact text; three separate endings; two launches reserved for the final check; briefs that reward justified disagreement. settings.py accepts the saved default but never authorises launches by itself.

What should work:
- With no effort, debaters or record in the command, one card asks all three before any launch; with all three stated, no card.
- "Until agreement" asks for a cap (20 · 30 · 50 or a number, at least 6) and ends on agreement, deadlock or the cap, each reported as itself.
- A merged or edited proposal is never called agreed until both accept that exact version.

Technical details: may change skills/spar/ (SKILL.md, T3.md, SPAR-FILE.md), skills/workflow/scripts/settings.py, README.md, tests/test_spar.py, tests/test_settings.py, tests/behavioral/spar.json, docs/RULE-CONTRACTS.md.

How to verify: test_spar and test_settings first failing, then passing; test_owned_skills; the full suite; a review by GPT-6.1 Sol; live: run 5 (after the owner's OK).
