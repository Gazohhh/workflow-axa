# Validation — workflow-axa 2.2.0

## Observed checks

Tested on Linux with Python 3.13.5, Git 2.47.3 and Chromium 144.0.7559.96. Renderer/checker target: Python 3.10+ standard library. The optional browser runner uses already installed Playwright/Chromium. No upstream skills, browsers, libraries or fonts were installed during this build.

| Check | Observed result | What it establishes |
|---|---|---|
| Baseline before edits | 76 tests passed | The supplied 2.1.0 package's existing tooling suite ran before changes. |
| Package validator | PASS; workflow core 1,009 words; codebase-map 634 words | Two registered local skills, required files, minimal metadata, internal links, version/catalogue consistency and core word budgets. |
| Python unit suite | **108 tests passed** | Existing package/fixture/report checks plus explicit flow geometry, labelled decisions, ports/crossings/masks, default feature flow, delivery dependency fidelity, start links, source uncertainty disclosure and additional-provider inventory checks. |
| Chromium offline browser suite | **15 checks passed** | View selection, actual node/diamond label fit, natural-size text, desktop/mobile overflow, mobile entry centering, keyboard/drag/Fit, evidence anchors, no-script native navigation, print views and inert hostile-looking text. Zero external requests and page errors observed. |
| Bundled schema-2 example freshness | MATCH | Input and all supplied source bytes match the report manifest; not complete code coverage, semantic correctness or approval authentication. |
| Actual 2.1.0 example compatibility | MATCH | The new checker successfully checked the original example from an untouched extraction of the supplied 2.1.0 ZIP. New generation deliberately requires schema 2. |
| Final archive integrity and re-extraction | PASS | ZIP integrity and paths checked; package validation, 108 unit tests, bundled-example freshness and 15 browser checks rerun from extracted release contents. |

Candidate evidence: [unit log](tests/evidence/tooling-tests.txt) and [browser results](tests/evidence/browser-smoke.json). Browser screenshots of the default, current, build and narrow-window views were visually inspected; the working generic HTML example is included instead of large QA images or private application reports.

Commands from the plugin root:

```text
python -X utf8 tools/validate.py
python -X utf8 -m unittest discover -s tests -p "test_*.py" -v
python -X utf8 skills/codebase-map/scripts/render_report.py --root skills/codebase-map/examples --check skills/codebase-map/examples/review.html
python -X utf8 tools/browser_smoke.py --browser <installed-chromium> --output <new-results-directory>
```

The isolated root-container browser run explicitly used `--no-sandbox`; normal desktop use keeps sandboxing enabled. Direct `file://` navigation was attempted and blocked by this environment's managed policy. A new context then received the identical HTML through Playwright `set_content` with networking offline. The suite reports that limitation rather than claiming direct-file opening succeeded. A manual desktop default-browser check remains necessary.

## Not executed or not proven

- **Live Claude Code/Codex evaluation and native plugin validation:** neither CLI was present. The 37 named behavioral scenarios are authored protocols, not passed agent runs. Ordinary-prompt activation, actual specialist invocation, question quality, current-code understanding, approval compliance and recovery require testing in the actual host.
- **Upstream specialist execution:** diagram-design source/references were reviewed through the public repository. No installed invocation or upstream self-check execution is claimed. Its canonical-script checker is not the contract for this report shell; the integration documents the difference. Matt's historical inventory is preserved, not re-certified as a current installed collection.
- **Windows/macOS default opening and Python 3.10 execution:** supported by design but not exercised here. An opener accepting a request is not proof that the user saw the report.
- **Full accessibility/usability and semantic verification:** browser assertions check selected behaviors, not every assistive technology or real user comprehension. Geometry cannot determine whether an inferred route is true or whether a required branch was omitted. Source paths/hashes do not authenticate origin or prove complete repository coverage.
- **Hard enforcement:** neither instructions nor a schema can authenticate real user approval or guarantee agent obedience. Existing host permissions and the user's recorded response remain authoritative.

Only the candidate skill package, its examples, documentation and tests changed. The user's application, original R3 report and approved presentation sample remain unchanged. The release is not installed, remotely published, tagged, pushed or deployed. Follow README's upgrade checklist, verify both local skills and the separate diagram-design dependency, then run the local host pilot.
