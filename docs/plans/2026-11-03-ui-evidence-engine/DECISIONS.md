# Decisions

Open questions for the owner (asked 2026-11-03 with the r1 plan).

## U1 — Architecture
- (a) Contract and element verification first, then two real adapters (Cheflabels, Altinstar). Recommended.
- (b) The full adapter engine at once.
- (c) Kit routes only: capture only approved kit pages.

## U2 — Browser automation
The engine needs an already installed browser automation tool (Playwright). Altinstar has it, Cheflabels does not, and the workflow never installs anything. Options: (a) you install it where you want real previews, and the rest keep sketches (recommended); (b) use the installed Edge in headless mode only, which gives screenshots but no console or network records.

## U3 — Cheflabels offline kit capture
Capturing the kit page safely needs app changes in Cheflabels: an offline configuration and a fixture translation file, so nothing reaches the live backend. Options: (a) a separate Cheflabels task for that, planned with its own gates (recommended); (b) not now: Cheflabels keeps sketches.

## U4 — Machine-readable approval status
Approval status now lives in a Markdown table (Cheflabels DESIGN.md). Options: (a) the adapter reads that table as it is (recommended, no project change); (b) each project adds a small JSON status file.
