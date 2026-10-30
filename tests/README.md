# Local evaluation

## What is executable here

From the plugin root, run:

```powershell
python -X utf8 tools/validate.py
python -X utf8 -m unittest discover -s tests -p "test_*.py" -v
```

Python 3.10+ and Git are enough for the original/core tests; optional image-comparison tests skip when Pillow is unavailable; no package installation, API account or network is needed. The first command checks this repository's deliberately small metadata format, registration, relative links and core word budget. It is not a general YAML/schema validator. The unit tests check those diagnostics, fixture isolation, all fixture variants, clean/failing baselines, synthetic mixed staging, and the read-only specialist checker. Checker tests cover complete/missing/duplicate/policy-mismatched skills, support files, baseline changes, and honest runtime-status reporting.

These are **package/tooling tests, not agent behavioral tests**. They cannot prove documentation-before-code ordering, question quality, approval compliance, code quality, or recovery. Those require actual host runs and inspection of their traces/files. See [SCENARIOS.md](SCENARIOS.md).

## Create an isolated scenario

```powershell
python -X utf8 tools/create_fixture.py --output "C:\Dev\workflow-case-01" --scenario clean
```

Use a fresh destination for each run. Available variants: `clean`, `approved`, `interrupted`, `mixed`, `owned`, `secret`, `baseline-failure`, `decision-gap`, `related-task`, `multiple-tasks`, `completed-task`, `answered-task`. The generator creates a local baseline commit inside the new synthetic repository and no remote; it refuses existing paths, paths inside this package and paths beneath another `.git` directory/file. It does not reset or clean an existing project. A failed creation may leave a partial new fixture; inspect it before manually removing it.

`.fixture-state.json` records the starting commit, staged diff, unstaged diff and status. It is local evaluation metadata, not the agent's handoff record. Preserve it to compare later ownership/staging effects. The secret scenario contains an unmistakably fake credential, never a real one. The intentionally partial/failing scenarios are not expected to have complete behavior or green tests.

## Run the current skill and candidate fairly

For this release use 2.7.0-rc.3 as the comparison baseline, not the original first workflow. Keep the baseline package unchanged. Load only one workflow version per fresh host session. Do not mix a global installation, a repository skill and a session plugin unintentionally.

Generate two copies of the same scenario. Hold the host/model version, permissions, prompt, fixture and specialist installation
constant. For 2.3.0, complete SETUP.md and confirm the relevant specialists are enabled.
Dependency-failure scenarios deliberately vary only the named capability. Inventory
fixtures in test_specialists.py are synthetic; they are not installed upstream skills. Run the same staged user replies. Save observed paths/commands, traces, final files and actual results in a private location outside the package or `.artifacts/`. Sanitize before sharing. Record model, host version, scenario, package version/hash, repetition, question rounds, authority violations, record ordering, recovery outcome, cleanup, and evidence freshness. Token/cost/runtime measurements are observations, not guessed scores.

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

Pilot with another teammate on the actual hosts and a cold handoff. Keep a working previous copy and record which version each pilot used. The candidate package version is 2.7.0-rc.6; publishing/tagging/pushing remains a human action, not a side effect of tests. The absence of live model results in this ZIP is stated in [VALIDATION.md](../VALIDATION.md).


## Retained visual and activation checks

The stdlib suite also tests report modes, requirement/evidence/task references, pending-decision and approval-state validation, escaped labels, source drift, paths, CLI behavior and overwrite refusal. These assertions do **not** prove semantic correspondence to code or authentic approval.

Before live tests merge the reviewed project routing block into the disposable project's applicable host instructions. Install all eight local skills plus the approved relevant Matt specialists. Do not install an external diagram skill for these tests. Add the plain-prompt cases at the end of SCENARIOS.md; do not prepend a skill command to those prompts. Inspect actual skill-load and code-read traces. Test inspection-only and conceptual negative cases separately.

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
`skills/codebase-map/FLOWCHART-DESIGN.md`. Synthetic specialist inventories test detection,
not actual upstream loading. For live evaluation leave external diagram skills unavailable. Verify codebase-map
reads its bundled flowchart guide, uses the existing approved style, preserves grilling and
stops at approval. Do not grade a card layout or generic research/plan/code chart as a
passing feature flow. See E32–E37 in SCENARIOS.md.


## New in 2.3.0

