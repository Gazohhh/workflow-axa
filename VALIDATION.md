# Validation — workflow-axa 2.7.0-rc.7

Date: 30 October 2026. Based on the actual supplied rc.6 archive. Tests use Python 3.13/Linux and Chromium 144.0.7559.96 with already installed Playwright. This release changes the package only, not an application, live kit, user profile, memory, device or global installation.

## Observed results

- rc.6 baseline: **490 tests ran, 489 passed, 1 skipped** (Git-checkout-only policy test; archive has no .git).
- Candidate: **545 tests ran, 544 passed, 1 skipped**, same checkout limitation. Fifty-five added regressions exercise strict UI policy, exact component/pattern/variant/state/example selection, scope and candidate rejection, capture input/image fingerprints, changed/deleted sources, partial approval, source escaping and local Storybook-index discovery. No unresolved failing tests or expected failures.
- Package validator: PASS, eight local skills, relative references, manifest consistency and existing word budgets. Main workflow: 1,236 words. Shared rules library 1.6.0, package rc.7.
- Browser suites: **19 base-report + 19 historical/additive UI + 10 source-bound kit checks = 48 passed**. The new suite checks component details, element/source navigation, mobile scrolling, no-script disclosures, inert images, offline behaviour and deletion without rewriting the saved report. Its grey PNG and catalogue are synthetic fixture data, not a real application kit or human approval.
- Visual regression against rc.6: initial comparison matched three views exactly and found eight edge pixels different in the desktop-build view. No report asset or threshold was changed. A second capture matched all four views exactly against the original baseline. This small rendering variability is disclosed rather than claiming universal pixel identity.
- All four report assets (`report.css`, `report.js`, `ui-review.css`, `ui-review.js`) are byte-identical to rc.6. The existing full report shell is retained; exact selection tables are added only to optional UI-screen details using existing styles.
- All **34 pre-existing task-history files** are byte-identical. Matt's catalogue differs only in the package version field. Questioning policy, artifact policy/installer, shared TypeScript rule and global activation helper are byte-identical.
- Release packaging: archive integrity and source/extraction equality are checked. Package validation, all tests and all three browser suites are rerun from the fresh extracted release. No generated QA images/logs, machine paths, Git internals or Python caches are included in the installable archive.

## Initial failures and repairs

The first suite runs identified stale version assertions and missing documentation wording after the edit. Those were corrected without weakening the checks. Browser verification caught a changed accessible label for existing decision markers; that label was restored. The new fixture exposed a missing-source error path and narrow mobile table columns; the error now names the missing kit source, and the optional table reuses the existing scrollable technical-table styling. No application theme, core report CSS or screenshot reference was changed to force a pass.

## What the checks do not establish

- **No live Claude/Codex/T3 loading or compliance test was run.** All 26 new cases in [STRICT-KIT.md](tests/behavioral/STRICT-KIT.md) remain NOT RUN. Earlier live-host cases remain unverified unless their own evidence establishes otherwise.
- No real Altinstar/Cheflabels kit, React/Angular component runtime, backend, build or device was inspected or modified. Installing this skill does not create a kit page, set up Storybook, run a sync service or migrate project documentation.
- No OS/tool-level hook, permission blocker or absolute prevention mechanism was installed. Instruction compliance still requires actual host testing. The diff helper is triage, not approval or comprehensive enforcement.
- Source hashes establish that declared inputs match supplied bytes. They do not authenticate a human decision, prove every dependency is listed, or prove the captured pixels came from that code. Actual render evidence and owner acceptance remain necessary.
- The optional Storybook adapter reads a local generated v4/v5 index. It detects missing story files/entries but is not a compiler or module graph; deleted exports or broken nested imports still need project verification. Tags are not approval. Generated indexes can themselves be stale.
- No native Windows/macOS profile, desktop opener, Firefox/Safari, real accessibility audit or human comprehension test was performed. Existing Windows-related regression fixtures remain present.

## Browser transport

Direct file:// navigation was blocked by the managed environment (ERR_BLOCKED_BY_ADMINISTRATOR). Identical HTML bytes were loaded through the browser content API with networking disabled. No external HTTP/WebSocket request or script exception was observed in successful suites. --no-sandbox was used only in this trusted disposable container. This does not verify desktop double-click/open behaviour.

