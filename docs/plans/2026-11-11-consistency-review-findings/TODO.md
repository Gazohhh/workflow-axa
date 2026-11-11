# TODO

## Overview

| Ticket | What needs to happen | Status | Dependencies |
|---|---|---|---|
| H1 | Reproduce the known gate failures in an isolated copy | Verified | none |
| H2 | Enter a phase only through a real phase start | Verified | H1 |
| H3 | Keep edits of one task working while another task's records change, and close the chained-command pass | Verified | H2 |
| H4 | Let the gate accept the small-change route | Verified | H3 |
| H5 | Name overlapping process plugins at session start | Verified | H1 |
| H6 | Copy the verified hooks into the checkout | Verified | H4, H5 |
| D1 | Check documentation structure with a script | Verified | none |
| D2 | List related documents and check named facts | Verified | D1 |
| D3 | Redesign rule-maker around entry point, index and three operations | Verified | D2 |
| W1a | Add the documentation step to the phases | Verified | D3 |
| W1b | Choose UI elements by the job they do for the user | Verified | W1a |
| W1c | Ask fewer, better questions | Verified | W1b |
| L1 | Describe the small-change route | Verified | H6, W1c |
| L3 | Add budgets, the term and owner table, and the term check to the package validator | Verified | D1 |
| L4 | Archive obsolete root documents | Verified | none |
| T2a1 | Consolidate and align the wording of skills/workflow | Verified | L1, L3 |
| T2a2 | Consolidate and align the wording of the phase and status skills | Verified | L1, L3 |
| T2b | Consolidate and align the wording of codebase-map and ui-design | Verified | L1, L3 |
| T2c | Consolidate and align the wording of rule-maker | Verified | L1, L3 |
| T2d | Consolidate and align the wording of the other skills and package docs | Verified | L1, L3 |
| T3 | Merge moved explanations, update asserted phrases and run the whole suite | Verified | T2a1, T2a2, T2b, T2c, T2d |
| X1 | Release notes and version | Verified | T3 |
| V1 | Audit the accessible repositories read-only | Verified | X1 |
| V2 | Run realistic sessions within the cap and the host checks | implemented — verification pending | V1 |
| Y1 | Apply workflow-axa's own audit proposal (revision r2) | Verified | V1 |
| Y2 | One-word document names in capitals (revision r3) | Verified | Y1 |

## Tickets

### H1 — Reproduce the known gate failures in an isolated copy
Status: Verified

What needs to happen: Prerequisite for H2 to H4. Copy the repository to a candidate folder and write failing characterization tests for the gate problems seen so far, so each later hook change is checked against real failures.

What should work:
- A candidate copy exists at .artifacts/2026-11-11-consistency-review-findings/candidate (plain file copy without .git and .artifacts, no Git operation). A hash list of the copied hook and hook-test files is saved beside it for H6. Sessions on this machine load hooks from the checkout (FINDINGS E9 of the guard task), which no H ticket touches before H6.
- Tests reproduce, where the evidence allows: a whole Read of a phase SKILL.md entering the phase; the session check matching the folder name "workflow-axa"; another task's record write stopping an approved edit; `git apply` chained after a record write passing without approval (seen 2026-11-11); and the earlier Altinstar items (requirement IDs read as report revisions, approval checks in worker sessions, repeated goal stops). An item that cannot be reproduced from trustworthy evidence is recorded as not reproduced, not invented.
- Adversarial cases for later tickets: interrupted session, resumed task, approval line for another revision, approval quote from before the report, approval in agent text, attempts to bypass the gate (chained shell commands, a Write through PowerShell, an MCP write).

Technical details:
- May change: tests/test_gate_regressions.py (new) in the candidate copy. Must not change: anything in the checkout.
- Test seam: the hook scripts as processes with synthetic transcripts and events, as tests/test_phase_gate_hook.py already does. Misses: real host timing. V2 covers it.
- TDD: yes. These tests are expected to fail before H2 to H4. Each failing test names the ticket that fixes it.

How to verify:
- In the candidate: `python -X utf8 -m unittest discover -s tests -p "test_gate_regressions.py" -v`. Expected: the reproduced failures fail, the adversarial cases that the current gate already blocks pass. Output: .artifacts/2026-11-11-consistency-review-findings/.

Docs and cleanup: none.

Verification: passed

References:
- Supports: R12, R16, A6, A7
- Depends on: none
- Rules: AGENTS.md (hook candidates in isolation), tests/README.md
- Evidence: V4

### H2 — Enter a phase only through a real phase start
Status: Verified

What should work:
- Reading a phase SKILL.md no longer starts that phase. A phase starts through a Skill call or a typed command, or a whole read of the SKILL.md under CLAUDE_PLUGIN_ROOT while a workflow session is already active.
- plain_reply.py treats a session as a workflow session only after such a start or a task-record write, not when a path contains "workflow-axa".
- Every existing phase_gate and plain_reply test still passes. Changed tests are listed with the reason.

