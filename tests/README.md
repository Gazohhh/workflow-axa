# Local evaluation

## What is executable here

From the plugin root, run:

```powershell
python -X utf8 tools/validate.py
python -X utf8 -m unittest discover -s tests -p "test_*.py" -v
```

Python 3.10+ and Git are enough for the original/core tests; optional image-comparison tests skip when Pillow is unavailable; no package installation, API account or network is needed. The first command checks this repository's deliberately small metadata format, registration (the skills plugin.json lists), relative links, repeated paragraphs and the documented counts and versions; word ceilings and CONTEXT.md synonyms are advisory NOTE lines. It is not a general YAML/schema validator. `test_package_contract.py` lists the essential skills, hook registrations, LICENSE folders, renderer assets and key tests independently of the manifests, so a deletion that also edits a manifest still fails; a ticket that adds or removes one of them updates that list. The unit tests check those diagnostics, fixture isolation, all fixture variants, clean/failing baselines, synthetic mixed staging, and the read-only specialist checker. Checker tests cover complete/missing/duplicate/policy-mismatched skills, support files, baseline changes, and honest runtime-status reporting.

These are **package/tooling tests, not agent behavioral tests**. They cannot prove documentation-before-code ordering, question quality, approval compliance, code quality, or recovery. Those require actual host runs and inspection of their traces/files. See [SCENARIOS.md](SCENARIOS.md).

## Create an isolated scenario

```powershell
python -X utf8 tools/create_fixture.py --output "C:\Dev\workflow-case-01" --scenario clean
```

Use a fresh destination for each run. Available variants: `clean`, `approved`, `interrupted`, `mixed`, `owned`, `secret`, `baseline-failure`, `decision-gap`, `related-task`, `multiple-tasks`, `completed-task`, `answered-task`. The generator creates a local baseline commit inside the new synthetic repository and no remote; it refuses existing paths, paths inside this package and paths beneath another `.git` directory/file. It does not reset or clean an existing project. A failed creation may leave a partial new fixture; inspect it before manually removing it.

`.fixture-state.json` records the starting commit, staged diff, unstaged diff and status. It is local evaluation metadata, not the agent's handoff record. Preserve it to compare later ownership/staging effects. The secret scenario contains an unmistakably fake credential, never a real one. The intentionally partial/failing scenarios are not expected to have complete behavior or green tests.

## Run a candidate and a baseline fairly

For the current candidate, prepare and run fresh sessions as [docs/EVALUATION.md](../docs/EVALUATION.md) describes. Historical, 2.8.0-rc.1 to rc.4 only: the baseline was the supplied **post-hardening 2.8.0-rc.1 archive**, identified in docs/archive/CANDIDATE-REVIEW.md, and runs followed docs/archive/CLAUDE-TEST-PROMPT.txt; neither is current test authority. Load only one version per fresh session; do not mix a global copy, repository skill and session plugin.

Generate two copies of the same scenario. Hold the host/model version, permissions, prompt, fixture and specialist installation
constant. For 2.3.0, complete SETUP.md and confirm the relevant specialists are enabled.
Dependency-failure scenarios deliberately vary only the named capability. Run the same staged user replies. Save observed paths/commands, traces, final files and actual results in a private location outside the package or `.artifacts/`. Sanitize before sharing. Record model, host version, scenario, package version/hash, repetition, question rounds, authority violations, record ordering, recovery outcome, cleanup, and evidence freshness. Token/cost/runtime measurements are observations, not guessed scores.

Repeat critical scenarios and inspect errors such as usage exhaustion separately from behavior failures. A correct pause awaiting a required decision counts as success. Refusing to continue an already approved ordinary step does not. Do not substitute "the agent said it passed" for inspecting the code, documents and trace.

## Abrupt interruption test

Run a real task and terminate the host during discovery or implementation **without asking for a handoff first**. Keep its actual worktree. Start a fresh session/account with only the task-folder location and an explicit statement that the old session stopped. Confirm the new session reads and reconciles records before coding, identifies partial work, reuses scope approval and obtains fresh verification.

The `interrupted` fixture makes this scenario repeatable but does not replace a real hard-stop run. For another machine/cloud environment, transfer the actual working edits and records through an authorized method; a folder of plans alone cannot resume missing code.

## Optional Claude-native automation

On an installed CLI that supports it, inspect help and initialize a native suite in a separate candidate checkout:

```powershell
claude plugin eval --help
claude plugin eval init
claude plugin eval . --no-publish
```

