# Audit of report and visualizer changes

Read this, with [AUDIT.md](AUDIT.md), when a change touches report or visualizer code, the report renderer or how a report or UI screen renders.

## Visual-review regression

For changed reports/visualizer code, verify that the actual feature flow remains primary (not cards or generic workflow phases), branches preserve source meaning, build dependencies and containment are separate, source ambiguities stay visible, and no style approval grants application authority. Check that codebase-map uses its bundled FLOWCHART-DESIGN.md and actual browser geometry/readability when available; no external diagram skill is required. Retain evidence/acceptance/exclusions and safe offline behavior. Native-size overflow must stay within the diagram wrapper; Fit is optional.

## Rendering fidelity

When report/UI rendering changes, compare stable screenshots against a reviewed reference in the same environment. The package maintenance tools capture and compare images without replacing a baseline. Missing references or incompatible environments are NOT VERIFIED, not passes. A deliberate visual change needs the user's review before a new baseline is adopted. A passing comparison does not replace branch/meaning checks, manual accessibility review or a cold-reader check. Keep an application's own design system; the report theme is not permission to redesign the app.