Technical details:
- May change, in the candidate: hooks/phase_gate.py, hooks/plain_reply.py, their tests. Must not change: approval rules, write blocking, install blocking.
- Test seam: hook processes with transcripts. TDD: yes, the H1 tests for these two items go green.

How to verify:
- In the candidate: the hook test files (test_phase_gate_hook.py, test_plain_reply_hook.py, test_phase_reads_hook.py, test_truncated_read_hook.py, test_duplicate_skills_hook.py) and test_gate_regressions.py. Expected: green except H3/H4 items. test_line_endings skips without .git, so H6 reruns everything in the checkout.

Verification: passed

References:
- Supports: R12, A6
- Depends on: H1
- Rules: AGENTS.md
- Evidence: V10, V11; reviews of H2 in FINDINGS

### H3 — Keep edits of one task working while another task's records change, and close the chained-command pass
Status: Verified

What should work:
- Writing a record of task B does not stop an edit that task A's approved write_paths cover, when task B has approved write_paths of its own and the file is outside them. In every other case the gate keeps today's stop and asks: task B has no write_paths yet (unapproved or an older report), task A's report has no write_paths, task A is approved for another revision, or the file is in both. This only narrows a stop, it never widens an approval.
- Tests for each of those cases, including the three where the stop must remain.
- Git commands that write files (`git apply`, `git checkout -- <file>`, `git restore`) are checked against the current task's approved write_paths like an Edit (D36). For `git apply`, the files come from the patch (`git apply --numstat` or the patch headers). A file outside the list is refused.
- The gate recognizes a task-record write made through a shell variable that holds the record.py command (D36), so the current task follows such writes.
- The `git apply` cases from H1 are refused without approval, and refused for files outside the approved list.
- Existing approval protections keep their tests.

Technical details:
- May change, in the candidate: hooks/phase_gate.py and its tests. TDD: yes.
- If the fix for the chained command needs a change to what counts as approval, the ticket stops and goes to the owner.

How to verify:
- In the candidate: the hook tests and test_gate_regressions.py. Expected: green except H4 items.

Verification: passed

References:
- Supports: R12, R16, A6, A7
- Depends on: H2
- Rules: AGENTS.md
- Evidence: V13, V16; reviews of H3 in FINDINGS

### H4 — Let the gate accept the small-change route
Status: Verified

What should work:
- A checkpoint line `- Small change: <files> — <what changes>` allows writes to the listed existing files only, without an HTML report, when the Approval line quotes a user message that came after an assistant message naming the same files with "Small change:". This is the same kind of rule the gate already uses for a shown report path.
- plain_reply.py does not demand the report guides for a small change.
- A write to a file not listed, or the creation of a new file, is refused with the message to switch to the full route. Package installs stay blocked as today. An interface or behavior change that fits inside the listed files cannot be seen by a hook: that limit is enforced by instructions only, and L1 says so.

Technical details:
- May change, in the candidate: hooks/phase_gate.py, hooks/plain_reply.py and their tests. Must not change: hooks/hooks.json.
- TDD: yes.

How to verify:
- In the candidate: all hook tests and test_gate_regressions.py. Expected: all green.

Verification: passed

References:
- Supports: R11, R12, A6, A7
- Depends on: H3
- Rules: AGENTS.md
- Evidence: V18; reviews of H4 in FINDINGS

### H5 — Name overlapping process plugins at session start
Status: Verified

What should work:
- When the Claude settings (user and project settings.json `enabledPlugins`) enable a known overlapping process plugin (superpowers), the session-start note adds one line: which of its skills overlap workflow-axa phases, that the workflow-axa phase skills are used while a workflow task runs, and that the owner may disable the other plugin in the project. Nothing is disabled.
- No overlap, unreadable settings or malformed JSON: nothing is added. The duplicate guard's existing behavior and tests stay.

Technical details:
- May change, in the candidate: hooks/duplicate_skills.py, tests/test_duplicate_skills_hook.py. The known overlapping plugins are one short list in the script.
- Test seam: the script as a process with temporary settings files. TDD: yes.

How to verify:
- In the candidate: `python -X utf8 -m unittest discover -s tests -p "test_duplicate_skills_hook.py" -v`. Expected: all pass.

Verification: passed

References:
- Supports: R13, A12
- Depends on: H1
- Rules: AGENTS.md
- Evidence: V5, V6; reviews of H5 in FINDINGS

### H6 — Copy the verified hooks into the checkout
Status: Verified

What needs to happen: Prerequisite that makes H2 to H5 take effect. Copy exactly these files from the candidate to the checkout: hooks/phase_gate.py, hooks/plain_reply.py, hooks/duplicate_skills.py and the test files H1 to H5 changed or created.