[Live-host decision/task-reuse cases](behavioral/README.md) cover overlooked decisions, complete requests, partial answers, recommendation consent, related/ambiguous/completed task discovery, no-file explanations, interrupted work and missing grilling. Their JSON is evaluator-only; do not paste expected outcomes into agent prompts. No live model run is asserted by validating that JSON or constructing fixtures.

[Visual regression instructions](VISUAL-REGRESSION.md) describe read-only captures and exact screenshot comparisons. The original browser smoke suite remains for geometry, semantics represented by fixtures and interaction checks. Screenshot references preserve prior styling; they are not proof of pixel perfection on other devices. No new dependency is installed by either tool.

## Global policy setup and retention checks (2.5.0)

`test_global_policy.py` uses disposable user homes to test preview/check no-write behavior, idempotent merges, override selection, CRLF/BOM preservation, custom profiles, modified policy refusal, symlink/junction boundary checks, hardlinks, concurrent edits and untouched project artifacts. The helper is not a filesystem cleaner. Linux filesystem checks are not evidence of Windows junction or native ACL behavior; test the actual target environment before deployment.

B15–B24 in the live-host suite cover policy loading outside workflow, safe reruns/concurrency, required captures, producer retention limits, ownership and delivery preservation. They are authored but NOT RUN. Existing browser output directories remain isolated for safety: use an owned child under one task parent, retain necessary proof, and clean eligible temporary captures after inspection instead of creating an unrelated root each time.

## Record history and backward compatibility (2.6.0)

`test_record_context.py` checks additive schema-2 fields, distinct progress states, no approval-request bypass, original-file preservation, exact aliases, missing historical review descriptions, owner-removed outcomes, escaped input and legacy fixtures. It checks the data/renderer and instruction contracts, not whether a host model follows them. H01–H07 in behavioral/cases.json exercise actual-agent record handling; they remain NOT_RUN until observed.

The old pending example and historic task records are intentionally unchanged. The new task-overview example uses the same graph geometry with an optional sourced checkpoint/revision log. Inspect both desktop and mobile, the closed/open history disclosure and source links. Do not refresh approved visual baselines merely because a status section was added.


## Rules readiness (2.7 candidate)

`test_rules.py` validates the declared gate states, bounded exceptions, setup-only consent, stale inputs, root/scope/host/branch changes, missing/corrupt modules, no-write inspection and global reference merges. These checks are not model behavioural results or a permission system. The candidate adds one central library and no per-project copy.

Use [the 40-case matrix](behavioral/RULES-READINESS.md) for actual host runs. Keep its expectations outside the agent context. All results remain NOT_RUN until execution is observed. Preserve valid old rules, approval/history, test artifacts and the separately maintained global artifact policy.

## Engineering rules and version facts (2.7.0-rc.3)

The new `test_version_facts.py` exercises real read-only file inspection, scoped lock observations, version ambiguity, unsafe inputs and no project execution. `test_engineering_rules.py` checks library routing/content contracts and additional version-input freshness. Content assertions are not model-behaviour evidence.

[Engineering scenarios](behavioral/engineering-rules.json) add thirty baseline/candidate cases. They remain NOT_RUN until actual host executions are reviewed. Do not feed expected outcomes to the agent. Verify that selected guidance changes the result without gratuitous questions, new reports, wrappers or unrelated cleanup.

## UI-design integration

Install all eight skills, then run the [UI acceptance cases](behavioral/UI-DESIGN.md) using [their scenario data](behavioral/ui-design.json). They are NOT RUN until observed in actual hosts. `test_ui_design.py` covers read-only diff parsing, styling and markup cues, malformed/partial inputs, legitimate semantic changes, no-write/no-approval behaviour and local route contracts. These mechanical assertions do not prove a model follows the policy.

## Rules audit and design kit

Read [RULES-AUDIT-KIT.md](behavioral/RULES-AUDIT-KIT.md) for the new live-host cases. The installation/catalogue tests operate on temporary synthetic files. They establish parsing, scope/freshness, readonly and error behaviour, not actual designer acceptance, successful host loading or completeness of an application audit.

## rc.6 additive screen-flow testing

`test_screen_flow.py` covers optional schema validation, approval/source distinctions, screenshot inputs, inert text, preserved full-report sections, extra-file auditing and policy integration. `tools/ui_browser_smoke.py` exercises the actual view in an offline browser. Neither substitutes for a live Claude/Codex acceptance test or real project-kit signoff.

Live UI report cases: [UI-SCREEN-FLOW.md](behavioral/UI-SCREEN-FLOW.md). These fourteen cases are authored acceptance scenarios, not executed model tests.
