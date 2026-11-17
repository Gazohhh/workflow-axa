# TODO

Agreement 1 (R1–R12, A1–A6). All tickets edit agent instructions, reference docs and tests only. No hooks, scripts or release records. Rules for every ticket: AGENTS.md (repo root), CONTEXT.md (one owner file per repeated rule), writing-for-agents for skill text, WRITING.md and SIMPLE-ENGLISH.md for human-facing docs. Owner policy (test_owned_skills): no file under `skills/` names where text came from, except LICENSE files. So no "pstack", "Lauren Tan" or "upstream" under `skills/`.

## Overview

| Ticket | What needs to happen | Status | Dependencies |
|---|---|---|---|
| T1 | Blast-radius method file and code-review step 4b | Verified | none |
| T2 | Blast radius at planning and routing points | Verified | T1 |
| T3 | Blast radius in each recipe | Verified | T2 |
| T4 | The Unslop check and its tells list | Verified | T1, T2, T3 |
| T5 | Credits, glossary, contracts, README and test docs | Verified | T4 |

## Tickets

### T1 — Blast-radius method file and code-review step 4b
Status: Verified

What needs to happen: Create `skills/code-review/BLAST-RADIUS.md` as the single owner of the method. Shrink step 4b to its trigger, a link to the file, and where the result goes.

What should work:
- BLAST-RADIUS.md covers these parts. Callers are the input, not the result. Safety facts: the riskiest one or two come first, with no cap on material facts. The evidence ladder 1–5, with the step each fact reached. Where grep stops: library source with its pinned version and local patch; timing, teardown and async order; JSON or API shape; a DB column; a wire or file format; another language; a config key; a feature flag; saved data; downstream hops. Risks (how it breaks, file:line, likelihood, cost, check) listed separately from Cleared. "Before you merge": the cheapest test or repro. "None" counts only with a boundary trace. The probe limits: the OPERATIONS standing diagnostic allowance; an isolated copy through `../interrogate/scripts/snapshot.py` id/copy; "unproven" plus the named experiment when a probe can't run. A wide change gets a recommendation of the user-started `/interrogate`. There is no arena or multi-model step. It reports only. It also states its two other uses: a planning pass with no diff, which yields assumptions and their falsifying checks and runs no proof; and an Inspect question, which gets a report only.
- Step 4b: the trigger is anything outside the diff that reads what changed (exported symbol, shared module, schema or DB column, API or JSON shape, wire or file format, config key, feature flag, saved data, timing or lifecycle, dependency version). It holds a sibling Markdown link to BLAST-RADIUS.md, puts the result under `## Standards` as "Blast radius", and reuses the safety assumptions in the task records. It reopens an assumption when the implementation or new evidence changes or contradicts it.
- The old sentence "Search for the callers outside the diff, name them" is gone. No 25-word paragraph repeats between SKILL.md and BLAST-RADIUS.md.

Technical details:
- May change: `skills/code-review/BLAST-RADIUS.md` (new), `skills/code-review/BLAST-RADIUS.LICENSE` (new, MIT notice "Copyright (c) 2026 Lauren Tan", the full pstack licence text), `skills/code-review/SKILL.md` (step 4b only), `tests/test_new_skills.py` (CodeReviewChecks), `tests/test_package_contract.py` (KEY_FILES gains both new files).
- Must not change: code-review steps 1–4, 5 and 6, and `skills/code-review/LICENSE`.
- Necessity check: one reference file. Three readers (code-review, clarify, the Inspect route) need the method without loading all of code-review. Deleting it would put the text back into one long step.
- Test seam: `tests/test_new_skills.py` phrase checks on the files. They catch a missing or renamed part and the old caller-listing sentence. They miss whether an agent follows the method; the NOT_RUN cases in T2 track that.
- TDD: yes. Change `test_blast_radius_step` and add `test_blast_radius_method` first; both fail on today's text.

Documents: none here (T5 owns README, CONTEXT, RULE-CONTRACTS and tests/README).