What should work:
- Before copying, each checkout file's hash equals the hash saved in H1. A difference stops the copy and is reported, because someone changed the checkout meanwhile.
- Each file is replaced in one step (temporary file in the same folder, then replace), so no session sees a half-written hook.
- Every session that loads the plugin from D:\workflow-axa, including the session doing this work, uses the new hooks from its next event on. This is expected and named in the checkpoint before the copy.

Technical details:
- May change: the listed files in the checkout. TDD: no (copy).

How to verify:
- In the checkout: all hook tests, test_gate_regressions.py, `python -X utf8 tools/validate.py` and the full suite. Expected: the baseline result plus the new tests, baseline failures named separately.

Verification: passed

References:
- Supports: R12, A6, A7, A12
- Depends on: H4, H5
- Rules: AGENTS.md (hook candidates in isolation)
- Evidence: V19; also the reply-mark repair E41 (V-E41), built and reviewed in the candidate after H6 and copied the same way

### D1 — Check documentation structure with a script
Status: Verified

What needs to happen: A new standard-library script reads a repository's instruction files and documentation index and reports structural problems with a severity.

What should work:
- Starting from AGENTS.md (and CLAUDE.md), it follows Markdown links into subordinate indexes and documents. It reports: no AGENTS.md, CLAUDE.md that is not a one-line import or duplicates AGENTS.md, broken links, documents under the usual documentation folders that nothing reaches, cycles, index depth over two, AGENTS.md over its advisory size, and repeated paragraphs across instruction files.
- Each finding has a severity: blocking (a broken link to a document marked required with the existing required-read marker), warning, or note. Exit code is non-zero only for blocking findings.
- Read-only. Output as text and JSON.

Technical details:
- May change: skills/rule-maker/scripts/docs_check.py (new), tests/test_docs_check.py (new). The fixture repositories (missing docs, nested docs, stale references, conflicting rules, renamed files, monorepo, several instruction files, undocumented code) are built in a temporary folder by the test code, as test_docs_consistency.py already does, so their deliberately broken links never reach the package validator or an agent's folder walk.
- The repeated-paragraph check is one function in docs_check.py. L3 calls the same function.
- Necessity: no existing script reads link graphs. readiness.py hashes rule files and rules_stamp.py reads a version line. D3 decides with evidence whether either can be retired.
- Test seam: the script as a process on the fixture repositories. TDD: yes, each finding type has a negative test.

How to verify:
- `python -X utf8 -m unittest discover -s tests -p "test_docs_check.py" -v`. Expected: all pass.

Verification: passed

References:
- Supports: R1, R4, R7, R16, A1, A3
- Depends on: none
- Rules: AGENTS.md
- Evidence: V3, V7, V8, V9; reviews 1 to 3 of D1 in FINDINGS

### D2 — List related documents and check named facts
Status: Verified

What should work:
- Given changed files (a list or `git diff --name-only`), the script lists the related documents and why: the document links to or names the path, the document sits in the folder, or an optional directory-level Covers hint matches. A hint that matches no path is reported as stale.
- For the related documents, it checks named facts: named paths exist, named commands exist in the project's manifests (package.json scripts, composer.json scripts, Makefile targets), and named versions match the manifests through version_facts.py. Each fact is reported as matched, contradicted or not checkable.
- It never reports a document as accurate. It reports which facts it checked. The agent's claim review covers meaning.

Technical details:
- May change: skills/rule-maker/scripts/docs_check.py, tests/test_docs_check.py.
- TDD: yes. Fixtures include a wrong command, a wrong module path and a renamed file.
- The meaning of a claim (a wrong described behavior, a business claim) is not judged here. W1a's claim review does that, and V2 session 3 observes it.

How to verify:
- `python -X utf8 -m unittest discover -s tests -p "test_docs_check.py" -v`. Expected: all pass.

Verification: passed

References:
- Supports: R5, R6, A2, A4
- Depends on: D1
- Rules: AGENTS.md
- Evidence: V12, V14, V15; reviews 1 to 3 of D2 in FINDINGS

### D3 — Redesign rule-maker around entry point, index and three operations
Status: Verified

What should work:
- skills/rule-maker/SKILL.md describes three operations: audit (read-only, runs docs_check, writes a proposal: problems, proposed AGENTS.md, indexes, moves, risks, auto-loaded words before and after), apply (only an approved proposal), check (the script).
- A new reference file DOCS.md holds: the responsibility table (what belongs in AGENTS.md, CLAUDE.md, CONTEXT.md, docs/architecture.md, docs/adr/, nested indexes), the short AGENTS.md shape with its index format and "read when" lines, the one-line CLAUDE.md, the claim review procedure (verified with evidence, contradicted, not verified with reason), the severity rules, and how a nested package is handled. For the CONTEXT.md and ADR formats it points to domain-modeling instead of restating them, and states that the project file is named CONTEXT.md (the vendored format text says GLOSSARY.md).
- Readiness (rules/READINESS.md) takes facts from the script. The sentences that rule out any structure or migration are replaced by D11 and D22. Valid existing rules still pass.
- The shared standards library and its global imports stay. rules/version.json is regenerated with tools/update_rules_manifest.py.

