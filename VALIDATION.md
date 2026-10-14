# Validation — workflow-axa 2.2.1

## Executed checks

| Check | Result | Evidence |
|---|---|---|
| Supplied 2.2.0 baseline tooling suite | PASS: 108 tests, run before the patch | Baseline established before the correction; historical release logs are labelled 2.2.0 below. |
| Candidate tooling/fixture/package tests | PASS: 113 tests | [Tooling log](tests/evidence/tooling-tests.txt) |
| Chromium report checks | PASS: 15 checks; Chromium 144.0.7559.96 | [Browser results](tests/evidence/browser-smoke.json) |
| Package structure, links, metadata, local references and core budgets | PASS | Run `python tools/validate.py`. |
| Matt dependency and design preservation | PASS against the supplied 2.2.0 ZIP | [Preservation comparison](tests/evidence/dependency-preservation.json) |
| Bundled example regeneration and source freshness | PASS | Renderer `--check` on `skills/codebase-map/examples/review.html`. |

Tooling covers the complete Matt-only synthetic inventory without diagram-design,
continued questioning dependency checks, rejection of a previous-version baseline,
required local guide, absence of the retired adapter and METHODS.md replacement,
standalone map rendering, schema/geometry, safe paths, task/evidence links, source drift,
fixture safety and approval state boundaries. Fixture skill names are not actual upstream
executions. The standalone renderer test copies only codebase-map, not external skills.

The browser suite covers three readable views, node/diamond text fit, native-size default,
mobile entry, zoom/Fit/scroll/keyboard, evidence disclosure, offline/no-script display,
inert malicious text and no approval controls. Desktop flow screenshot was also inspected.
There were no external requests or page errors. Browser tools were already installed;
no dependencies or browsers were installed for the tests.

## Preservation

All 27 Matt catalogue entries, the historical source snapshot, eleven model-invocable
route rows and Q/R/D/T/M/C/P/W adapters match 2.2.0. QUESTIONS, GROUNDING, TASK-FOLDER,
PDF-DELIVERABLE, CHATGPT-PROMPTS and the specialist checker are byte-identical. The workflow
core changes only its visual-routing phrase. No locally condensed research, debugging,
testing or review methods replace Matt's skills.

Report CSS, JavaScript and example JSON are byte-identical. Renderer logic is unchanged;
only emitted tool_version changes to 2.2.1. The regenerated example differs only in that
metadata and generated timestamp. No report schema migration is needed from 2.2.0.

## Limits and checks not run

- **Claude/Codex runtime:** no live skill invocation, ordinary-prompt activation,
  questioning, handoff or implementation-approval behavior was tested. The behavioral
  scenarios are test protocols, not passing model results.
- **Desktop opener:** managed browser policy blocked direct file navigation. The identical
  HTML was tested through Playwright content loading with networking disabled. Default
  desktop opening must be tested locally; no claim that a browser window opened for the user.
- **Upstream sources:** Matt's recorded catalogue is preserved, not refreshed or certified
  as an installed collection. No Cathryn or Matt skill execution is claimed. The local
  guide preserves the previously approved design contract and historical attribution;
  it does not bundle the complete external diagram-design skill or any font files.
- **Human review/accessibility:** no new comparative usability study, full accessibility
  audit, or live application verification. Geometry and phrase checks cannot prove genuine
  understanding or authenticate approval.

Logs prefixed `2.2.0-` are explicitly historical. Current checks are rerun from the release
archive before delivery; final extraction logs, when present, are named `release-*`.

## Release boundary

Only the candidate package, its documentation, examples and tests changed. Original ZIPs,
the user's reports and application code remain unchanged. No user-environment installs,
uninstalls, staging, commits, pushes, publication or deployment were performed. Preserve
Matt's existing installation. Upgrade both local skills and replace the old external
visual-routing instruction as README describes; do not install diagram-design for this workflow.
