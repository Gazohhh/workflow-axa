---
name: codebase-map
description: "Create an evidence-linked local flowchart or codebase map when the user requests one, or workflow requests its visual approval report. Use the bundled flowchart design guide for the approved editorial diagrams; inspect current code and preserve tasks/evidence. Visualization only: never implement, approve work or launch an architecture-refactoring workflow."
---

# Codebase map

Create offline HTML/SVG with an actual flowchart as the primary view. Do not replace it with summary cards, UI mockups or generic research/plan/build boxes. A local report is not an editable Miro board. Never call workflow recursively.

Write for a reader new to the project: behavior and consequences first, exact references underneath. Show risks, exclusions and unresolved choices; retain technical precision.

## 1. Establish the view and current evidence

Read project rules, repository/worktree and local changes. Inspect the behavior’s owner, entrypoints, callers, alternate paths and tests/docs. Reuse task findings after checking freshness. Keep static inspection, runtime observation, inference and unknowns distinct. Missing access blocks current-code claims; label explicitly requested hypothetical designs.

Choose **explain** when the user wants a no-assumed-context walkthrough of how a feature works today; **current** for a concise current-state map, **proposed** for a supplied/requested future design, **compare** for an implementation review. In explain mode, lead with a plain-language story of the real user/system flow, then the flowchart, then exact files/symbols/evidence; do not create a plan or propose improvements unless asked. In compare mode the proposed feature flow opens first; current behavior and an aligned change comparison remain available. For new features show the verified integration point, not a fictional baseline.

Identify and reuse the current/named task and its requirements, answers, PLAN, TODO, FINDINGS and decisions. If a likely existing record is ambiguous, ask before creating another artifact location; a new command is not a new task. Read the selected plan/review identity exactly. Distinguish the recorded baseline, approved scope, implementation and acceptance; do not infer authority from a pending badge in a historical snapshot. No new refactor candidates or product features merely to enrich the map. Inspection needs no task scaffold.

## 2. Apply the local flowchart design

Read [FLOWCHART-DESIGN.md](FLOWCHART-DESIGN.md). This guide, report assets and renderer are bundled in this skill. Follow them directly; no external diagram-design installation, lookup or invocation is required. Matt's architecture-improvement command is not the visualizer. Missing local guide/assets/runtime are installation or rendering issues, not a reason to install a third-party skill or waive approval.

Use the inspected evidence, approved answers, type, audience, revision and allowed artifact paths. Choose the geometry, not new product behavior. Main flow: start/actions/real decisions/results, short domain labels and labelled branches. Structural containment, runtime steps and delivery dependencies belong in separate focused views when needed. Preserve independent controls as independent; do not invent an exclusive decision or sequence. Unknowns and conditional/error paths needed for approval stay visible.

Reuse the approved workflow-editorial-v1 light styling and offline/system fonts. No repeated branding interview, online references or external checker is needed. Do not replace the requested flowchart with cards or the old generic grid.

## 3. Render, inspect and open

Read [REPORT.md](REPORT.md). Derive schema-2 JSON from authoritative task records. Old schema-2 inputs remain valid. Only for a requested task overview use the optional checkpoint/revision log; show its as-of/source and treat the selected flow as a historical reviewed scope, not live implementation proof. Explicit node geometry and connector routes are validated; each change retains requirement/task/evidence traceability. Approval-ready compare requires the resolved revision, PLAN/TODO/acceptance and no material open decisions; otherwise use draft.

Render with the bundled standard-library tool in the authorized artifact directory. The renderer packages the explicit local design; it does not understand code or authenticate approval. No implementation, installation or publication. Explicit no-file instructions take precedence.

Check freshness and meaning. Inspect desktop/mobile output when available: default text readable, no node/path/mask collision, no document-wide overflow, correct branches and evidence navigation. Native-size scrolling is the default; Fit is optional. Disclose unavailable checks instead of claiming them.

Before delivery, check that someone without the prior conversation can explain the change, exclusions and decision. For renderer/style edits, compare stable screenshots with the reviewed reference in a controlled environment; never replace a failed baseline automatically.

Request local opening with `--open` and give its path. Report the actual accepted/failed/unverified result; launch acceptance is not proof of display. A headless host may deliver the file. Do not install or upload to work around an opener.

## 4. Return without implementing

Return report/source paths, mode, revision, local design/renderer version, checks and limits. There is no approval button or agent connection. Workflow shows the report, stops, then records the user’s real approval before coding. A standalone map ends with artifact delivery. Visual approval never replaces necessary grilling, and settled questions are not reopened here.

## Output lifetime

Follow the active workflow's ARTIFACTS.md or its installed global policy. Keep requested HTML/JSON at the explicit review destination (project convention, otherwise existing task folder); do not create a new task to store a map. Approved/presented reviews and visual baselines are protected, not test scratch. Reuse permitted unpresented drafts; don't regenerate unchanged reviews on resume. Browser-check captures use the existing task output parent, with only necessary proof retained. No extra cleanup report.