Technical details:
- May change: skills/rule-maker/SKILL.md, AUDIT.md, SETUP.md, CHECKER.md, DOCS.md (new), rules/READINESS.md, rules/version.json, and readiness.py or rules_stamp.py only if D3 retires a function with evidence.
- TDD: no for the prose. The existing rule tests (test_rules.py, test_rules_audit.py, test_rules_stamp.py) must pass or be changed with a stated reason.
- Budget: rule-maker SKILL.md is at 850 of 850 words. Text moves to DOCS.md.

How to verify:
- `python -X utf8 tools/validate.py` and the rule test files. An independent reviewer reads SKILL.md and DOCS.md against R1 to R8.

Verification: passed

References:
- Supports: R1, R2, R3, R4, R6, R7, R8, A10
- Depends on: D2
- Rules: AGENTS.md, VENDORED-SKILLS.md
- Evidence: V17; reviews of D3 in FINDINGS

### W1a — Add the documentation step to the phases
Status: Verified

What should work:
- Clarify finds the documents related to the task through AGENTS.md and docs_check, and notes suspected staleness. Specify names the documents each ticket changes. Execute passes the related documents to workers and updates documents with the code. Deliver runs docs_check on the changed files and reports each affected code-related claim as verified (with evidence), contradicted, or not verified (with the reason), and lists document changes.
- An unsafe contradiction stops the task and goes to the owner (R7). A minor one is reported at delivery.
- TASK-FOLDER.md: the ticket template has a Documents line, and agreement revisions are written as "agreement N", never "rN", because the gate reads any rN in the checkpoint as a plan revision (D37). GROUNDING.md says how a claim is checked against code.
- Each step is one or two sentences that point to rule-maker DOCS.md. Skill word budgets hold. Words are cut elsewhere where needed.

Technical details:
- May change: skills/workflow-clarify/SKILL.md, workflow-specify/SKILL.md, workflow-execute/SKILL.md, workflow-deliver/SKILL.md, workflow/TASK-FOLDER.md, workflow/GROUNDING.md, and the tests that assert phrases it changes (each change with its reason).
- TDD: no (instructions).

How to verify:
- `python -X utf8 tools/validate.py`, tests/test_behavioral_cases.py and the other test files it touched.
- A fresh subagent that did not build it runs the claim review on a fixture with a wrong documented command, a wrong module path, a wrong described behavior and a business claim, using only the new instructions. Expected: the first three contradicted with evidence, the last not verifiable.

Verification: passed (V23 fresh-agent claim review on the claimfix fixture: three contradicted with evidence, the business claim not verifiable; V24 final files: validate.py PASS, phase-skill test files OK, full suite only the four baseline failures)

References:
- Supports: R5, R6, R7, A4, A9
- Depends on: D3
- Rules: AGENTS.md
- Evidence: V23, V24

### W1b — Choose UI elements by the job they do for the user
Status: Verified

What should work:
- For a user-facing change, clarify writes a short purpose statement (who, situation, goal, what must stand out) from CONTEXT.md and the code. When missing intent would change the result, the agent asks. It never invents product intent.
- ui-design and design.md rule 4: find the element by the job it does for that user, then mirror its tag and classes, and record why. The selection record gains "why". The TASK-FOLDER agreement template has the purpose lines and the ticket template a Purpose line. Execute passes the purpose to workers.

Technical details:
- May change: skills/workflow-clarify/SKILL.md, workflow/TASK-FOLDER.md, workflow-execute/SKILL.md, ui-design/SKILL.md, ui-design/CONTRACT.md, rule-maker/rules/design.md, rule-maker/rules/version.json (regenerated), and the tests that assert phrases it changes (tests/test_ui_design.py, tests/test_behavioral_cases.py).
- TDD: no (instructions).

How to verify:
- `python -X utf8 tools/validate.py`, tests/test_ui_design.py, tests/test_behavioral_cases.py.

Verification: passed (V25: validate.py PASS, test_behavioral_cases OK, test_ui_design only its baseline failure; both reviews closed)

References:
- Supports: R9, A13
- Depends on: W1a
- Rules: AGENTS.md
- Evidence: V25, V32 (A13)

### W1c — Ask fewer, better questions
Status: Verified

What should work:
- The grilling adaptation and clarify step 2: research first, plain engineering choices become stated assumptions, only choices that change product intent, architecture, risk or irreversible outcomes are asked, grouped, each with a recommendation and its trade-off. Silence is never approval. The vendored upstream text stays byte for byte.

Technical details:
- May change: skills/grilling/SKILL.md (adaptation section only), skills/workflow-clarify/SKILL.md, and the tests that assert phrases it changes.
- TDD: no (instructions).

How to verify:
- `python -X utf8 tools/validate.py`, tests/test_vendored_specialists.py, tests/test_behavioral_cases.py.

