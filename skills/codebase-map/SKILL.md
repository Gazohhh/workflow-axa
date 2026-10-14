---
name: codebase-map
description: "Create an evidence-linked local flowchart or codebase map when the user requests one, or workflow requests its visual approval report. Use the bundled flowchart design guide for the approved editorial diagrams; inspect current code and preserve tasks/evidence. Visualization only: never implement, approve work or launch an architecture-refactoring workflow."
---

# Codebase map

Create offline HTML/SVG with an actual flowchart as the primary view. Do not replace it with summary cards, UI mockups or generic research/plan/build boxes. A local report is not an editable Miro board. This skill can be invoked independently; never call workflow recursively.

## 1. Establish the view and current evidence

Read applicable project rules. Resolve the repository/worktree and relevant local changes. Inspect the behavior’s owner, entrypoints, callers, alternate paths and tests/docs. Reuse task findings after checking freshness. Keep static inspection, runtime observation, inference and unknowns distinct. Missing access blocks current-code claims; label explicitly requested hypothetical designs.

Choose **current** for “show how it works”, **proposed** for a supplied/requested future design, **compare** for an implementation review. In compare mode the proposed feature flow opens first; current behavior and an aligned change comparison remain available. For greenfield work show the verified integration point or absence, not a fictional old feature.

Reuse existing requirements, answers, PLAN, TODO, FINDINGS and decisions. No new refactor candidates or product features merely to enrich the map. Standalone inspection needs no implementation scaffold.

## 2. Apply the local flowchart design

Read [FLOWCHART-DESIGN.md](FLOWCHART-DESIGN.md). This guide, report assets and renderer are bundled in this skill. Follow them directly; no external diagram-design installation, lookup or invocation is required. Matt's architecture-improvement command is not the visualizer. Missing local guide/assets/runtime are installation or rendering issues, not a reason to install a third-party skill or waive approval.

Use the inspected evidence, approved answers, type, audience, revision and allowed artifact paths. Choose the geometry, not new product behavior. Main flow: start/actions/real decisions/results, short domain labels and labelled branches. Structural containment, runtime steps and delivery dependencies belong in separate focused views when needed. Preserve independent controls as independent; do not invent an exclusive decision or sequence. Unknowns and conditional/error paths needed for approval stay visible.

Reuse the approved workflow-editorial-v1 light styling and offline/system fonts. No repeated branding interview, online references or external checker is needed. Do not replace the requested flowchart with cards or the old generic grid.

## 3. Render, inspect and open

Read [REPORT.md](REPORT.md). Derive schema-2 JSON from authoritative task records. Explicit node geometry and connector routes are validated; each change retains requirement/task/evidence traceability. Approval-ready compare requires the resolved revision, PLAN/TODO/acceptance and no material open decisions; otherwise use draft.

Render with the bundled standard-library tool in the authorized artifact directory. The renderer packages the explicit local design; it does not understand code or authenticate approval. No application edits, tests written, migrations, dependency installation, uploads or publication. Explicit no-file instructions take precedence.

Check source freshness and semantic fidelity. Inspect actual desktop and narrow-window output when a browser is available: default text readable, no node/path/mask collision, no document-wide overflow, correct branches and evidence navigation. Native-size scrolling is the default; Fit is optional. Disclose unavailable checks instead of claiming them.

Request local opening with `--open` when supported and give the absolute artifact path. Report the actual accepted/failed/unverified result; launch acceptance is not proof of display. A headless host may deliver the file. Do not install or upload to work around an opener.

## 4. Return without implementing

Return report/source paths, mode, revision, local design/renderer version, checks and limits. There is no approval button or agent connection. Workflow shows the report, stops, then records the user’s real approval before coding. A standalone map ends with artifact delivery. Visual approval never replaces necessary grilling, and settled questions are not reopened here.
