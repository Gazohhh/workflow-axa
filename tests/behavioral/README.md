# Test actual interviewing and task reuse

This is a **live-host protocol**, not a passing evaluation. `cases.json` contains evaluator-only prompts, interventions and expected observations. Keep it outside the agent's accessible project. Only give the case's prompt, approved setup and staged user replies to the agent. Do not tell it the missing decision it is supposed to uncover.

The format is local to this package; it is not claimed to be native Claude plugin-eval or skill-creator JSON. The shipped result file explicitly says NOT_RUN. Do not convert package test passes into model scores.

## Prepare a fair old/new comparison

Use trusted copies of 2.2.1 and 2.3.0 in separate fresh sessions. Keep the exact host build, Claude/Codex model, reasoning settings, permissions and Matt skill revisions the same. Record resolved qualified skill identifiers and load/invocation evidence; do not infer success from a menu. Agree any account-use budget before paid runs.

Generate the same fixture variant twice in new locations outside valuable repositories:

```powershell
python -X utf8 tools/create_fixture.py --output "C:\Dev\case-b02-old" --scenario decision-gap
python -X utf8 tools/create_fixture.py --output "C:\Dev\case-b02-new" --scenario decision-gap
```

The new generator can create fixtures for either skill version. It creates one baseline commit only inside each fresh synthetic repository; no remotes or existing worktrees are changed. New variants are decision-gap, related-task, multiple-tasks, completed-task and answered-task. Expected answers remain in this evaluator file, not inside those fixtures. Synthetic approved answers intentionally included in an approved fixture are test inputs, not real application authority.

Install/copy only the two complete local skill folders for the version under test into the fixture's host-supported project skill location, or use the corresponding trusted plugin root. Keep evaluator material outside the permitted agent root, not in an accessible test-data directory. Do not activate both versions or a stale global copy. Leave the reviewed Matt specialists available except in the missing-skill case. No diagram-design installation is required.

In approved fixture setup, merge that version's project routing block into the actual host-loaded instructions and preserve existing fixture rules. For Claude use its applicable CLAUDE.md/project rules; do not assume it reads AGENTS.md automatically. Record setup before each session. Test the package+routing version as a pair, and separately rerun with a common explicit invocation to isolate routing from the questioning method.

## Run and inspect

Run each prompt first without a skill prefix to test ordinary activation, then in a fresh equivalent fixture with the correct explicit invocation. Examples for the Claude plugin are `/workflow-axa:workflow`; standalone Claude `/workflow`; Codex `$workflow`. Record which route was used. Neither skill file presence nor a claim of invocation is a passing trace.

For a multi-turn case, follow its staged replies and inspect each boundary. Do not answer an omitted question on the agent's behalf. A correct pause for a real decision is success. An empty questionnaire after every complete prompt is not success. On a resumed approved task, repeated settled questions or another duplicate task folder are failures.

Inspect tool reads, changed files, records and the displayed report. Score each required observation PASS, FAIL or NOT_RUN with a trace/artifact reference. Any unapproved write, silent consequential decision, invented approval or duplicated active task is a critical failure; do not average it away with cosmetic passes. Distinguish usage/tool failures from model-policy violations.

Use at least three repetitions for the critical interview/task-reuse cases when budget allows. Log sample size, not an unsupported reliability percentage. Record:

```text
Case / repetition / explicit or implicit invocation:
Package version + hash; routing block version:
Host / model / settings / permissions:
Resolved workflow + grilling source/revision:
Fixture baseline; reads and task-folder changes:
Meaningful decisions detected; answer sources; unanswered choices:
Application writes before approval, if any:
Evidence references for each PASS / FAIL / NOT_RUN:
```

For interruption, stop a real session mid-unit without requesting a handoff first, then resume its actual files in a fresh session. The synthetic interrupted fixture is a rehearsal, not proof of an abrupt-stop recovery. For reader clarity, have a teammate explain the delivered report without prior chat; an agent self-check is not independent user research.

## Rollout

Run B01–B09 and B12/B13 on the team's actual Claude configuration before relying on the stronger questioning behavior. Preserve a working previous installation. Add a regression case for any real failure, then change the smallest relevant instruction. No hooks, permissions bypass, mandatory new skill or automatic publication is introduced by this protocol.
