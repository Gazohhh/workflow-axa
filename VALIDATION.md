# Validation — workflow-axa 2.1.0

## Observed checks

Tested on Linux with Python 3.13.5, Git 2.47.3 and Chromium 144.0.7559.96. Runtime renderer/checker target: Python 3.10+ standard library. The browser smoke runner additionally uses already installed Playwright/Chromium; nothing was installed during this build.

| Check | Observed result | What it establishes |
|---|---|---|
| Package validator | PASS; workflow core 1,004 words, codebase-map 620 words | Both registered skills, required files, package version/catalogue consistency, minimal metadata, internal links and local word budgets. |
| Python unit suite | **76 tests passed** | Package/fixture tooling, existing specialist checker, report states/modes, evidence/task/requirement references, cycles, unsafe paths, source drift, label escaping, saved-projection agreement, portable renderer, CLI/overwrite behavior and truthful opener results. |
| Chromium offline-content smoke | **7 checks passed** | Current/proposed rendering, visible pending approval, no submission controls, zoom/fit/pan, desktop/mobile overflow, evidence anchors and inert malicious-looking labels. Zero page errors and zero network requests observed. |
| Supplied-source example check | PASS | Bundled report input and named source file bytes match its manifest. No assertion about omitted files or complete repository coverage. |
| Final archive integrity and re-extraction | PASS | ZIP integrity checked; package validation, the 76-test suite, example freshness and 7 browser checks rerun from the extracted final archive. |

Actual candidate output: [unit log](tests/evidence/tooling-tests.txt) and [browser results](tests/evidence/browser-smoke.json). Final-archive reruns use the same included commands. Browser screenshots were visually inspected during the build; the working HTML example is included rather than bundling multiple large screenshots.

Commands from the package root:

```text
python -X utf8 tools/validate.py
python -X utf8 -m unittest discover -s tests -p "test_*.py" -v
python -X utf8 skills/codebase-map/scripts/render_report.py --root skills/codebase-map/examples --check skills/codebase-map/examples/review.html
python -X utf8 tools/browser_smoke.py --browser <installed-chromium> --output <new-results-directory>
```

The isolated root-container browser run explicitly used `--no-sandbox`; normal desktop use keeps the browser sandbox enabled. Direct `file://` navigation was attempted and blocked by this environment's managed Chromium policy. The successful visual/interaction tests supplied the same rendered HTML through Playwright `set_content` with networking offline. This does not establish successful desktop default-browser opening or direct-file policy compatibility.

## Not executed or not proven

- **Live Claude Code/Codex evaluations and native plugin validation:** neither CLI was present. The 31 behavioral scenarios are authored protocols, not passed agent tests. Ordinary-prompt activation, real specialist invocation, code-grounding quality, semantic diagram correctness, approval compliance and cross-account handoff must be tested in the actual host.
- **Windows/macOS desktop opening, OS permissions and Python 3.10 runtime:** command/path support is designed for these environments, but this build did not execute their platform-specific integrations. An accepted `--open` request is not proof that a viewer displayed.
- **Matt collection installation or full new upstream audit:** no installation, automatic update or bundled upstream collection. Its historical inventory provenance is preserved. Disk hashes do not prove host availability, source identity or actual skill use.
- **Hard enforcement:** schema checks, hashes and instructions cannot prove a requirement was really requested, authenticate user approval or prevent every model mistake. The real user response and task records remain authoritative; host permissions remain separate.

This is a local release artifact. It was not installed into a user's repository, remotely published, tagged, pushed or deployed. Read README's upgrade checklist, install both local skills, merge the reviewed routing block into the actual host instructions, and run the local behavior pilot before wider team rollout.