## Compatibility

Non-UI report input remains compatible and existing saved HTML is untouched. Historical/draft schematic demonstrations remain readable, explicitly non-authoritative. **New approval-ready application UI reports have a stricter contract:** approved-kit selection, real captures, exact elements including the composition pattern, and source/capture evidence. Earlier plain-markup/design-authoring modes do not grant current UI permissions. See UPGRADE.md and UI-FLOW.md; do not silently rewrite old approvals or add mandatory duplicate kit manifests.

## Reproduce with already installed tools

```bash
python -X utf8 tools/validate.py
python -X utf8 -m unittest discover -s tests -q
python -X utf8 skills/rule-maker/scripts/audit_installation.py
python -X utf8 tools/browser_smoke.py --browser /path/to/chromium --output /new/base-check
python -X utf8 tools/ui_browser_smoke.py --browser /path/to/chromium --output /new/ui-check
python -X utf8 tools/kit_browser_smoke.py --browser /path/to/chromium --output /new/kit-check
```

Do not install tools or spend live-model credits implicitly. Browser helpers refuse existing output directories. Keep only necessary release evidence under the artifact policy; these commands do not author or install a project UI.

---

## Earlier release reports — historical, not current results

# Validation — workflow-axa 2.7.0-rc.6

Date: 30 October 2026. Based on the owner's uploaded rc.5 source checkout and original review-r2.html. Testing here used Python 3.13/Linux and Chromium 144.0.7559.96 through already installed Playwright. No application repository, production backend, global host profile or remote model was modified or invoked.

## Observed results

- Supplied rc.5 baseline in a sanitised package: **437 tests ran = 436 passed + 1 skipped**. The skipped test requires a Git checkout; the installable payload deliberately contains no .git. This is a separate Linux run, not a claim to have repeated the source's Windows environment.
- Candidate: **490 tests ran = 489 passed + 1 skipped**. The same Git-checkout-only test was skipped. No expected failures or unresolved failing tests. Fifty-three new tests cover optional UI schema, authority boundaries, source/PNG validation, preserved sections, safe escaping, original views, capture sources, installation extras and policy references.
- Three new regression tests first demonstrated missing draft-preview/kit/acceptance constraints; after the targeted fix they pass. No test assertion was weakened to suppress those failures.
- Package validator: PASS; eight local skills, references, metadata and rule manifest. Core sizes remain within existing budgets (workflow 1,250 words; codebase-map 844; ui-design 849, including frontmatter).
- Existing browser suite: **19 checks passed**.
- New additive UI report suite: **19 checks passed**. Includes full-report preservation, diagrams and screen tabs, native zoom/Fit, source/decision links, desktop/mobile overflow, inert screen controls, no-JavaScript navigation, print layout and the local PNG path.
- Visual comparison: **four legacy desktop/mobile views match the uploaded rc.5 with zero changed pixels** in the same controlled environment. This does not assert that new UI views have no pixels, nor promise identical fonts across operating systems.
- Both original R2 SVG diagrams are structurally identical in the additive sample. The original report.css and report.js are byte-identical; optional UI CSS/JS are appended only when ui_review is present.
- Original review-r2.html matches the supplied historical task file byte-for-byte. All **33 existing task-history files** are preserved. The Matt specialist registry is unchanged apart from package version. Grilling policy, artifact policy/installer, TypeScript rule and global activation helper remain byte-identical.
- Source rule manifest: consistent. Shared library 1.5.0, package 2.7.0-rc.6. Source-to-release byte equality, ZIP integrity and the final extracted-run results are checked during release packaging.

## Browser and artifact limits

Direct file:// navigation was blocked by this managed test environment (ERR_BLOCKED_BY_ADMINISTRATOR). The identical generated HTML was tested through the browser content API, offline. No external HTTP/WebSocket request or JavaScript exception was observed. No desktop default opener, Firefox, Safari, native Windows/macOS installation or device rendering was tested. --no-sandbox was used only for Chromium inside this trusted disposable container.

