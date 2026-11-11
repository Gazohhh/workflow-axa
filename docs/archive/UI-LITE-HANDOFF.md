# workflow-axa — UI-lite proposal (not installed)

This is an isolated **source ZIP candidate** from the supplied latest `workflow-axa(1).zip`, not a commit, push, install or approved release. Have Claude review independently before adoption. All existing files are retained except `.git`, bytecode/cache and other generated metadata.

## Changes

1. **Quick styled examples in the existing approval report** (no prototype app): optional `ui_review.quick_previews` lists one existing HTML element (`#id`/`.class`/`tag.class`/`tag#id`) and one to four existing compiled CSS source IDs. The renderer extracts a sanitized fragment, embeds its current CSS in a no-script/no-network sandboxed iframe, and displays a short preview and expandable, full-width, scrollable view. Report-only padding improves legibility. No app CSS, new UI classes or dependencies are created. Other UI diagram and owner approval gates are unchanged.
2. **Manual changes / design drift:** `skills/ui-design/scripts/design_drift.py --root <project>` compares Git changes against a last **reviewed** baseline recorded optionally in `DESIGN.md` (`<!-- workflow-axa-design-baseline: FULL_GIT_SHA -->`); it includes tracked committed, staged, unstaged and untracked UI files. Missing or divergent baseline => unknown; approvals are never inferred. Run it when planning UI tasks; scope review to changed files, broadening on shared CSS changes. No separate database or auto-edits.
3. **Policy:** `DESIGN.md` should remain a policy/approval/usage/exception reference, not a second copy of CSS variables. Existing Angular/React code and real styles are authoritative. New approved components may need one-time example/kit registration. No automatic approval from code changes.

## What this deliberately does NOT do

- Does **not** run Angular/React/Ionic, compile SCSS, perform network requests or take production-API risks. Framework-bound/dynamic components still need a real authorised local app capture. A static fragment is a *real existing HTML/CSS sample*, **not a rendered proposed screen**.
- Does **not** rewrite old reports, move design baseline markers automatically, edit the Cheflabels application or DESIGN.md, or change approved application styles.
- Does **not** add a new skill, phase, UI framework or extra registry. The gallery remains optional; if a source is unavailable, use the existing schematic/capture and cite the gap.
- The baseline tool reports changed **files**, not a full selector dependency graph. Shared-token changes warrant broader checks.

## Files changed / added

- `skills/codebase-map/scripts/quick_preview.py` (new)
- `skills/codebase-map/scripts/screen_flow.py`, `render_report.py`
- `skills/codebase-map/assets/ui-review.css`
- `skills/codebase-map/UI-FLOW.md`, `REPORT.md`
- `skills/ui-design/scripts/design_drift.py` (new)
- `skills/ui-design/{SKILL.md,LIVE-KIT.md}`
- `skills/rule-maker/rules/design.md` and required `version.json` hash
- `tests/test_quick_preview.py`, `tests/test_design_drift.py` (new)
- `tests/fixtures/quick-preview-sample/*` (example projection + HTML/CSS)

## Local verification already done

- `python tools/validate.py` — PASS.
- `PYTHONPATH=tests python -m unittest tests.test_quick_preview tests.test_design_drift tests.test_screen_flow tests.test_reports tests.test_ui_design tests.test_design_kit -q` — **188 tests PASS**.
- Browser in headless Chromium using the generated demo report: two sandboxed previews loaded; existing sample CSS rendered **24px padding**; no browser console errors. The main report's CSS stayed isolated from the preview.
- `render_report.py --check`: MATCH on unchanged sources; changed CSS => expected CHANGED status.
- The complete full-suite test run was attempted but **did not finish before the runtime timeout**. Do not report it as PASS. Live Claude/Codex session and real Cheflabels UI are NOT TESTED.

## Independent audit checklist

- Verify source extraction/HTML sanitization with untrusted tags, malformed HTML, external images/URLs and nested custom elements.
- Verify iframe CSP/sandbox and no app network calls (including CSS `url()`/`@import`).
- Verify compiled-CSS-only behaviour and fallback for Angular templates, Ionic host elements and SCSS-only projects.
- Verify a real report with two or more examples expanded, responsive layout and 8 MiB report limit.
- Verify stale report manifests detect changed HTML/CSS; changed baseline/UI files don't silently count as approved.
- Run full Windows + WSL suites and one live E2 plan in a disposable Cheflabels worktree, with **real owner approvals**. No automatic install/commit/push or paid test without owner authorisation.
