# Validation — workflow-axa 2.3.0

Validated 16 October 2026. This is package/browser testing, not proof of model compliance.

## Observed checks

| Check | Result | Evidence |
|---|---|---|
| Original 2.2.1 tooling baseline | PASS — 113 tests | Historical 2.2.1 evidence retained; original rerun before modification. |
| Updated package/tooling | PASS — 141 tests, no skips in this environment | tests/evidence/tooling-tests.txt; final extracted package rerun outside this archive. |
| Structure, metadata, references and core budget | PASS — two skills, workflow 993 words | tools/validate.py; same checks in the extracted package. |
| Offline Chromium browser suite | PASS — 15 checks | tests/evidence/browser-smoke.json; repeated on extracted package. |
| Exact screenshot comparisons against 2.2.1 | PASS — 4 cases, zero changed pixels | tests/evidence/visual-comparison.json; reference PNGs in tests/visual-baselines/2.2.1. |
| Deliberate visual defect | EXPECTED FAIL — changing node titles from 18px to 19px is detected | tests/evidence/visual-negative-control.json; four failed visual comparisons, exit 1. |
| External-provider/design preservation | PASS | tests/evidence/dependency-preservation.json. |
| Live-host cases | NOT RUN — 14 authored cases | tests/evidence/behavioral-results.json; tests/behavioral/README.md. |

Environment: Python 3.13.5, Linux x86_64, Playwright 1.57.0, Chromium 144.0.7559.96. Pillow and browser tooling were already installed. Tests used an explicitly permitted no-sandbox mode only in this disposable container; the command defaults retain sandboxing elsewhere. No dependency/browser installation was performed.

The 141 tests exercise existing renderer/checker safety plus input integrity, optional pixel comparison, negative comparison cases, synthetic task-discovery fixtures and regression checks on instruction contracts. Assertions that a rule appears in a file are not observed agent behavior. The live fixture generator creates a local baseline commit only in a new isolated synthetic repository, never the user's checkout.

## What is preserved

Matt's 27 catalogue entries and historical source metadata match 2.2.1; only workflow_version changes in the catalogue. Nine research/debugging/TDD/review/design/domain/prototype/PR/wizard route rows are unchanged. The grilling route/adapter is deliberately strengthened; writing integration now includes the local reader policy. No upstream skill bodies are bundled or replaced.

Report CSS, JavaScript and example JSON are byte-identical to 2.2.1. Renderer behavior is byte-identical after allowing the emitted tool_version change to 2.3.0. The saved example was regenerated only for version/timestamp metadata. Four prior-fixture images match exactly at the recorded viewports. No schema migration is needed from 2.2.1, no external diagram-design dependency returns, and no font files are included.

The default and mobile screenshots were also visually inspected in this maintenance session. The first mobile view shows the entry path; horizontal scrolling exposes offscreen branches rather than shrinking all labels. This preserves the previously chosen interaction, not an assertion that every future graph will be clear.

## Limits

- **No live Claude/Codex runs:** neither executable is available. Actual grilling invocation, meaningful decision discovery, task-folder reuse, compaction/handoff, approval compliance and optional helper integration have not been tested on the user's host. The new protocol must be run there before broad rollout. No model reliability score is claimed.
- **No desktop opener confirmation:** managed browser policy blocked direct file navigation. The browser suite and visual capture loaded identical HTML with networking disabled. No external requests or page errors occurred. Default-browser opening must be checked on the target machine.
- **No universal pixel-perfect claim:** screenshot equality covers four stable synthetic views in this environment. Reference images were carried forward from the already accepted design, not individually reapproved by the user. Different fonts/OS/browser conditions must be reviewed; no baseline is rewritten automatically. Image equality does not prove accessibility, semantics or human comprehension.
- **No new specialist installations:** optional skill-creator/webapp-testing were assessed from primary source guidance and documented as opt-in candidates. They were not invoked. Reading a public skill is not proof of installed availability. Matt's current user installation was not inspected or upgraded.
- **No external actions:** this delivery changes only the extracted package and disposable test fixtures. No user repository, host permissions, Git staging, remote, publication or subscription was modified.

## Packaging

The final ZIP is CRC-checked, extracted into a fresh directory and compared byte-for-byte with the source-file manifest. Structural/unit, browser and visual checks are rerun from that extracted package; their final logs are kept outside the archive to avoid a self-referential ZIP. The archive excludes .git, caches, test worktrees, credentials and font binaries. The external checksum identifies the delivered ZIP, not an upstream release or installed version.
