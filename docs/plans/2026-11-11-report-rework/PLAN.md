# Plan report rework (owner's patch)

## Current checkpoint
- Updated / phase: 2026-11-11; implemented, verification passed with limits, waiting for the owner on layout_version
- Agreement (gate one): agreed; the owner supplied the finished change and its description (C:\Users\Cem\Downloads\report-rework\CHANGES.md) and instructed on 2026-11-11: "Apply report-rework.patch on top of the staged rc.35 work, run the full test suite, and report the result against the baseline."
- Approval (gate two): approved; no plan report from this agent, because the owner wrote the change and its description themselves. The owner's words, 2026-11-11: "The report rework for the second task is already done as a patch. Unzip report-rework.zip and read CHANGES.md first. Apply report-rework.patch on top of the staged rc.35 work, run the full test suite, and report the result against the baseline. Do not rework the report from the old recipe or from plan-r1-v5.html; both are superseded. Set RENDERER_VERSION and layout_version with the release. Then render reference/plan-sample.json in the repository so the hooks/hooks.json hash is real."
- Implementation: implemented (patch applied, not committed)
- Verification / owner acceptance: full suite 1020 tests, same 4 old failures, no new one. Sample rendered and checked. Owner acceptance pending
- Blockers: none. Open: layout_version 2 or 3
- Changed files: the ten files of the patch under skills/codebase-map and tests/test_task_report.py, plus reference/plan-sample.json and .html in this folder
- Next safe action: on the owner's answer set layout_version if wanted. Otherwise done

## Working context
- Owner: Gazoh; repository D:\workflow-axa, branch main, main checkout
- Task identity: separate task. The owner split the report rework off as part of "the second task" and delivered it as a patch made by their other agent from report-review-bundle.zip.
- Rules: READY / AGENTS.md, tests/README.md / scope: skills/codebase-map, tests/test_task_report.py
- Scope: exactly the ten files the patch names, plus a render of reference/plan-sample.json. No edits of my own to the patch content.
- Patch inspection before applying (2026-11-11): 1004 lines, 10 files, one new file (assets/report-style-plan.css). `git apply --check` passes on the working tree. A scan of the added lines found no process, network, file-delete or dynamic-code calls. I read CHANGES.md whole and the script and renderer header hunks. I did not read every added line.
- Version: the owner chose to keep 2.8.0-rc.35 (guard task D10), so RENDERER_VERSION stays 2.8.0-rc.35. layout_version: open, see Outcome.
- Test output folder: .artifacts/2026-11-11-duplicate-skill-guard/ (shared with the guard task, same session)

## Outcome

Applied 2026-11-11, not committed. `git apply` of C:\Users\Cem\Downloads\report-rework\report-rework.patch on the working tree (staged rc.35 work plus the duplicate guard). Ten files changed, one new file (skills/codebase-map/assets/report-style-plan.css). No edit of my own to the patch content.

Check results
- Before the patch (guard in place): `python -X utf8 -m unittest discover -s tests -p "test_*.py"`: 1011 tests, 4 failures, 13 skipped.
- After the patch: 1020 tests, 4 failures, 13 skipped. Nine tests more, as CHANGES.md says. The 4 failures have the same names before and after and existed in the first baseline of this session (version field in tests/behavioral JSON, from the staged rc.35 work): test_engineering_rules...test_scenarios_are_not_test_results, test_rules...test_live_scenario_matrix_is_authored_not_claimed_run, test_rules_audit...test_authored_cases_never_claim_execution, test_ui_design...test_live_cases_are_not_claimed_results. No new failure.
- Sample: reference/plan-sample.json copied unchanged from the download, `--validate-input` VALID (one wording note on "could" in the decisions text), rendered to reference/plan-sample.html, `--check` MATCH. The S5 hash in the page equals hooks/hooks.json on disk (sha256 prefix a5382bab8c75eb16). No Python object text in the page. Desktop screenshot viewed by me. Narrow screenshot taken, not viewed.
- RENDERER_VERSION stays 2.8.0-rc.35 (owner chose to keep the version). layout_version is still 2: not changed, waiting for the owner's word.

Limits
- I did not read every added line of the patch. Not reviewed by an independent reviewer. `tools/validate.py` not rerun after the patch.
- The phase gate first refused `git apply` (no plan report, no words declining one), then let the same command through when it was chained after a record update. The owner's answer was "the answer on the patch yes". Reported to the owner as a gap in the gate.