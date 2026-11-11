# Consistency: the review findings

## Current checkpoint
- Updated / phase: 2026-11-11; delivered (partial): see ## Outcome
- Agreement (gate one): agreed 2026-11-11, agreement 4 (adds R19 and A16 to agreements 2 and 3), the owner said "no need for report i approve already"; earlier agreement words: D24 to D35
- Approval (gate two): r3 approved, 2026-11-11, no report: "Approve r3, no report (Recommended)"
- Reconfirmed (gate two): r3, 2026-11-11: "Yes, r3 holds as approved"
- Implementation: implemented. Verified: H1-H6, D1-D3, W1a, W1b, L1, L3, L4, T2a1-T2d, T3, X1, V1, Y1 (V45), Y2 (V46). Verification pending: W1c (A14 partial), V2 (live results limited)
- Verification / owner acceptance: full suite 1219 OK on the final files (V41 and final review), validate.py PASS, A4 and A13 rerun passed (V42, V43); partial items and owner rulings listed in ## Outcome; owner acceptance pending
- Blockers: none. Owner rulings pending: R12 (H2), A14, A6, a paid rerun for A15 and R7, plain prompts starting the workflow
- Changed files: hooks/phase_gate.py, plain_reply.py, duplicate_skills.py; tests (test_gate_regressions.py, test_docs_check.py, test_validate_budgets.py, test_phase_gate_hook.py, test_plain_reply_hook.py, test_duplicate_skills_hook.py, test_behavioral_cases.py, test_engineering_rules.py, test_rules.py, test_rules_audit.py, tests/behavioral/*.json, tests/README.md); skills/rule-maker/scripts/docs_check.py; tools/validate.py; CONTEXT.md; docs/EVALUATION.md; docs/archive/ (two moved files); wording in every skill under skills/, rules 1.8.6 (CHANGES.md, version.json), README.md, UPGRADE.md, VALIDATION.md, docs/ARCHITECTURE.md, CHANGELOG.md, .claude-plugin/plugin.json, skills/workflow/specialists.json, render_report.py. hooks/hooks.json is not changed by this task (guard task). Full list: .artifacts/2026-11-11-consistency-review-findings/delivery-state.txt
- Next safe action: commit and push rc.36 (D50), update the installed plugin from Git and test it; then PletrixV2 (branch approval first). Repository applications: D51, D53; pushes D54

## Working context
- Owner: Gazoh; repository D:\workflow-axa, branch main, main checkout
- Task identity: the second task the owner chose in the guard task's Q4 ("Separate second task"). Parts: one language (1), purpose awareness in UI work (3), consistent rule-maker (4), lighter rules (5). Part 2, the report rework, arrived as the owner's finished patch and is its own task: docs/plans/2026-11-11-report-rework.
- The owner asked on 2026-11-11 to run as many parts in parallel as possible. Investigation runs in parallel now. Build tickets will be cut by file ownership so they can run side by side after approval.
- Rules: READY / AGENTS.md, tests/README.md / scope: skills, hooks, tests
- Test output folder: .artifacts/2026-11-11-consistency-review-findings/

## Goal and acceptance
The owner's words (2026-11-11): "1. I feel like the language is to different ... 3. we are missing context-aware when its building something it makes it because it has to make it not really understanding what its making and for who so the UI elements are just randomly chosen it has to be aware of for who also its meant to be build for and why. 4. rule maker is not consistent accross repo's 5. any thing you can think of your opinion thinking that needs improvements?" and "I want consistency".

## Agreement

Agreement 2, agreed 2026-11-11. Agreement 1 (proposed the same day) plus the owner's nine adjustments, marked [adj N]. The owner's answer: "I agree with the revised architecture, with the following adjustments before creating the detailed implementation plan." (DECISIONS D24 to D33.)

### Design
- The index in AGENTS.md is the manifest. No generated manifest. A small script reads the Markdown links from AGENTS.md and from the indexes it links, and reports broken links, documents nothing reaches, cycles, depth and size.
- Shallow nested indexes are supported: AGENTS.md may link a subordinate index (for example docs/README.md or a package's AGENTS.md), which links its own documents. Not every document has to appear in the root index. More than two index levels is reported as advisory. [adj 1]
- A new project starts with AGENTS.md, a one-line CLAUDE.md and CONTEXT.md (product, users, terms). docs/architecture.md and docs/adr/ are added when there is content for them. Existing locations are kept when they work. No file is created only to fill a template.
- AGENTS.md keeps the common build and test commands. Complex setup and environment details go to referenced documents. [adj 2]
- Code-to-document relationships are discovered automatically: a document covers the paths it links to or names, and a document inside a folder covers that folder. An index entry may add an optional "Covers" hint with directory-level patterns. No mapping of individual source files is kept by hand. A hint that matches no path is reported as stale. [adj 4]
- No caching of read documents. The host keeps what was read. After compaction or a file change a reread is correct. On resume, the recorded commit and `git diff` show which documents changed.
- No new skill. Rule-maker owns project instructions and documentation structure. Each workflow phase has one short documentation step. The shared standards library stays where the global instructions import it.

### Requirements
- R1: AGENTS.md is short: essential rules, boundaries and safety rules, the common build and test commands, and an index with one line per entry on what it holds and when to read it. Advisory budget about 1,200 words. [adj 1, 2]
- R2: CLAUDE.md is the line `@AGENTS.md`. A fresh Claude Code session must show that a project-local `@AGENTS.md` loads AGENTS.md. The global import is not taken as proof. A nested package with its own AGENTS.md gets the same one-line CLAUDE.md beside it. [adj 7]
- R3: each document has one responsibility. Rule-maker holds one short table of what belongs where, not a fixed heading set.
- R4: every document the agent needs is reachable from AGENTS.md, directly or through shallow nested indexes. Links resolve. [adj 1]
- R5: each workflow phase handles documentation incrementally. Clarify finds the documents relevant to the task and notes suspected staleness. Specify puts needed document changes into tickets. Execute updates documents with the code. Verification runs the script on the changed files and checks the affected claims. Delivery reports document changes and discrepancies. A full audit runs only when asked.
- R6: validation is meaningful, not only a link check. Deterministic checks cover links, named paths, named commands in the project's manifests, and named versions (the existing version_facts.py). The agent then checks each affected code-related claim against implementation evidence (source, configuration, tests). The report lists every affected claim as verified (with its evidence), contradicted, or not verified (with the reason). When code and document disagree, the agent determines which is wrong, and reports it when it cannot decide safely. Non-code claims are checked against their own evidence, or marked not verifiable. [owner's important requirement]
- R7: two documentation conditions block: a broken link to a document marked required (the existing required-read marker), and a contradiction the agent judges unsafe to build on, which stops the task and goes to the owner. They add to all existing approval gates, safety hooks and blocking protections, which all stay. [adj 3]
- R8: rule-maker has three operations: audit (read-only, writes a proposal), apply (only an approved proposal), check (the script). It works for new and existing projects and never rewrites a project without approval.
- R9: user-facing changes carry a short purpose statement (who, situation, goal, what must stand out) taken from CONTEXT.md and the code. When missing intent would change the result, the agent asks. It never invents product intent.
- R10: one vocabulary in a CONTEXT.md at the root of this repository, American spelling in prose, each rule stated once with references, repeated limit explanations consolidated, version history out of instructions. Identifiers and asserted phrases change together with their tests.
- R11: a lightweight route for genuinely small changes (text, order or visibility of existing elements on one screen, or a comparable change with no new element, data, interface or dependency). It keeps the owner's quoted yes, relevant tests and one review, drops the HTML report, the screen diagram and the delivery snapshot, and switches to the full route when scope or risk grows.
- R12: hook changes are built and tested in an isolated copy first: the small route, reading a phase skill file no longer enters the phase, the session check no longer matches the folder name, and records of a second task no longer stop edits of the first. The known approval-gate failures from earlier sessions, and the chained `git apply` that passed today without approval, are reproduced first. Every existing protection keeps its tests. [adj 3]
- R13: the session-start guard also names overlapping process plugins (superpowers) and explains which skill to use. It disables nothing.
- R14: word budgets for reference files, a duplication check in the package validator, and obsolete root documents moved to docs/archive after a reference check.
- R15: questions follow the new rule: research first, plain engineering choices become stated assumptions, only consequential choices are asked, grouped, with a recommendation.
- R16: adversarial tests: missing documentation, stale documentation, conflicting instructions, broken references, interrupted sessions, resumed tasks, incorrect approval states, and attempts to bypass hooks. [adj 6]
- R17: verification order: deterministic tests first, then at most 5 fresh headless Claude sessions in disposable projects with a total budget of 5 US dollars, then the manual host-specific checks. Paid runs start only if the budget is enforced as the plan states. Otherwise the agent asks before any cost. [adj 5]
- R18: the real-repository trial is read-only. No repository is modified without approval. [adj 8]

### What happens for each actor
- A developer opening a configured repository sees a short AGENTS.md: rules, commands and a document index with "read when" lines, with subordinate indexes where the project has them.
- An agent on a task reads AGENTS.md, then only the documents that the task or its changed files relate to. It updates them with the code. The check at the end reports broken links and paths, and the agent's claim review reports what was verified and what was not.
- The owner gets documentation discrepancies in the delivery report, sorted by severity, and is asked only when a contradiction makes building unsafe.
- Failures: a missing or broken index is reported by the script and in readiness. A stale hint is reported. A repository without AGENTS.md gets an audit proposal. No repository is changed without approval. A paid run that cannot be capped does not start.

### What stays the same
- All existing approval gates, safety hooks and blocking protections, and the duplicate guard with its repairs. [adj 3]
- The shared standards library and its global imports.
- Vendored upstream text, byte for byte.
- The owner's report patch in skills/codebase-map.
- Valid existing project rules keep passing.

### Not included
- Rewriting any project repository.
- A documentation generator, a generated manifest, or a hand-kept file-by-file mapping.
- Automatic plugin disabling.
- An ADR, unless the plan finds a lasting trade-off that DECISIONS.md does not already document. [adj 9]

### Acceptance
- A1: the script reports, on fixtures, a missing AGENTS.md, a broken link, an unreachable document, an index cycle, too deep nesting, a stale hint, a named path or command that does not exist, an oversized AGENTS.md and duplicated text. Each has a negative test that proves detection.
- A2: on a fixture task, the script lists the documents related to the changed files through links, folders and hints.
- A3: isolated fixture repositories cover missing docs, nested docs, stale references, conflicting rules, renamed files, a monorepo, several instruction files and undocumented code.
- A4: the claim review on a fixture with a wrong documented command, a wrong documented module path and a wrong documented behavior lists each as contradicted with its evidence, and lists a business claim as not verifiable.
- A5: a fresh Claude Code session in a disposable project shows that a one-line `@AGENTS.md` CLAUDE.md loads the AGENTS.md content.
- A6: each hook change has a test that fails before it. All existing hook tests still pass. The earlier gate failures and today's chained `git apply` are reproduced and retested.
- A7: adversarial tests for interrupted sessions, resumed tasks, incorrect approval states and bypass attempts exist and pass.
- A8: the package validator enforces the reference-file budgets and the duplication check. The full suite gives the baseline result plus the new tests, with baseline failures named separately from new ones.
- A9: the phase skills and rule-maker stay within their word budgets, and a check lists remaining synonyms of the CONTEXT.md terms.
- A10: the read-only audit runs on each accessible repository and writes a proposal: current problems, proposed AGENTS.md and indexes, migration risks, and auto-loaded words before and after. Unreadable repositories are listed as not tested.
- A11: at most 5 headless runs with the documented cap show the documentation step in the phases on a disposable project. The total spend stays within 5 US dollars. Results are reported as observations of those runs only.

### Assumptions the owner can reject
- Audit proposals for the real repositories are written under .artifacts in this repository, which Git ignores, because they quote private project content.
- Accessible repositories with instruction files: AXA-Retail, Cheflabels-labeler-V2, Hooqd, Pletrix-Cheflabels, Pluryn, Racing-Edge-Web, Tippaa, android-launcher, bare-skin, workflow-axa, workflow-paperclip.
- Codex is not installed in this shell, so Codex compatibility is checked against its documented AGENTS.md behavior only. Reported as a limit.
- The work runs in waves, with parallel workers only where files do not overlap. The language pass runs last.

## Approval
Approved 2026-11-11: plan r1, report reviews/plan-r1.html, the owner's answer "go" (D35), together with agreement 3 below. Tickets: all of TODO.md. Paid runs (V2) still need the owner's confirmation of the budget before the first paid call.


## Agreement 3 (proposed with the plan, agreed 2026-11-11 with "go", D35)
The plan review found four requirements without an acceptance item. Agreement 3 adds them. Everything else in agreement 2 stands.
- A12 (R13): with superpowers enabled in a temporary settings file, the session-start note names the overlapping skills and says which to use. Without it, nothing is added. Nothing is disabled.
- A13 (R9): a fresh subagent given a fixture UI request and the fixture's CONTEXT.md writes a purpose statement from it, chooses the element by its job and records why. With the user description removed from CONTEXT.md, it asks instead of inventing.
- A14 (R15): a fresh subagent given a fixture request with three plain engineering choices and one product choice states the three as assumptions and asks only the product choice, with a recommendation.
- A15 (R11): the gate allows writes to the files of a small change after the quoted yes, and refuses a file not listed and a new file. A capped run shows the route end to end.

## Outcome

Delivered 2026-11-11 as **partial**: everything was built, reviewed and tested offline; some acceptance items were shown only partly in live sessions, and a few agreement wordings need the owner's ruling. Reconciliation by a fresh subagent that built none of the work: `.artifacts/2026-11-11-consistency-review-findings/delivery-reconciliation.md` (requirement verdicts, checks, file map, reviews, records, change table). Verdicts below update it with the reruns V41-V43 and the final review.

**Asked, agreed and built.** The owner's five points (one language, simpler report input, purpose awareness in UI work, a consistent rule-maker, lighter rules), with Agreement 2 (D24-D34) and Agreement 3 (A12-A15), implemented under plan r1 ("go", D35). Built: the gate repairs and the small change route (H1-H6, E41, later SP2/SP4/SP8, the two V2 gate fixes), docs_check and the rule-maker redesign (D1-D3 and the V1-driven repairs), the documentation step, purpose statement and questioning rules in the phases (W1a-W1c), the validator, glossary and wording passes (L1, L3, L4, T2a1-T2d, T3), release 2.8.0-rc.36 with rules 1.8.6 (X1), 11 read-only audits (V1) and 5 capped live sessions (V2).

**Tickets.** Verified: H1-H6, D1-D3, W1a, W1b, L1, L3, L4, T2a1-T2d, T3, X1, V1. Verification pending: W1c (A14 partial), V2 (live results limited).

**Checks.** Final state (frozen in delivery-state.txt, then the R10 spelling fix): full suite 1219 tests OK, 14 skipped (V41, and again in the final review after the last edit); validate.py PASS with synonyms and repeated paragraphs failing; rules manifest current, rules_version 1.8.6. Fresh-agent acceptance runs on the final files: A4 passed (V42), A13 passed (V43), A14 partial (V33). Live sessions (V2, 9 calls, 2.6431 USD estimated): A5 passed, A11 resume case passed, A4 live partial, A15 end to end and R7 not shown.

**Reviews.** Every ticket had an independent two-axis review, plus the whole-feature review and its re-reviews, the V1-driven repair reviews, and a final review on the final files covering L4, the CHANGELOG, the coordinator-only wording repairs and a whole-feature delta (no finding above Low).

**Acceptance verdicts.** Verified: R3, R4, R9, R13, R14, R16, R18; A1, A2, A3, A4 (fixture), A5, A7, A8, A9, A10, A12, A13. Partial: R1, R2, R5, R6, R7, R8, R10, R11, R12, R15, R17; A6, A11, A14, A15. None failed, waived or superseded. Reasons per item in the reconciliation; R10 is partial only for British prose left in skills/codebase-map/examples/ui-review.

**For the owner to rule on.** R12: the H2 decision keeps the write gate turning on when a phase skill is read whole (narrower than R12's words). A14: the agent also asks a visible-change question (accept, or rerun with a request that names the link). A6: one hook message wording change had no failing test first. A15 end to end and R7 live: a rerun needs new paid calls. Whether a plain prompt must start the workflow (it did not in V2). The 14 `by: agent` entries in DECISIONS.

**Limits.** Human checks not run (the guard messages live; a refused agent-made Skill call). Codex not tested. New sessions load an installed rc.35 copy of the plugin until the owner updates it; the ~/.agents shared-rules copy also differs, so the duplicate guard warns at each start until updated. The audit proposals are not applied (three repositories load no project rules in Claude Code; nine have data-writing commands that need the owner's OK). Pre-existing: `git tag`, `git add`, `git branch <name>` not gated; README and EVALUATION name tools that never existed; test_record_safety intermittent under load. Low findings left from the final review: the gate's small-route branch when an Approval line names a missing report file, openai.yaml "approve the plan report" wording, VISUAL-REVIEW:17 two senses of "small", the TASK-FOLDER Approval placeholder lacks the small-change form, AUDIT.md item 6 on files loaded on demand, the validate.py repeat_notes docstring, CONTEXT.md "Small change" omits the description binding, deliver's commit rule now comes from the router's "unasked".

**Kept evidence.** FINDINGS V1-V43 and V-E41; `.artifacts/2026-11-11-consistency-review-findings/`: delivery-reconciliation.md, delivery-state.txt, delivery-suite.txt, audits/ (private content), runs/LEDGER.md and the run JSON, the gate diffs, a4-final.md, a13-final/, a14/. Disposable once the owner accepts: candidate/, t2/, claimfix/, the older suite outputs (h1, h6, t3, x1, final-suite), the runs/ fixture trees. Nothing staged, committed or pushed by this task.

**Delivery snapshot.** docs/plans/2026-11-11-consistency-review-findings/reviews/delivery-2026-11-11.html (V44).

**Next safe action.** The owner reviews this delivery and rules on the items above; then updates the installed plugin from this checkout to test rc.36 live; commit and publish only when the owner asks.

## Agreement 4 (proposed 2026-11-11 with plan revision r2, not yet agreed)
After delivery the owner asked to "do for all the repos the rule check and improving their agents.md by running the skill do not commit or push" and chose "Full proposals" (D44). Agreement 2 listed rewriting repositories as not included; this revision changes that item only. Everything else in agreements 2 and 3 stands.
- R19 (D44, D48): the reviewed audit proposals are applied in full through rule-maker's apply operation, with no commit, push or project command; open owner questions are listed, not decided. The ten other repositories were done under D44; this repository's own proposal needs this revision because its files are outside plan r1's approved file list.
- A16 (R19): in workflow-axa, CLAUDE.md is the one line `@AGENTS.md`, AGENTS.md carries the proposal's rules, boundaries, commands and index, the documents no longer name tools that never existed, the release ZIP ships the documents README links, and the three old evaluation records live under docs/archive/; validate.py, the full suite and docs_check pass, and nothing is committed or pushed.

## Plan revision r3 (approved 2026-11-11, no report)
The owner asked (2026-11-11): "design.md is lowercase should be capitalized. Always capitalized 1 word like DESIGN.md should be capitalized fix everywhere" and chose "Every one-word .md name" (D52). Agreements 2, 3 and 4 stand; r3 adds:
- R20 (D52): every one-word Markdown document name is written in capitals. In workflow-axa this covers the 20 modules in skills/rule-maker/rules/ (angular, capacitor, compatibility, design, ionic, laravel, lifetimes, operations, performance, php, pixijs, react, reliability, rust, security, testing, threejs, typescript, unity, vite). Not included: vendored skills/tdd files (upstream names, VENDORED-SKILLS.md), test fixtures (they imitate real projects), and history under docs/plans and docs/archive.
- A17 (R20): the renamed files are recorded by `git mv`; no live reference to a lowercase module name remains outside the exclusions; rule-maker DOCS.md states the naming rule; rules version 1.8.7 with manifest regenerated; validate.py, the full suite and docs_check pass.
- Ticket Y2 (Supports R20, A17): files: skills/rule-maker/rules/* (rename and links), every live file referencing them (skills/, hooks/, tools/, tests/, README.md, CONTEXT.md, AGENTS.md, docs/ARCHITECTURE.md, docs/EVALUATION.md, CHANGELOG.md, UPGRADE.md), skills/rule-maker/DOCS.md, rules CHANGES.md and version.json, rules manifest. TDD: yes for the naming rule if docs_check enforces it, otherwise docs/config; check: validate.py, full suite, docs_check.