The initialization is interactive and model-assisted; native runs consume account usage. Agree a budget before running them. Use the installed help to configure tools, model, run count and cost ceiling; grant only fixture access. Do not bypass host permission checks. `--no-publish` keeps the eval report local, not the model inference itself offline. Native cases and Anthropic skill-creator suites use different formats; this package does not mislabel its manual scenarios as either format. [Native eval documentation](https://code.claude.com/docs/en/plugin-evals)

Native with/without-plugin scores do not directly compare the old and new workflow versions. Run each version with the same suite and compare the corresponding plugin-enabled traces/results. Multi-turn approval and cross-session resumption still need staged or interactive tests, not a single final-response rubric.

## Rollout gate

Resolve unauthorized changes, unsafe staging, leaked evidence or false completion before piloting; high-risk failures are not averaged away by a good mean score. Review code simplicity with a human. Add a targeted regression case for each actual failure, then change the smallest relevant instruction rather than adding another generic warning.

Pilot with another teammate on the actual hosts and a cold handoff. Keep a working previous copy and record which version each pilot used. The candidate package version is 2.9.0-rc.2; publishing/tagging/pushing remains a human action, not a side effect of tests. The absence of live model results in this ZIP is stated in [VALIDATION.md](../VALIDATION.md).


## Retained visual and activation checks

The stdlib suite also tests report modes, requirement/evidence/task references, pending-decision and approval-state validation, escaped labels, source drift, paths, CLI behavior and overwrite refusal. These assertions do **not** prove semantic correspondence to code or authentic approval.

Before live tests merge the reviewed project routing block into the disposable project's applicable host instructions. Install the complete registered skill set of the version under test; the manifest is authoritative. Bundled specialists stay with the package; do not install duplicates. Do not install an external diagram skill for these tests. Add the plain-prompt cases at the end of SCENARIOS.md; do not prepend a skill command to those prompts. Inspect actual skill-load and code-read traces. Test inspection-only and conceptual negative cases separately.

An optional browser smoke runner uses already installed Python Playwright and a supplied Chromium executable:

```powershell
python -X utf8 tools/browser_smoke.py --browser "C:\Path\To\Chromium\chrome.exe" --output "C:\Dev\workflow-browser-results"
```

This does not install dependencies. Browser sandboxing remains enabled by default; an explicit `--no-sandbox` switch is available only for a trusted disposable container that requires it, not normal desktop use. It opens a fresh headless browser context offline and first attempts direct local-file navigation. If managed policy blocks it, the identical HTML is tested in a new content context and that limit is recorded. Checks cover default flow, node/diamond text fit, view selection, readable size, mobile entry centering, native scrolling/zoom/Fit, keyboard/mouse controls, evidence anchors, no-JavaScript navigation, inert malicious text and absence of approval controls/network requests. It can save screenshots and JSON results in a new directory. Desktop default-browser behavior still requires a separate manual check; managed browser policies may prohibit them. The actual renderer still produces a standalone file and needs no web server.

## Flowchart-specific regressions

`test_flowcharts.py` exercises schema-2 geometry, labelled decision exits, distinct
ports, crossing routes, label masks, overflow budgets, source/task traceability,
delivery-order agreement, source uncertainty disclosure and native start links.
Schema-1 HTML remains freshness-checkable; new schema-1 renders fail with migration
guidance. The renderer never infers feature flow from old row/column positions.

The approved visual direction is implemented in the local assets and documented in
`skills/codebase-map/FLOWCHART-DESIGN.md`. For live evaluation leave external diagram skills unavailable. Verify codebase-map
reads its bundled flowchart guide, uses the existing approved style, preserves grilling and
stops at approval. Do not grade a card layout or generic research/plan/code chart as a
passing feature flow. See E32–E37 in SCENARIOS.md.


## New in 2.3.0

[Live-host decision/task-reuse cases](behavioral/README.md) cover overlooked decisions, complete requests, partial answers, recommendation consent, related/ambiguous/completed task discovery, no-file explanations, interrupted work and missing grilling. Their JSON is evaluator-only; do not paste expected outcomes into agent prompts. No live model run is asserted by validating that JSON or constructing fixtures.

[Visual regression instructions](VISUAL-REGRESSION.md) describe read-only captures and exact screenshot comparisons. The original browser smoke suite remains for geometry, semantics represented by fixtures and interaction checks. Screenshot references preserve prior styling; they are not proof of pixel perfection on other devices. No new dependency is installed by either tool.

## Global policy setup and retention checks (2.5.0)

`test_global_policy.py` uses disposable user homes to test preview/check no-write behavior, idempotent merges, override selection, CRLF/BOM preservation, custom profiles, modified policy refusal, symlink/junction boundary checks, hardlinks, concurrent edits and untouched project artifacts. The helper is not a filesystem cleaner. Linux filesystem checks are not evidence of Windows junction or native ACL behavior; test the actual target environment before deployment.

B15–B29 in the live-host suite (B25–B28: the offer model's minimal offer, one-ticket offer, report only on html-first, and deliver's `unknown`; B29: a fully specified one-ticket request still gets its offer through workflow-specify, found by T26 live run r20) cover policy loading outside workflow, safe reruns/concurrency, required captures, producer retention limits, ownership and delivery preservation. They are authored but NOT RUN. Existing browser output directories remain isolated for safety: use an owned child under one task parent, retain necessary proof, and clean eligible temporary captures after inspection instead of creating an unrelated root each time.

## Record history and backward compatibility (2.6.0)

`test_record_context.py` checks additive schema-2 fields, distinct progress states, no approval-request bypass, original-file preservation, exact aliases, missing historical review descriptions, owner-removed outcomes, escaped input and legacy fixtures. It checks the data/renderer and instruction contracts, not whether a host model follows them. H01–H07 in behavioral/cases.json exercise actual-agent record handling; they remain NOT_RUN until observed.

The old pending example and historic task records are intentionally unchanged. The new task-overview example uses the same graph geometry with an optional sourced checkpoint/revision log. Inspect both desktop and mobile, the closed/open history disclosure and source links. Do not refresh approved visual baselines merely because a status section was added.


## Offer model and package redesign (2.9.0-rc.1)

New test files: `test_approval_hook.py` (the offer checker), `test_offers.py`, `test_settings.py`, `test_shadow_comparison.py`, `test_session_failures.py`, `test_required_reads.py`, `test_flows.py`, `test_rules_pass.py`, `test_package_contract.py`, `test_completion_check.py` (`completion_check.py` baseline, snapshot and check), `test_cutover.py` (no stale text, the registered hook, the legacy route, rollback to rc.39, and `ReleaseNotes`: the current CHANGELOG entry names the removed hooks and the three new skills), `test_new_skills.py`, `test_interrogate_snapshot.py` and `test_stage_candidate.py`. `test_plain_reply_hook.py`, `test_phase_reads_hook.py` and `test_truncated_read_hook.py` are removed with their hooks; docs/RULE-CONTRACTS.md "Removed with their hooks" maps their checks.

One limit was loosened on purpose: `test_engineering_rules.py` lets CORE.md grow from 650 to 710 words, because T11 added the required comment rules (CORE went from 649 to 702 words). Version pins were retargeted for the release: `rules_version` 1.8.8 → 1.9.0 in `test_rules.py` and `test_engineering_rules.py`; the `candidate_version` of the four live-case files under `behavioral/` 2.8.0-rc.39 → 2.9.0-rc.1 (the tests compare it with plugin.json). `test_global_policy.py` reads the policy revision from `global_policy.py`, now 2.9.0.

Known intermittent failure: `test_record_safety.test_parallel_appends_lose_nothing` sometimes leaves `FINDINGS.md.lock` after eight parallel `record.py` appends (about 1 run in 30). It fails the same way on rc.39. Rerun once only when the failure is that test with `['FINDINGS.md.lock'] != []`, and report both runs; never skip it.

## Workflow redesign (2.9.0 candidate)

Task `docs/plans/2026-11-15-workflow-redesign`. `test_session_failures.py` replays the owner's session failures (report waiver, unnumbered plan, task switch on a commit, small changes across sessions and with a new test file) with a guard test per relief. `test_required_reads.py` covers the one required-read parser and `paths=` scoping. `test_flows.py` checks the recipe index (`skills/workflow/flows/`): rows and files match, frontmatter, registered `uses`, and the labelled prompts and behavioural cases in `behavioral/flows.json`, which are observed host runs (NOT_RUN until run). `test_package_contract.py` is the independent package list. `test_docs_consistency.py` covers `verification_summary.py` exit status, tree identity and `--check`. `test_settings.py` covers the machine CSS switch, `test_offers.py` the offer record and `test_approval_hook.py` the offer checker (presentation, answers, history across sessions, CSS, settings). `test_shadow_comparison.py` runs each scenario through both the offer checker and phase_gate and compares the outcomes with its expected table; every difference is classified (`SHADOW_PRINT=1` prints the pairs).

## Bold approvals and one-run validation (2.8.0-rc.39)

`test_gate_regressions.EmphasisedAnswers` checks that a typed answer in bold or italics matches its quote, that other words still do not, and that the install check still reads the plain words. `test_docs_consistency.test_one_run_brings_validation_to_a_new_version` runs `tools/verification_summary.py` on a stand-in project whose validator fails while VALIDATION.md names the old version.

## Approval gate checks (2.8.0-rc.38)

`test_gate_notes.py` (`StyleNotes`) feeds `hooks/phase_gate.py` a PostToolUse event and checks the styling and small-change notes: a note when an edit adds a style cue or stylesheet rule to an application file, none for Markdown, test files or unchanged styles, and a timing case for very long texts. New classes in `test_gate_regressions.py`: `CheckpointHeadingRegressions` (any "Current checkpoint" heading), `AgreementGateRegressions` (writes wait for the Agreement line on two-gate tasks), `BulkArtifactDeletes` (`git clean` and bulk deletes of `.artifacts`, also inside `bash -c` and `powershell -Command`) and `LinkedWorktreeCopies` (the refusal names a differing PLAN copy). `AltinstarRegressions` gains two pins: requirement IDs such as "D4-R6" are not revisions, and a report named only in an answered approval question counts as presented. The `task` helper in `test_phase_gate_hook.py` adds a default `Agreement (gate one): agreed` line to a two-gate task without one. These tests use synthetic transcripts. They do not show how a live host records a session.

## Blast radius and the Unslop check (task 2026-11-17-pstack-blast-radius-unslop)

`test_new_skills.py` checks code-review step 4b and `skills/code-review/BLAST-RADIUS.md` (`BlastRadiusMethod`: every part of the method, no multi-model step, no source name, the full MIT licence text) and every planning and routing point (`BlastRadiusRouting`). Its `pointer_targets` resolves each code-form pointer to `skills/code-review/BLAST-RADIUS.md` from the folder of the file that holds it, because `tools/validate.py` checks Markdown links only. `test_flows.py` checks that every recipe except new-project names the method at its step, and that the `blast_radius_cases` in `behavioral/flows.json` are live-host NOT_RUN. `test_simple_english.py` checks the Unslop tells (numbered, overlaps that only name their rule, Unslop 24 not adopted), the WRITING.md Unslop section before the cold-reader check, the pointers from deliver, specify, code-review, docs-tests and writing-for-agents, `UNSLOP.LICENSE`, and case B30 in `behavioral/cases.json`. `test_owned_skills.py` adds the new source names to the no-source rule and checks that the credits name both licence files without adding a credited skill. These checks prove the text says it, not that an agent follows it. B30 and the BR-* cases stay NOT_RUN until an observed host run.

## User commands: interrogate, no-comments, wait-what (2.9.0)

`test_new_skills.py` checks that the three are registered and user-only (in both `SKILL.md` and `agents/openai.yaml`), each contract of REDESIGN §3.8–3.10, code-review's comment, reader-load and blast-radius checks, links that stay inside each skill folder, and no repeated paragraph with CORE. `test_interrogate_snapshot.py` runs `skills/interrogate/scripts/snapshot.py` on temporary Git repositories: a stable id that covers edits, deletions and untracked files; a copy that is byte-equal under `core.autocrlf=true` and leaves the target's `.git` untouched; `fill` of an existing host checkout and its refusals; a link or junction in the checkout replaced, never followed (an outside sentinel stays untouched); the stale check. The phrase checks prove the text says it, not that an agent follows it. That needs an observed run (FINDINGS, T23).

## /spar (2.9.0-rc.3 candidate)

`test_spar.py` checks that `/spar` is registered and user-only, that the workflow names it without running it, and that the skill text (SKILL.md, T3.md, SPAR-FILE.md) states each rule of agreement 6 (docs/plans/2026-11-17-spar-skill, R31-R40: rebuilt around SPAR.md). `tests/behavioral/spar.json` holds its live process scenarios: each stages a situation (a real idea, a direction-changing owner question, a labelled synthesis, a spent budget, one model only, cancel, the handoff, the SPAR.md structure) and lists the process to observe, never a prescribed answer; results from earlier designs are kept under `history`. They run only live; until then they stay `NOT_RUN`, and a recorded result names its evidence and the candidate it ran on. `test_settings.py` covers the default depth.

## Owned skills (2.8.0-rc.37)

`test_owned_skills.py` checks that each formerly copied skill that still ships is registered and keeps its `LICENSE`, that the archived ones (implement-spec, retro, simple-english) are unregistered with their licences in place, that the phase skills load their sibling skills, and that no file under `skills/` names where a skill came from. It also covers `tools/digest_sessions.py` (formerly retro's script). The pattern list of source names sits in the test; a mention in a form the list does not cover passes unnoticed.

## Rules readiness (2.7 candidate)

`test_rules.py` validates the declared gate states, bounded exceptions, setup-only consent, stale inputs, root/scope/host/branch changes, missing/corrupt modules, no-write inspection and global reference merges. These checks are not model behavioural results or a permission system. The candidate adds one central library and no per-project copy.

Use [the 40-case matrix](behavioral/RULES-READINESS.md) for actual host runs. Keep its expectations outside the agent context. All results remain NOT_RUN until execution is observed. Preserve valid old rules, approval/history, test artifacts and the separately maintained global artifact policy.

## Engineering rules and version facts (2.7.0-rc.3)

The new `test_version_facts.py` exercises real read-only file inspection, scoped lock observations, version ambiguity, unsafe inputs and no project execution. `test_engineering_rules.py` checks library routing/content contracts and additional version-input freshness. Content assertions are not model-behaviour evidence.

[Engineering scenarios](behavioral/engineering-rules.json) add thirty baseline/candidate cases. They remain NOT_RUN until actual host executions are reviewed. Do not feed expected outcomes to the agent. Verify that selected guidance changes the result without gratuitous questions, new reports, wrappers or unrelated cleanup.

## UI-design integration

Install all local skills of the version under test (all 21 registered in the package manifest), then run the [UI acceptance cases](behavioral/UI-DESIGN.md) using [their scenario data](behavioral/ui-design.json). They are NOT RUN until observed in actual hosts. `test_ui_design.py` covers read-only diff parsing, styling and markup cues, malformed/partial inputs, legitimate semantic changes, no-write/no-approval behaviour and local route contracts. These mechanical assertions do not prove a model follows the policy.

## Rules audit and design kit

Read [RULES-AUDIT-KIT.md](behavioral/RULES-AUDIT-KIT.md) for the new live-host cases. The installation/catalogue tests operate on temporary synthetic files. They establish parsing, scope/freshness, readonly and error behaviour, not actual designer acceptance, successful host loading or completeness of an application audit.

## rc.6 additive screen-flow testing

`test_screen_flow.py` covers optional schema validation, approval/source distinctions, screenshot inputs, inert text, preserved full-report sections, extra-file auditing and policy integration. `tools/ui_browser_smoke.py` exercises the actual view in an offline browser. Neither substitutes for a live Claude/Codex acceptance test or real project-kit signoff.

Live UI report cases: [UI-SCREEN-FLOW.md](behavioral/UI-SCREEN-FLOW.md). These fourteen cases are authored acceptance scenarios, not executed model tests.

## rc.7 strict kit reuse

`test_strict_kit.py` covers exact item/variant/state/composition references, changed/deleted sources, scope, stale capture inputs, legacy-mode rejection, preserved report assets and snapshot history. `test_kit_index.py` checks the optional read-only local index adapter. `tools/kit_browser_smoke.py` checks real renderer output and element links using synthetic source/capture fixtures, not a real project kit. The strict live-host matrix is [STRICT-KIT.md](behavioral/STRICT-KIT.md); all 26 cases are NOT RUN. Old live UI case expectations that permitted raw markup/design-authoring have been deliberately superseded; no agent runs are invented.

## Modular phases and central report (2.8.0-rc.1)

`test_task_report.py` exercises the optional `task_report` content through the renderer's public interface: sourced sections, per-ticket specifications, agreement authority kept separate from implementation approval, check and acceptance-result consistency, unknown keys in the new objects, escaping, partial delivery, and no new sections for inputs without the object. The validator now requires the twelve registered skills and their word budgets. These checks cover the renderer and package structure, not whether an agent follows the phase skills.

Agent behavior for the four phase skills needs actual sessions: a request with a missing requirement reaching clarify, each phase skill invoked directly without its prerequisite, separate gate-one and gate-two responses including a refusal and a scope change, a dependent multi-ticket execution with ticket and whole-feature reviews, an interruption between gates, a missing specialist, and a delivery with an unverified item. Compare with the `9daf507` baseline on the same prompts. Record which skill copies actually loaded. Results are recorded in [VALIDATION.md](../VALIDATION.md) once observed; until then they are NOT RUN.