The report uses no network assets or bundled fonts. Screens are either inert structured sketches or bounded local PNG captures. The parser validates structure, dimensions, CRC and limits; it does not scrub private pixels, verify the depicted application or authenticate designer consent. The tested image fixture is synthetic. No real project kit was rendered.

## Explicitly unverified

- **No live Claude/Codex/T3 session, context loading or compliance test.** Fourteen new cases in [UI-SCREEN-FLOW.md](tests/behavioral/UI-SCREEN-FLOW.md) remain unrun, as do earlier live cases unless separately established in their own histories.
- No current Altinstar/Cheflabels code, kit, memory, build, backend or device acceptance. Source records of owner decisions and past tests are preserved, not independently re-certified.
- The owner's rc.5 runtime swap/global activation were still held in the supplied checkpoint. This release does not perform them or imply they succeeded.
- No OS sandbox or agent-tool permission hook is installed by this update. Read-only helpers check structure/freshness, not all ways an agent might act.
- The installation audit is relative to a trusted local package, not a remotely authenticated signature. Unexpected files inside the eight owned trees are flagged, not deleted. Unrelated external skills remain outside its comparison.
- Old schema-2 inputs still work. An old renderer may ignore the new optional UI field: install the complete new codebase-map folder and verify the UI tab rather than assuming an older runtime supports it.
- Presentation snapshots are not current task status. Draft, design-authoring, behaviour approval, implementation and release remain distinct.

## Reproduce locally

From a complete package, with already installed optional tools:

```bash
python -X utf8 tools/validate.py
python -X utf8 -m unittest discover -s tests -p 'test_*.py'
python -X utf8 skills/rule-maker/scripts/audit_installation.py
python -X utf8 tools/browser_smoke.py --browser /path/to/chromium --output /new/qa-directory
python -X utf8 tools/ui_browser_smoke.py --browser /path/to/chromium --output /new/ui-qa-directory
```

Do not run browser installations or live-credit tests implicitly. Existing output directories are not overwritten. Optional visual capture/comparison commands are documented in tests/VISUAL-REGRESSION.md.

---

## Earlier release reports — historical evidence, not this release's environment

# Validation — workflow-axa 2.7.0-rc.5

Date: 30 October 2026. Built from the rc.4 source tree on the owner's Windows 11 machine. Python 3.14.2 (Windows), Git 2.38.0.windows.1, Pillow 12.1.0. Python Playwright is not installed. Checks ran with `PYTHONDONTWRITEBYTECODE=1` and `python -B`; output went to the console.

## Observed package checks (rc.5)

- `python -X utf8 tools/validate.py`: PASS (exit 0). Eight skills, manifest consistency, shared-rule hashes, relative links; workflow core 1,235 words.
- `python -X utf8 -m unittest discover -s tests -p "test_*.py"` in the source checkout: exit 0. **437 ran = 426 passed + 11 skipped.**
  - Skipped: 5 existing symlink-dependent tests ("symlinks unavailable"); 4 file-symlink rejection tests ("file-link rejection is unverified here"); 1 POSIX-mode test ("mode preservation is unverified here"); 1 FIFO test.
  - Directory-link rejection was exercised with real NTFS junctions.
- **Release archive:**
  - The replacement ZIP holds every Git-tracked file in its working-tree bytes, plus `.gitattributes` and the two new test files.
  - It excludes this release's live-audit task folder (`docs/plans/2026-10-30-rules-audit-design-kit/`), which holds machine-specific evidence.
  - It was extracted into a fresh directory. Archive integrity passed, and the payload is byte-identical to the source.
  - In the extracted tree: validator PASS (exit 0); unittest exit 0, 437 ran = 425 passed + 12 skipped (the extra skip is the Git checkout-policy test, since the extract is not a Git checkout); installation self-audit DISK_MATCH at 2.7.0-rc.5.
- Skills inventory: 95 files, sha256 `a53b10d516db7b060d4588905b148516516990e32bdf6c8b9b5e9654ff108abd` (sha256 over the sorted list of "path, NUL, file sha256, newline"). Identical in source and extract.

## Not run or unverified (rc.5)

