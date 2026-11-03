# Findings

Read-only audit on 2026-11-03 at HEAD 0b4e4b4, of workflow-axa and the Cheflabels reference (D:\Cheflabels-labeler-V2). Nothing was run, built or contacted.

## What workflow-axa does today
- E1 — Flow: the agent finds an element with `ui-design/scripts/class_rules.py` (`--match` :144-185, `--compare` :84-106). It writes `ui_review.screens[].elements` by hand ({id, source, locator, tag, classes, context, changes}, `codebase-map/scripts/kit_bindings.py:220`). `screen_flow.py` validates (:81-279) and draws an SVG board (:344-408). A screen is an embedded PNG (:295-308) or a sketch of six generic control types (:19, :309-339), labelled "Sketch · not a screenshot". `render_report.py` hashes each source file (:745-749) and `--check` compares them later (:882-903).
- E2 — Partial: nothing verifies that a cited `file:line` really has that tag, those classes and that wrapper (`check_reused`, kit_bindings.py:226-248, checks the format only).
- E3 — Partial: discovery is a text scan of CSS and markup (class_rules.py:14-15), a Storybook index reader and a hand-kept kit JSON checker. Nothing extracts components, inputs, variants or usage counts from source.
- E4 — Partial/missing: `screenshot_report.py` captures local `.html` files only, at 1280 and 500 px, with no URL, element crop or readiness wait. Proposed screens are always sketches. No isolated render of real components exists.
- E5 — Partial: before/after screens, arrows, hand-placed markers and decision callouts exist (up to 6 screens). Changes are not highlighted from the real page.
- E6 — Partial: reuse mode links an element to its source, tag, classes and wrapper, but not to a component variant or an approval status. Decisions link to screens, not to elements.
- E7 — Missing: no capture adapter or shared adapter interface (the Storybook reader is the only adapter-like code).
- E8 — Mostly missing: PNG structure and size limits are checked (2 MB per image, 4 MB total). Pixel comparison covers the report shell only. No console-error, failed-request or missing-asset capture for applications.
- E9 — Partial: presented reports are never overwritten. The legacy kit mode records capture and input hashes. Reuse mode hashes only the files it cites, not the full set of files a component depends on.
- E10 — Exists: the offline report shell with its strict content policy, the owner's report design and the approval gates.

## Cheflabels reference (Angular 20, Ionic 8, Capacitor 8)
- E11 — A real kit page exists at `/design-kit`, loaded by `design-kit.routes.ts:9-14`. Production swaps in an empty routes file (angular.json:66-75); development, local and staging keep it; the login redirect skips it (app.component.ts:96-101). It renders about 30 real components with fixed fixtures and reads token values live.
- E12 — Approval status lives only in the Status column of DESIGN.md (Markdown). About 14 entries are "not on kit page", because they need backend data or native features.
- E13 — Risk: the kit page still contacts a server. Translations load over HTTP (app.module.ts:20-22, axa-translate-loader.ts:39-43), and the development environment points at the live backend. The offline fallback folder `assets/i18n` does not exist.
- E14 — No Storybook and no Playwright. Karma has no screenshot output. One earlier capture exists (`.artifacts/2026-10-31-design-kit-page/design-kit-full.png`).
- E15 — Safe real screens would need, in the app: an offline configuration, a fixture translation file, a fake session, a user payload with rights, per-page data mocks, and a capture browser that blocks every non-local request. Each is an application change for the owner to approve.
- E16 — Impossible without a server or device: live data screens, fresh translations, printing, the Wi-Fi wizard, camera and cropper, live updates and native safe areas.

## Other frameworks
- E17 — Altinstar (React 18, Vite 7) already has Playwright 1.60 and a harness that renders real components with stubbed services (test/e2e/mobile-layout/globalSetup.ts). It injects its own styles and fonts, which limits fidelity. All its kit entries are candidates.
- E18 — Next.js needs mocks for server components and data. Vue on Vite is close to React. Plain HTML is nearly covered today. Capacitor plugins exist only as web shims in a browser. Unity has no DOM classes, so class mirroring does not apply.
- E19 — Risks: production contact (E13), committed tokens in environment files, personal data in captures (the renderer does not blur pixels), running project code to capture, and fidelity limits (500 px minimum width, fonts, Ionic md vs iOS mode, WebView differences).