Verification: passed (owner accepted A14 as met, D43; V33: plain engineering choices stated as assumptions, the product choice asked with a recommendation, plus one visible-change question the agreed rule requires); file checks V26 passed. For the owner at delivery

References:
- Supports: R15, A14
- Depends on: W1b
- Rules: AGENTS.md, VENDORED-SKILLS.md
- Evidence: V26; V33, D43

### L1 — Describe the small-change route
Status: Verified

What should work:
- skills/workflow/SKILL.md, VISUAL-REVIEW.md and TASK-FOLDER.md describe the small-change route exactly as H4 enforces it: what qualifies, the chat before and after, the owner's quoted yes, tests and one review, no HTML report or screen diagram, and the switch to the full route.
- The lightweight edit and the small change are two named routes with one sentence each on the difference.
- It states that the hook enforces the file list and the quoted yes, and that "no interface or behavior change beyond the description" is enforced by instructions only.

Technical details:
- May change: skills/workflow/SKILL.md, workflow/VISUAL-REVIEW.md, workflow/TASK-FOLDER.md, workflow/SETUP.md (what the hooks enforce), and the tests that assert phrases it changes.
- TDD: no (instructions).

How to verify:
- `python -X utf8 tools/validate.py` and the behavioral tests. An independent reviewer compares the prose with H4's tests.

