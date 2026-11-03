# UI evidence and preview engine for plan reports

## Current checkpoint
- Status: questions answered (DECISIONS D1-D5); waiting for agreement and plan approval
- Owner: this Claude Code session (workflow-axa-ff); ownership: active
- Updated: 2026-11-03
- Repository / branch / worktree: D:\workflow-axa, main, main worktree
- Task identity: new, separate task. Source: the owner's request of 2026-11-03. Related: `2026-11-02-modular-engineering-workflow` (built the current screen flow and D14) and `2026-11-03-audit-hardening` (report wording and replace rules, T5).
- Rules readiness: READY (repository CLAUDE.md, package tests, shared rules 1.8.0).
- Agreement: proposed revision r1, not agreed. U1-U4 answered as D1-D5.
- Approval: proposed revision r1, not approved. Report: `reviews/plan-r1.html`.
- Current understanding / evidence: FINDINGS.md E1-E19.
- Next safe action: the owner says yes to the agreement and the plan, or asks for changes. Nothing is built before that, and no application repository changes in this task.

## Goal in plain words
Today a plan report shows the current screen as a screenshot when that is safe, and the proposed screen as a labelled sketch. The goal is to show real screens and real components wherever that can be done safely, link every element to its real source and approval status, and refuse visual approval when an accurate picture is not possible.

## Requirements (the owner's request, 2026-11-03)
- R1: Inspect the existing workflow, renderer, design rules and project architecture before proposing changes.
- R2: Discover approved kit components, variants, wrappers, styles and actual usage from source code, never from documentation alone.
- R3: Use real application screenshots for current UI and isolated renders of real components for proposed UI.
- R4: Keep the original framework, styling, fonts, assets and responsive behaviour. Never recreate application components with invented HTML, CSS or SVG.
- R5: Show screen-by-screen before and after, connected user actions, highlighted changes and design-decision callouts.
- R6: Link every preview element to its real source component, variant, approval status and decision.
- R7: Support framework-specific capture adapters through one shared interface.
- R8: Verify preview fidelity, missing assets, runtime errors and unintended visual changes.
- R9: Keep approved review snapshots and detect stale previews when components change.
- R10: Keep the existing report styling and approval workflow; improve only the application previews.
- Also: respect approved versus candidate components; change no application code and invent no UI to make a preview work; block visual approval when an accurate picture is impossible; capture no screen that shows personal data.

## Agreement
Proposed revision r1, not agreed. It covers the requirements above, the architecture below and the boundaries, with the owner's answers: contract first and two adapters (D1); Playwright installed or used only when an accurate capture needs it, and recorded (D2); the Cheflabels design kit stays separate from task reviews, which reuse its approved components and real screenshots (D3); only explicitly approved components count as approved, the rest stay candidate or unverified (D4); framework-agnostic, and never invented UI when real components or screenshots exist (D5). If a Cheflabels capture would reach the live backend, that preview stays blocked until a separate Cheflabels task makes it offline.

## Proposed architecture (recommended: contract first, then two real adapters)
1. **Evidence contract (in workflow-axa, framework-neutral).** One manifest per capture: the image, the viewport and environment, the component and variant it shows, approval status (approved or candidate) from the project's kit source, the decision IDs it supports, the console errors, failed requests and missing assets seen during capture, and fingerprints of every file the component depends on. The renderer accepts a real preview only with a valid manifest. Missing or failed evidence keeps the sketch and blocks visual approval.
2. **Element verification.** Before a report is rendered, check that each cited `file:line` really contains the tag, classes and wrapper the report claims.
3. **Adapters behind one interface.** Each adapter answers five things: discover (components, variants, usages from source), render one component in isolation, capture a screen, report runtime problems, fingerprint dependencies. The workflow has one flow; only the adapter differs. Planned adapters: static HTML (from today's tool), Angular/Ionic through an approved kit route (Cheflabels), React/Vite through the project's own harness (Altinstar). Next.js, Vue and native follow the same interface later. Unity and other non-DOM screens: manual capture, or visual approval blocked.
4. **A shared capture runner.** It drives an already installed browser automation tool, blocks every non-local network request, waits for a ready signal instead of a fixed delay, crops to the element, and records errors. The workflow never installs it.
5. **Staleness.** A preview is stale when any fingerprinted dependency changes. Approved snapshots are kept unchanged; a stale one is flagged, never refreshed silently.
6. **Report.** The existing styling and approval workflow stay. Screen-by-screen before and after with real images, changes highlighted from the real element positions, each element linked to source, variant, approval status and decision.

## Tradeoffs
- Contract first is safe and framework-neutral, but gives no real proposed renders until an adapter exists.
- A full adapter engine gives the most, but needs browser automation on each machine, runs project code, and is the most work to keep working.
- A kit-route-only approach is simple at capture time, but every project needs an owner-approved kit page, and native screens stay out.
- Recommended: build the contract and element verification first, then exactly two real adapters (Cheflabels, Altinstar), because two real users justify a shared interface; one would be guesswork.

## Boundaries
- No application code changes from this task. Anything a project needs (Cheflabels offline translations and configuration, a machine-readable approval list) is proposed to its owner as a separate task.
- No invented HTML, CSS or SVG for application UI. D14 stays. The report shell keeps the owner's design.
- No production contact during capture. No installs except Playwright when a capture needs it (D2). No pixel blurring is promised; screens with personal data are not captured.

## Approval
Not yet given.