How to verify:
- `python -X utf8 -m unittest discover -s tests -p "test_new_skills.py"; python -X utf8 -m unittest discover -s tests -p "test_package_contract.py"; python -X utf8 -m unittest discover -s tests -p "test_owned_skills.py"` (tests/ is not a package, so dotted module names do not import) run from D:/workflow-axa: red before the text change, green after. The new test also asserts that BLAST-RADIUS.LICENSE starts with "MIT License", has the line "Copyright (c) 2026 Lauren Tan" and holds the complete MIT permission and warranty text.
- `python -X utf8 -I tools/validate.py`: PASS, with no repeated-paragraph failure.
- Cold-reader check (A5, part 1): a fresh subagent gets only BLAST-RADIUS.md and its audience. It restates when the method runs (review, planning, Inspect), what it produces (safety facts with ladder step, Risks, Cleared, Before you merge, or "none" with a boundary trace) and what it never does (edit, write outside an isolated copy, start /interrogate). Each mismatch is a writing defect, fixed in this ticket. Result recorded as a V entry.

Verification: passed (V1 tests red then green; V2 cold reader; validate PASS; final review S3 passed, history in FINDINGS)

References:
- Supports: R1, R2, R4 (4b reuses and reopens assumptions), R9 (BLAST-RADIUS.LICENSE), A1, A2, A3, A5
- Depends on: none
- Rules: AGENTS.md; writing-for-agents
- Evidence: FINDINGS V1, V2, Review S1-S3; FINDINGS V1, V2, Review S3

### T2 — Blast radius at planning and routing points
Status: Verified

What needs to happen: Point every planning and routing step to the method, so the trigger is noticed before and after the code exists.

What should work:
- workflow-clarify step 1 (our own lines, the trace list; the step 3 `/spar` bullet of the other session stays untouched): record the material safety assumptions and the check that could falsify each one. The pointer to `code-review/BLAST-RADIUS.md` is package-relative in code form, not a Markdown link that leaves the skill folder.
- workflow-specify step 3: those assumptions become ticket or whole-feature checks.
- plan-review step 3: flag a plan that changes something read outside its files but records no safety assumptions or checks.
- workflow SKILL.md §4 "Lightweight edit": an edit whose 4b trigger fires is not lightweight.
- flows/INDEX.md: the Inspect line answers "what could this break" with the method, report only. The Compatibility modifier requires the method.
- workflow-execute step 6 and "Whole-feature review": 4b runs per ticket when the trigger fires, and again on the whole diff.
- workflow/AUDIT.md: for a docs-only or instructions change whose text a tool, test, validator or other document reads, the review applies the method too.
- workflow-deliver step 5 (Reviews): when the trigger fired, a Blast radius result exists in the review, checked before step 7's defect routing. Step 8 lists open Risks and unproven facts under limitations.
- tests/behavioral/flows.json: one or more `inspect` prompts such as "What could renaming the `status` column break?". A new list `blast_radius_cases` (live-host, NOT_RUN) with: hidden non-grep consumer (JSON or DB column), denied probe marked unproven, local change with a boundary trace, natural-language Inspect question, two tickets that combine into a break at whole-feature review.