Verification: passed (V27: independent comparison with H4's code and tests, repairs re-checked; validate.py PASS; test_behavioral_cases OK)

References:
- Supports: R11, A9, A15
- Depends on: H6, W1c
- Rules: AGENTS.md
- Evidence: V27

### L3 — Add budgets, the term and owner table, and the term check to the package validator
Status: Verified

What should work:
- tools/validate.py checks word budgets for reference files. The ceilings start at today's sizes, so no ticket turns the validator red while it works. T3 lowers them to the sizes after the consolidation.
- It reports paragraphs repeated across skill files, by calling the duplication function of docs_check.py.
- A CONTEXT.md at the repository root holds: the package vocabulary (one term per concept with its rejected synonyms), the spelling rule, the identifiers that keep their old spelling, and the owner table: for each rule stated in several files today (for example "never write CSS", design.md rule 4's question, "never commit unasked", "agreement is not permission to code"), the one file that owns it. The T2 workers follow this table, so they choose the same owner.
- The synonym list is advisory until T3 and failing after it.

Technical details:
- May change: tools/validate.py, tests/test_validate_budgets.py (new), CONTEXT.md (new at the root).
- TDD: yes.

How to verify:
- `python -X utf8 -m unittest discover -s tests -p "test_validate_budgets.py" -v` and `python -X utf8 tools/validate.py`.

Verification: passed (V21: test_validate_budgets 10 OK, validate.py exit 0; ceilings at size plus 10 percent, see DECISIONS)

References:
- Supports: R10, R14, R16, A8, A9
- Depends on: D1
- Rules: AGENTS.md
- Evidence: V21

### L4 — Archive obsolete root documents
Status: Verified

What should work:
- AUDIT-rc5.md and UI-LITE-HANDOFF.md move to docs/archive/ after a reference search shows no test, tool or shipped file needs them. Old plan records that mention them get no edit. CANDIDATE-REVIEW.md, RC3-CASES.md and CLAUDE-TEST-PROMPT.txt stay, because tests and the release tool use them.

Technical details:
- May change: those two files (moved), docs/archive/ (new). TDD: no.

How to verify:
- `python -X utf8 tools/validate.py` and the full suite in T3.

Verification: passed

References:
- Supports: R14
- Depends on: none
- Rules: AGENTS.md
- Evidence: V2

### T2a1 — Consolidate and align the wording of skills/workflow
Status: Verified

What should work:
- In skills/workflow (SKILL.md and its reference files): the CONTEXT.md terms, American spelling, each rule stated once in the file the owner table names with a pointer elsewhere, and version history removed while the live rule stays.
- Explanations of what a check does not prove, where the agent does not act on them, are cut and written with their source line to a list for T3. The worker does not edit docs/EVALUATION.md.
- Every changed asserted phrase goes to a list for T3. The worker does not edit tests.

Technical details:
- May change: skills/workflow/**/*.md only. TDD: no.

How to verify:
- `python -X utf8 tools/validate.py` (budgets and synonym report). T3 runs the tests.

Verification: passed (V28: validate.py PASS; independent review closed; tests run in T3)

References:
- Supports: R10, R14, A9
- Depends on: L1, L3
- Rules: AGENTS.md
- Evidence: V28

### T2a2 — Consolidate and align the wording of the phase and status skills
Status: Verified

What should work: the same as T2a1 for skills/workflow-clarify, workflow-specify, workflow-execute, workflow-deliver, resume-task, task-status, plan-review and workflow-doctor.

Technical details: may change those folders' .md files only. TDD: no.

How to verify: `python -X utf8 tools/validate.py`. T3 runs the tests.

Verification: passed (V30: validate.py PASS; review and two repair re-checks closed; tests run in T3)

References:
- Supports: R10, R14, A9
- Depends on: L1, L3
- Rules: AGENTS.md
- Evidence: V30

### T2b — Consolidate and align the wording of codebase-map and ui-design
Status: Verified

What should work: the same as T2a1 for skills/codebase-map and skills/ui-design. The owner's report patch content is kept. Only wording, duplicates and history change.

Technical details: may change skills/codebase-map/*.md and skills/ui-design/**/*.md. Must not change scripts or tests. TDD: no.

How to verify: `python -X utf8 tools/validate.py`. T3 runs the tests.

Verification: passed (V28: validate.py PASS; independent review and repair re-check closed; tests run in T3)

References:
- Supports: R10, R14, A9
- Depends on: L1, L3
- Rules: AGENTS.md
- Evidence: V28

### T2c — Consolidate and align the wording of rule-maker
Status: Verified

What should work: the same as T2a1 for skills/rule-maker, including rules/*.md. CORE.md stays at or under 650 words and each engineering module at or under 450. rules/version.json is regenerated with tools/update_rules_manifest.py.

Technical details: may change skills/rule-maker/**/*.md and rules/version.json. Must not change scripts or tests. TDD: no.

How to verify: `python -X utf8 tools/validate.py` and `python -X utf8 tools/update_rules_manifest.py` (preview, then apply). T3 runs the tests.

Verification: passed (V29: validate.py PASS, manifest current, size limits hold; review and repair re-check closed; tests run in T3)

References:
- Supports: R10, R14, A9
- Depends on: L1, L3
- Rules: AGENTS.md
- Evidence: V29

### T2d — Consolidate and align the wording of the other skills and package docs
Status: Verified

What should work: the same as T2a1 for the adaptation sections of grilling, tdd, code-review, simple-english, and for writing-for-agents, domain-modeling, codebase-design, implement-spec, retro, README.md, UPGRADE.md and docs/ARCHITECTURE.md. Vendored upstream text stays byte for byte. docs/EVALUATION.md is left to T3.

Technical details: may change those files. Must not change tests or vendored text. TDD: no.

How to verify: `python -X utf8 tools/validate.py` and the vendored-text tests in T3.

Verification: passed (V28: validate.py PASS; vendored text byte-identical; independent review closed; tests run in T3)

References:
- Supports: R10, R14, A9
- Depends on: L1, L3
- Rules: AGENTS.md, VENDORED-SKILLS.md
- Evidence: V28

### T3 — Merge moved explanations, update asserted phrases and run the whole suite
Status: Verified

What should work:
- The limit explanations the T2 workers listed are merged into docs/EVALUATION.md once each, grouped by component.
- Each phrase on the T2 lists is updated in the tests that assert it, with the same meaning. No assertion is weakened or removed to pass.
- The reference-file ceilings are lowered to the new sizes. The synonym check becomes failing.
- The full suite gives the baseline result plus the new tests. The four baseline failures are named separately. Any other failure is fixed or reported.

Technical details:
- May change: docs/EVALUATION.md, tools/validate.py (ceilings), tests/*.py and tests/behavioral/*.json where a phrase is asserted. TDD: no.

How to verify:
- `python -X utf8 tools/validate.py` and `python -X utf8 -m unittest discover -s tests -p "test_*.py"`. Output kept in .artifacts/2026-11-11-consistency-review-findings/.
- One independent whole-feature review against agreement r2, Standards and Spec.

Verification: passed (V31 build; whole-feature review and every repair re-checked, V37 and V40; full suite V38: 1216 tests, one intermittent failure that predates the task, passing alone three times)

References:
- Supports: R10, R14, A8, A9
- Depends on: T2a1, T2a2, T2b, T2c, T2d
- Rules: AGENTS.md, tests/README.md
- Evidence: V31, V37, V38, V40

### X1 — Release notes and version
Status: Verified

What should work:
- One CHANGELOG entry for this task, and a rules/CHANGES.md entry with a rules_version bump for the READINESS.md change (D3 note: "docs_check facts are advisory; two blocking documentation conditions", project action: none). The version moves to 2.8.0-rc.36 in every file the package validator ties to plugin.json, in RENDERER_VERSION, and in the candidate_version of tests/behavioral/*.json, which also removes the four baseline failures. layout_version moves from 2 to 3, as the owner asked for the report patch ("Set RENDERER_VERSION and layout_version with the release").
- The shared rules copy in ~/.agents/skills then differs from the plugin, and the duplicate guard warns at session start until the owner updates that copy. This is expected and named in the delivery.

Technical details:
- May change: CHANGELOG.md, .claude-plugin/plugin.json, .claude-plugin/marketplace.json, skills/rule-maker/rules/version.json, skills/workflow/specialists.json, skills/codebase-map/scripts/render_report.py (two constants), tests/behavioral/*.json (candidate_version), README.md, UPGRADE.md and VALIDATION.md (version line). TDD: no.

How to verify:
- `python -X utf8 tools/validate.py` and the full suite. Expected: the four baseline failures are gone and nothing else changes.

Verification: passed (V35 suite OK with the four baseline failures gone; V40 changelog final; review of the release notes closed)

References:
- Supports: R14
- Depends on: T3
- Rules: AGENTS.md
- Evidence: V35, V40

### V1 — Audit the accessible repositories read-only
Status: Verified

What should work:
- For each of the 11 repositories: rule-maker audit runs read-only, docs_check runs, and a proposal is written under .artifacts/2026-11-11-consistency-review-findings/audits/<repository>.md with current problems, the proposed AGENTS.md and indexes, document moves, a code and documentation check of a sample of claims (verified, contradicted, not verified), migration risks, and the words auto-loaded today and after the proposal.
- A summary table across repositories. Findings that show a design flaw go back into this task before V2.
- No file in any of those repositories changes. Before and after, `git status` (where Git exists) and a file hash list are compared.

Technical details:
- May change: only .artifacts/2026-11-11-consistency-review-findings/audits/. Workers may run in parallel, one per repository.
- TDD: no.

How to verify:
- The before and after hash lists are equal for every repository. A reviewer checks two proposals against their repository.

Verification: passed (V36: 11 read-only audits, before and after snapshots identical; summary in audits/SUMMARY.md); two proposals checked by an independent reviewer and all 11 revised for the safety rule; design flaws repaired and re-reviewed, V37)

References:
- Supports: R8, R18, A10
- Depends on: X1
- Rules: AGENTS.md, each audited repository's own rules (read only)
- Evidence: V36, V37

### V2 — Run realistic sessions within the cap and the host checks
Status: implemented — verification pending

What should work:
- Disposable projects under .artifacts/2026-11-11-consistency-review-findings/runs/, built from the fixture generator.
- Cost control per invocation, because each `claude -p` call has its own cap: at most 5 sessions and at most 9 invocations in total, each `claude -p --model claude-sonnet-5-5 --max-budget-usd 0.40 --output-format json`, resumed steps with `--resume <session id>`. The first invocation is a cheap probe that confirms the JSON reports a cost. If it does not, no further paid invocation starts and the agent asks. An invocation starts only when the costs reported so far plus 0.40 stay at or under 4.00, which leaves 1.00 for calls that finish after a cap is hit. Any invocation that reports more than 0.60 stops the batch.
- Limits that remain, named in the delivery: the CLI does not bound the call that is already running when a cap is reached. The reported cost is an estimate at API prices. On a subscription account it is not the amount billed. Sessions also load the owner's global CLAUDE.md and enabled plugins, as real sessions do.
- The sessions: (1) a project-local one-line `@AGENTS.md` loads in a fresh session: AGENTS.md holds a unique word, and the session must repeat it with file tools disabled. (2) a small change through the small-change route. (3) a task that changes a documented command and a documented behavior: the agent must update the document and report the claims as verified, contradicted or not verified (A4). (4) stale and conflicting documentation, including one contradiction that must stop the task (R7). (5) an interrupted and resumed task with an approval line for another revision.
- Human checks, asked together at delivery: the guard r2 messages in a live session, and a refused agent-made Skill call. Codex: not installed here, reported as not tested.

Technical details:
- May change: only .artifacts/2026-11-11-consistency-review-findings/runs/. TDD: no.

How to verify:
- Each invocation's JSON kept with its cost. The total is reported. Results are reported as observations of these runs only.
- Human check: the owner, at delivery: the two live checks above.

Verification: limited: V39 — A5 passed; A11 partial (the documentation step was shown only partly: s3 sent the stale document back but ran no docs_check, s4 did not start the workflow; s5's resume case passed); A4 partial; A15 end to end and R7 not shown in live sessions (the gate defect found was fixed, V40, but not rerun live; a plain prompt did not start the workflow); 9 of 9 invocations used, 2.6431 USD reported; human checks and Codex not run

References:
- Supports: R2, R7, R16, R17, A4, A5, A11
- Depends on: V1
- Rules: AGENTS.md
- Evidence: V39, V40 (the gate defect V2 found, fixed)

## Bigger checks

- After H6: all hook tests, the gate regressions and the full suite in the checkout.
- After D3 and W1a: docs_check on this repository and on two fixtures, run by hand and the output read.
- After T3: the full suite, the package validator with the synonym check failing on any remaining synonym, and one independent whole-feature review against agreement r2.
- Not checkable here: Codex behavior (not installed), the cost of a call that is running when a cap is reached, and anything the capped runs do not cover.

### Y1 — Apply workflow-axa's own audit proposal (revision r2)
Status: Verified

What needs to happen: apply the reviewed audit proposal for this repository (.artifacts/2026-11-11-consistency-review-findings/audits/workflow-axa.md) in full, as the owner chose (D44, D48), so this repository follows the shape it now asks of others.

What should work:
- CLAUDE.md is the one line `@AGENTS.md`; AGENTS.md is the proposal's text: every existing rule and boundary kept, the commands that write global instructions, vendored skills or VALIDATION.md (`activate_rules.py --apply`, `global_policy.py --apply`, `tools/vendor_specialists.py`, `tools/verification_summary.py --run --write`) named as needing the owner's OK, the two check commands, and an index with "Read when" lines (CONTEXT.md, README.md, docs/ARCHITECTURE.md, docs/EVALUATION.md, docs/DESIGN.md as history, VENDORED-SKILLS.md, tests/README.md).
- README.md and docs/EVALUATION.md no longer name tools/build_source.py or tools/fresh_runs.py (they never existed); README.md:18 no longer claims GitHub checks that do not exist; README.md:88 says the check commands install no hook (the plugin's hooks stay registered). CHANGELOG rc.36 records these corrections; the rc.35 entry stays as history.
- tools/build_release.py ships docs/ARCHITECTURE.md and docs/EVALUATION.md, which README links, with tests/test_release.py updated.
- CANDIDATE-REVIEW.md, RC3-CASES.md and CLAUDE-TEST-PROMPT.txt move to docs/archive/, with tools/build_release.py, tools/validate.py REQUIRED, tests/test_rc3_reliability.py and tests/README.md:28 updated in the same change; tests/README.md's rc.1 baseline section is marked historical and points to docs/EVALUATION.md.
- Not included: restoring the two missing tools, adding a GitHub workflow, renaming docs/DESIGN.md, the rules-checked stamp line.

Technical details:
- May change: AGENTS.md, CLAUDE.md, README.md, CHANGELOG.md, docs/ (EVALUATION.md, archive/), tests/README.md, tests/test_release.py, tests/test_rc3_reliability.py, tools/build_release.py, tools/validate.py, CANDIDATE-REVIEW.md, RC3-CASES.md, CLAUDE-TEST-PROMPT.txt (moved). Must not change hooks/ or skills/.
- Test seam: tools/validate.py, tests/test_release.py, tests/test_rc3_reliability.py and docs_check; TDD: yes for the build_release and validator changes (a test that names the moved or shipped file fails first), no for wording.

Documents: AGENTS.md, CLAUDE.md, README.md, docs/EVALUATION.md, tests/README.md

How to verify:
- `python -X utf8 tools/validate.py`, the full suite, `python -X utf8 -I skills/rule-maker/scripts/docs_check.py D:/workflow-axa` plain and `--changed` on the changed files, and a claim review of the new AGENTS.md; output in .artifacts/2026-11-11-consistency-review-findings/apply/.
- One independent review, Standards and Spec.

Verification: V45. validate.py PASS; full suite 1222 OK, 14 skipped; docs_check 0 blocking, 0 warning; independent review done, repairs checked.

References:
- Supports: R1, R2, R8, agreement 4
- Depends on: V1
- Rules: AGENTS.md
- Evidence: V45 (2026-11-11): full suite 1222 OK, 14 skipped (apply/workflow-axa-suite-final.txt; again 1222 OK after Y2); validate.py PASS; docs_check 0 blocking 0 warning; independent review: findings 1 and 3 fixed, 2 reported to the owner, 4 and 6 accepted as wording; finding 5 (reviewer-marked optional Low) descoped because root AGENTS.md is outside the approved write paths

### Y2 — One-word document names in capitals (revision r3)
Status: Verified
Evidence: V46 (2026-11-11): 20 git mv renames; full suite 1222 OK, 14 skipped (apply/workflow-axa-y2-suite-final.txt); validate.py PASS; docs_check 0 blocking 0 warning; independent review, axes sequential: Spec PASS, Standards Medium/Low/Nit repaired and re-reviewed closed

What needs to happen: rename the 20 one-word rules modules in skills/rule-maker/rules/ to capitals with `git mv`, update every live reference, state the naming rule in rule-maker DOCS.md, and release the rules as 1.8.7 (D52, r3).

What should work:
- skills/rule-maker/rules/ holds DESIGN.md, REACT.md, OPERATIONS.md and the other 17 modules in capitals; git records each as a rename.
- No live file names a lowercase module (excluded: docs/plans, docs/archive, CHANGES.md history entries, vendored skills/tdd, test fixtures).
- rule-maker DOCS.md says one-word Markdown document names are written in capitals.
- Rules 1.8.7: CHANGES.md entry, version.json, regenerated manifest; validate.py, the full suite and docs_check pass.
- Not included: vendored skills/tdd/mocking.md and tests.md; fixture files under tests/fixtures.

Technical details:
- Supports: R20, A17. Depends on: Y1. TDD: no for the rename (mechanical; the suite and validate.py are the check); yes if a docs_check rule is added.
- How to verify: `python -X utf8 -I tools/validate.py`; full suite; docs_check on the repository; `git grep` for each old name outside the exclusions returns nothing.