- **No live Claude/Codex sessions.** Installed, loaded, followed and enforced are separate, and only disk-level checks ran.
- No browser checks or visual comparisons: Playwright is unavailable and was not installed. The flowchart renderer is unchanged from rc.4.
- On this host: file-symlink rejection and POSIX file-mode preservation.
- No Linux or macOS run of rc.5.
- No application tests, builds, device checks or backend calls.

## Earlier candidate (2.7.0-rc.4) — history, not rc.5 evidence

Date: 30 October 2026. Full candidate built from the supplied rc.3 package. The supplied two-project review pack informed requirements; it is not proof of the current repositories or host installations. No private source pack, memory transcript or project component was bundled.

## Observed package checks

- **418 automated tests passed.** Includes all retained regressions plus installation comparison, Angular/Ionic/Capacitor facts, source/config freshness, no-write checks, optional catalogue schema/selection/scope/reference checks, unsafe paths, drafts/deprecation, stale approval evidence and authored-scenario integrity.
- **19 Chromium browser checks passed**, with no external requests/page errors. Covered report layout, semantic controls, view switching, source links, mobile behaviour, optional checkpoint/history and no-script operation.
- **4 same-environment visual comparisons passed with zero changed pixels** against rc.3: desktop proposed/current/build views and mobile proposed view. These compare the approved report renderer, not a real application design kit.
- Package validator passed: eight registered skills, manifest consistency, shared-rule hashes, relative references and existing maintenance budgets. Workflow core remains 1,235 whitespace-delimited words.
- The final ZIP was extracted into a fresh directory; package validation, the complete 418-test suite, installation self-check and 19 browser checks were rerun there. Archive integrity and source/extracted payload equality were checked.

Read the bounded results in [rules-audit-kit-results.json](tests/evidence/rules-audit-kit-results.json) and the tooling transcript in [rules-audit-kit-tooling.txt](tests/evidence/rules-audit-kit-tooling.txt). Prior evidence files remain historical, not new test claims.

## Preservation checks

Matt's 27 catalogue entries are identical to rc.3 except the package release label; the specialist adapters and questioning rules are byte-identical. The shared artifact policy, artifact installer and shared global-reference helper are byte-identical. The flowchart renderer, CSS, JavaScript, local design guide and example files are unchanged. All old package files/task history are retained; no font binaries are included.

## Environment and browser limitation

Python standard-library tooling tests ran on Linux with Git available. Optional visual tests used the already available Pillow and Playwright/Chromium (144.0.7559.96); no package installation was performed. Existing visual comparison code emitted a Pillow deprecation warning; it did not affect the passing comparison and no runtime dependency was upgraded.

Browser checks ran with networking disabled. Managed policy blocked direct `file://` navigation, so the same HTML bytes were loaded via the browser content API. Tests used the explicit no-sandbox switch only inside this trusted disposable container. This does not verify a desktop file opener, Safari, Firefox, native Windows/macOS installation or all accessibility behaviour.

## Explicitly unverified

**No live Claude/Codex evaluations ran.** The 30 new cases in [RULES-AUDIT-KIT.md](tests/behavioral/RULES-AUDIT-KIT.md), as well as earlier live suites, are authored scenarios, not passed model tests. Instructions do not enforce tool calls; the helpers do not install hooks, run the host, infer authentic permission or prove an agent followed a rule.

The installation checker compares explicit candidates against the trusted local package executing it, not a remote release/signature. It does not discover every host cache or identify the host-selected copy from disk alone. Its global check validates managed references, not all user settings or semantic contradictions.

The optional kit checker validates selected local records and fingerprints. It does not authenticate approval, render components, infer all stylesheet/theme dependencies, guarantee preview isolation or approve shipping. Markdown/existing catalogues remain supported without conversion. Included templates contain no approved application components, palette or designer sign-off. Real project catalogue setup requires bounded inspection and approval.

No Cheflabels/Altinstar application tests, builds, production calls, device checks, repository-rule rewrites or memory changes were executed. Any current project contradictions still need an explicit scoped decision. No automatic migration, cleanup, dependency upgrade or publication is included.