Technical details:
- May change: `skills/workflow-clarify/SKILL.md` (step 1 only), `skills/workflow-specify/SKILL.md` (step 3), `skills/plan-review/SKILL.md` (step 3), `skills/workflow/SKILL.md` (§4 lightweight paragraph), `skills/workflow/flows/INDEX.md` (Inspect line and Compatibility modifier), `skills/workflow-execute/SKILL.md` (step 6 and Whole-feature review), `skills/workflow/AUDIT.md` (the review-selection paragraph), `skills/workflow-deliver/SKILL.md` (steps 5 and 8), `tests/behavioral/flows.json`, `tests/test_flows.py`, `tests/test_new_skills.py`.
- Must not change: the clarify step 3 `/spar` bullet, offer or hook wording, `uses:` frontmatter.
- Word budgets: the phase skills are near their advisory ceilings. Each addition is one sentence or one bullet, and the method stays in BLAST-RADIUS.md.
- Test seam: phrase checks per file catch a missing pointer. validate.py checks Markdown links only (tools/validate.py:421), so a new test resolves every code-form pointer `code-review/BLAST-RADIUS.md` (and T4's `workflow/WRITING.md` and `workflow/SIMPLE-ENGLISH.md` pointers) from the package's `skills/` folder and asserts the target file exists. `test_flows` checks the new cases are live-host NOT_RUN and that the Inspect prompts are labelled `inspect`. They miss live routing.
- TDD: yes. The tests are written first and fail.

Documents: none here (T5).

How to verify:
- `python -X utf8 -m unittest discover -s tests -p "test_flows.py"; python -X utf8 -m unittest discover -s tests -p "test_new_skills.py"; python -X utf8 -m unittest discover -s tests -p "test_owned_skills.py"` (tests/ is not a package, so dotted module names do not import)
- `python -X utf8 -I tools/validate.py`
- `python -X utf8 -I skills/rule-maker/scripts/docs_check.py D:/workflow-axa --changed skills/workflow-clarify/SKILL.md skills/workflow-specify/SKILL.md skills/plan-review/SKILL.md skills/workflow/SKILL.md skills/workflow/flows/INDEX.md skills/workflow-execute/SKILL.md skills/workflow/AUDIT.md skills/workflow-deliver/SKILL.md`: 0 blocking.

Verification: passed (V3 tests red then green, validate PASS, docs_check 0 blocking; final review S5 passed)

References:
- Supports: R3, R4, R12, A1, A2, A4, A6
- Depends on: T1
- Rules: AGENTS.md; writing-for-agents
- Evidence: FINDINGS V3, Review S4-S5; FINDINGS V3, Review S5

### T3 — Blast radius in each recipe
Status: Verified

What needs to happen: Each recipe names the method where its own steps meet it, as agreed in R5.

What should work:
- bug step 7; feature steps 1 and 6 ("none" with a boundary trace for a purely additive feature); ui (when a shared component, class, functional ID or text key is edited, name the other screens; step 5 checks one of them on screen); refactor steps 1 and 6; migration steps 1 and 5; performance (state the behaviour that must not change before step 5; the method for a cache, deferral, batching or reorder); architecture step 3 (the where-grep-stops list only, no proof); docs-tests steps 1 and 3 (readers that parse the text, then run them).
- new-project is unchanged. `uses:` stays unchanged.

Technical details:
- May change: `skills/workflow/flows/{bug,feature,ui,refactor,migration,performance,architecture,docs-tests}.md`, `tests/test_flows.py`.
- Must not change: `new-project.md`, `TEMPLATE.md`, frontmatter.
- Test seam: `test_flows` asserts that each of the eight recipes names `code-review/BLAST-RADIUS.md` and that new-project does not. Catches a missing step; misses whether the step is in the right place (covered by T3 review and the GPT ticket spar).
- TDD: yes.

Documents: none here (T5).

How to verify:
- `python -X utf8 -m unittest discover -s tests -p "test_flows.py"` (tests/ is not a package, so dotted module names do not import)
- `python -X utf8 -I tools/validate.py`

Verification: passed (V4 tests red then green, validate PASS, docs_check 0 blocking; final review S7 passed)

References:
- Supports: R5, A1, A2, A4
- Depends on: T2 (shared test files)
- Rules: AGENTS.md; writing-for-agents
- Evidence: FINDINGS V4, Review S6-S7; FINDINGS V4, Review S7

### T4 — The Unslop check and its tells list
Status: Verified

What needs to happen: Add the named, required Unslop check to WRITING.md and the numbered tells list to SIMPLE-ENGLISH.md, then point the writing steps to it.

What should work:
- WRITING.md "Unslop" section: run after drafting, before the cold-reader check. It applies to offer inputs before `record.py offer create` (never the presented output), substantial plans, FINDINGS prose, the delivery chat report, human-facing docs, changed prose hunks in code-review, and commit or PR text when asked to write one. It never changes application UI copy, error messages or translations by itself. "Keep the meaning" wins over every tell.
- SIMPLE-ENGLISH.md "Unslop tells": numbered "Unslop N", keeping the source numbering and leaving gaps for tells not adopted. It lists the tells not yet covered by rules 1–12, and it points to the rule that already covers each overlapping one, without restating it. Unslop 24 is listed as not adopted, with the reason. Banned words count only in figurative use; literal technical terms and rule 2 content stay.
- word-swaps.md: the vocabulary tells (Unslop 7, 26, 31) as rows, without duplicate rows.
- writing-for-agents: cites the tells list for prose and names the exceptions (leading words and deliberate metaphors, "Leading words" section).
- Pointers: workflow-deliver step 8 (Unslop before the cold-reader check), docs-tests step 2, code-review (changed prose hunks in the Standards brief), workflow-specify step 5 (offer inputs before `offer create`).
- tests/behavioral/cases.json: a new live-host NOT_RUN case, an Unslop pass that removes an empty claim and keeps "may", a quoted command and the word "vector" in its technical sense.

Technical details:
- May change: `skills/workflow/WRITING.md`, `skills/workflow/SIMPLE-ENGLISH.md`, `skills/workflow/UNSLOP.LICENSE` (new, MIT, Lauren Tan), `skills/workflow/simple-english/word-swaps.md`, `skills/writing-for-agents/SKILL.md`, `skills/workflow-deliver/SKILL.md` (step 8), `skills/workflow/flows/docs-tests.md` (step 2), `skills/code-review/SKILL.md` (Standards brief), `skills/workflow-specify/SKILL.md` (step 5, one clause), `tests/test_simple_english.py`, `tests/test_new_skills.py` (licence text and code-form pointer checks), `tests/behavioral/cases.json`, `tests/test_behavioral_cases.py` when it pins case counts, `tests/test_package_contract.py` (KEY_FILES gains UNSLOP.LICENSE).
- Must not change: SIMPLE-ENGLISH rules 1–12 and their numbers, WRITING "Keep the meaning", the offer presentation rules.
- Test seam: `test_simple_english` checks the section order in WRITING (Unslop before Cold-reader), the "Unslop N" ids, 24 marked not adopted, the UI-copy exclusion and the licence file. It misses agent behaviour (NOT_RUN case).
- TDD: yes.

Documents: none here (T5).

How to verify:
- `python -X utf8 -m unittest discover -s tests -p "test_simple_english.py"; python -X utf8 -m unittest discover -s tests -p "test_behavioral_cases.py"; python -X utf8 -m unittest discover -s tests -p "test_package_contract.py"; python -X utf8 -m unittest discover -s tests -p "test_owned_skills.py"; python -X utf8 -m unittest discover -s tests -p "test_new_skills.py"` (tests/ is not a package, so dotted module names do not import). The new test asserts UNSLOP.LICENSE's MIT heading, the line "Copyright (c) 2026 Lauren Tan" and the complete permission and warranty text, and resolves the code-form pointers to WRITING.md and SIMPLE-ENGLISH.md.
- `python -X utf8 -I tools/validate.py`
- Cold-reader check (A5, part 2): a fresh subagent gets only the WRITING.md Unslop section and the SIMPLE-ENGLISH tells, and restates when the check runs, on which texts, and what it never changes (meaning, uncertainty words, rule 2 content, presented offer text, application UI copy). Each mismatch is a writing defect. Result recorded as a V entry.

Verification: passed (V5 tests red then green, validate PASS, W5 search clean; V6 and V7 cold reader; final review S10 passed)

References:
- Supports: R6, R7, R8, R9 (UNSLOP.LICENSE), A1, A2, A4, A5, A6
- Depends on: T3 (docs-tests.md), T1 (code-review SKILL.md), T2 (specify, deliver)
- Rules: AGENTS.md; writing-for-agents; WRITING.md
- Evidence: FINDINGS V5-V7, Review S8-S10; FINDINGS V5-V7, Review S10

### T5 — Credits, glossary, contracts, README and test docs
Status: Verified

What needs to happen: Record where the text came from and what the package now says, outside `skills/`. Write the summary ready for CHANGELOG.

What should work:
- VENDORED-SKILLS.md: one new row. Its first column holds only names the table already counts, `code-review` and `simple-english`, plus plain words for the material ("blast-radius method in skills/code-review/BLAST-RADIUS.md; Unslop tells in skills/workflow/SIMPLE-ENGLISH.md"). Any path written there is not a bare backticked name: tools/validate.py:65 counts every backticked bare name in that column as a licensed skill. The source column names github.com/cursor/plugins `pstack/skills/blast-radius` and `pstack/skills/unslop` with the commits actually copied. The licence column names `skills/code-review/BLAST-RADIUS.LICENSE` and `skills/workflow/UNSLOP.LICENSE`. A test asserts that `licence_files()` finds both paths and that `licensed_skills()` is unchanged from before this task (the same sorted list).
- README.md, only around :43 and :58: the blast-radius step now lives in `code-review/BLAST-RADIUS.md`, adapted from pstack with credits; the Unslop check in WRITING.md. "no text was copied" and "No new writing skill" are corrected to the facts.
- CONTEXT.md: terms "Blast radius", "Safety fact" and "Unslop check", each naming its owner file.
- docs/RULE-CONTRACTS.md: the code-review row names the blast-radius procedure; the SIMPLE-ENGLISH / WRITING row names the Unslop check.
- tests/README.md: a short section on the new phrase and case checks, and what they don't prove.
- tests/test_owned_skills.py: `SOURCE_MENTIONS` gains `pstack`, `Lauren Tan` and `cursor/plugins`, so the owner's no-source rule covers the new source too.
- This task's FINDINGS gains a summary ready for CHANGELOG for the rc.3 release step.

Technical details:
- May change: `VENDORED-SKILLS.md`, `README.md` (the two lines only), `CONTEXT.md`, `docs/RULE-CONTRACTS.md`, `tests/README.md`, `tests/test_owned_skills.py`, `tests/test_release.py` (the ZIP holds both new licence files), this task's records.
- Must not change: README skill counts or the /spar lines (other session), CHANGELOG, UPGRADE, VALIDATION, plugin.json, marketplace.json, version.json.
- Test seam: `test_owned_skills` (source names, with a fixture line such as "adapted from pstack" that the extended pattern must match and the old one does not), `test_release` (ZIP contents), the credits assertions above, validate (counts, links, CONTEXT terms).
- TDD: the source-name pattern and the credits assertions are written first and shown failing (a negative fixture for the pattern; the credits test before the row exists). The ZIP assertion is a regression check: it can already pass after T1 and T4, so it is not given an invented red phase.

Documents: VENDORED-SKILLS.md, README.md, CONTEXT.md, docs/RULE-CONTRACTS.md, tests/README.md.

How to verify:
- `python -X utf8 -m unittest discover -s tests -p "test_owned_skills.py"; python -X utf8 -m unittest discover -s tests -p "test_release.py"` (tests/ is not a package, so dotted module names do not import)
- `python -X utf8 -I tools/validate.py`
- `python -X utf8 -I skills/rule-maker/scripts/docs_check.py D:/workflow-axa --changed VENDORED-SKILLS.md README.md CONTEXT.md docs/RULE-CONTRACTS.md tests/README.md`: 0 blocking.

Verification: passed (V8 tests red then green, validate PASS, docs_check 0 blocking; final review S12 passed)

References:
- Supports: R9, R10, R11, A1, A2, A4
- Depends on: T4
- Rules: AGENTS.md; WRITING.md; SIMPLE-ENGLISH.md
- Evidence: FINDINGS V8, Review S11-S12, Summary for the rc.3 CHANGELOG; FINDINGS V8, Review S12

## Whole-feature checks

- W0 — Baseline, before the first edit: PLAN `## Baseline before this change` records the exact command, folder, commit c5e954b plus diff hash, Python 3.14.2, git 2.38.0.windows.1, and each failing test with its first error line (`skills/workflow/scripts/baseline_state.py record` when it runs). A baseline run was started in specify; it is reused only while those inputs still match.
- W1 — The full suite: `python -X utf8 -m unittest discover -s tests -p "test_*.py"` from D:/workflow-axa. Failures that existed before (W0) are named apart. The known lock flake in test_record_safety is rerun once, as tests/README.md says.
- W2 — `python -X utf8 -I tools/validate.py`: PASS.
- W3 — Blast radius on this change itself (the method applied to its own diff). Trace each reader of the changed files by reading its code: tools/validate.py (credit_rows, licence_files, doc_fact_errors, link and repeated-paragraph checks, CONTEXT terms), skills/rule-maker/scripts/docs_check.py (index reachability, required reads), hooks/approval.py, hooks/phase_gate.py and hooks/read_evidence.py (do they parse any changed skill text, such as section headings in workflow-specify or deliver?), skills/workflow/scripts/record.py and offers.py (offer presentation text), tools/build_release.py (which files ship), and the tests that assert phrases. Prove each traced contract by running its test (W1, W2). A reader that no test covers is reported with the evidence level reached (file:line read, not run). The other session's /spar text that cites WRITING.md and SIMPLE-ENGLISH.md is a Risk to recheck at merge, not proven here.
- W4 — A5 reconciled: the T1 and T4 cold-reader results are rerun only if their texts changed after those checks, and both V entries are cited.
- W5 — The source-name search, shell-independent, from D:/workflow-axa: `python -X utf8 -I -c "import pathlib,re,sys; p=re.compile('pstack|lauren tan|upstream',re.I); h=[f'{f}:{i}' for f in pathlib.Path('skills').rglob('*.md') for i,l in enumerate(f.read_text(encoding='utf-8').splitlines(),1) if p.search(l)]; sys.stdout.write(chr(10).join(h)); sys.exit(1 if h else 0)"`: exit code 0 and no output. The .LICENSE files are not .md, so they are outside this search; test_owned_skills covers the same rule in the suite.
- Not checkable here: live agent behaviour (all new cases are NOT_RUN until an observed host run); the installed copies under ~/.agents/skills (unchanged until a release and reinstall).
- Output: no test artifacts outside the suite's own temp folders. Baseline output stays in the session scratchpad and is deleted after delivery.
