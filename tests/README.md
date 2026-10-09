# Local evaluation

## What is executable here

From the plugin root, run:

```powershell
python -X utf8 tools/validate.py
python -X utf8 -m unittest discover -s tests -p "test_*.py" -v
```

Python 3.10+ and Git are enough; no package installation, API account or network is needed. The first command checks this repository's deliberately small metadata format, registration, relative links and core word budget. It is not a general YAML/schema validator. The unit tests check those diagnostics, fixture isolation, all fixture variants, clean/failing baselines, synthetic mixed staging, and the read-only specialist checker. Checker tests cover complete/missing/duplicate/policy-mismatched skills, support files, baseline changes, and honest runtime-status reporting.

These are **package/tooling tests, not agent behavioral tests**. They cannot prove documentation-before-code ordering, question quality, approval compliance, code quality, or recovery. Those require actual host runs and inspection of their traces/files. See [SCENARIOS.md](SCENARIOS.md).

## Create an isolated scenario

```powershell
python -X utf8 tools/create_fixture.py --output "C:\Dev\workflow-case-01" --scenario clean
```

Use a fresh destination for each run. Available variants: `clean`, `approved`, `interrupted`, `mixed`, `owned`, `secret`, `baseline-failure`. The generator creates a local baseline commit inside the new synthetic repository and no remote; it refuses existing paths, paths inside this package and paths beneath another `.git` directory/file. It does not reset or clean an existing project. A failed creation may leave a partial new fixture; inspect it before manually removing it.

`.fixture-state.json` records the starting commit, staged diff, unstaged diff and status. It is local evaluation metadata, not the agent's handoff record. Preserve it to compare later ownership/staging effects. The secret scenario contains an unmistakably fake credential, never a real one. The intentionally partial/failing scenarios are not expected to have complete behavior or green tests.

## Run the current skill and candidate fairly

Keep the original uploaded package as the baseline; exclude its embedded `.git` when preparing a test copy. Load only one workflow version per fresh host session. Do not mix a global installation, a repository skill and a session plugin unintentionally.

Generate two copies of the same scenario. Hold the host/model version, permissions, prompt, fixture and specialist installation
constant. For 2.0.0, complete SETUP.md and confirm the relevant specialists are enabled.
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

Pilot with another teammate on the actual hosts and a cold handoff. Keep a working previous copy and record which version each pilot used. The user-selected package version is 2.0.0; publishing/tagging/pushing remains a human action, not a side effect of tests. The absence of live model results in this ZIP is stated in [VALIDATION.md](../VALIDATION.md).
