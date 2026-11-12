# Local flowchart design

## Scope and local files

This is codebase-map's own design procedure. Read it directly; do not resolve, invoke,
install, fetch or require an external diagram skill. Its absence is expected,
not a blocker and not a fallback exception.

The complete codebase-map folder contains this guide, [REPORT.md](REPORT.md),
[scripts/render_report.py](scripts/render_report.py),
[assets/report.css](assets/report.css), [assets/report.js](assets/report.js), and
[the synthetic example](examples/review.json). No external references, scripts,
font files or network calls are needed to design or render a report. Preserve the full
folder when installing it. Python 3.10+ is the renderer runtime; browser QA uses existing
local tools when available, never an automatic dependency install.

Missing local files or an unavailable renderer: report the incomplete installation or
runtime, preserve task evidence and pause only the dependent visual phase. Repair needs
setup authority. Do not install another person's skill, silently replace the design,
or waive the implementation-approval gate. A missing optional browser check is reported
as untested; it is not a reason to invent a third-party dependency.

## Approved design brief

Establish once per visualization phase:

- The requested outcome, audience, approved answers, current code evidence, task/acceptance IDs and unresolved limits.
- Primary actual feature/process flow. Additional build-dependency and structural views only when useful. A diagram of the agent’s workflow does not substitute for the feature.
- **Approved style: `workflow-editorial-v1`.** Minimal light, paper `#f5f5f5`, ink `#2d3142`, muted `#4f5d75`, accent `#bf4520`, accent tint `#f5e9e4`, rule `#cdd0d5`. Serif report heading; sans node names; mono for small technical labels. System-font mode; no font files or external requests. This is the owner-approved style, not an unapproved branded default.
- Default 1280px-wide drawing (at most 880px in a task report, see "Diagrams in a task report"), natural height, 18px node names and 13px notes at 100%. Reuse this choice; adjust a bounded view to keep it readable rather than reopening a style interview. No animations, glow, shadows, oversized rounded cards or decorative grid.
- Allowed output: explicit schema-2 graph geometry and a small design rationale in the existing FINDINGS. The bundled renderer creates the final report. No application edits, global profile/style-guide mutations, installation, uploads, approval actions or new requirements.

The style is already approved; no automatic brand discovery, website fetching or repeated style interview. Reuse existing answers and the selected content. A truly new user-owned design/scope decision still goes to the owner. Alternative formats must not erase the requested flowchart. An attribute comparison can accompany the flow as a table, not replace it.

## Visual contract

Shapes carry meaning: oval/rounded terminator for start/result, modestly rounded rectangle for action, diamond for a genuine decision with 2–3 labeled exits. Groups collect members rather than implying runtime order. Keep one arrow meaning per view; the caption explains it. Independent controls are neither exclusive nor necessarily sequential. Do not add error/default branches without source support.

Use at most 9 nodes, 12 connectors and 2 focal nodes per view (the selected style’s budget, not a universal scientific limit). Split larger maps by the question being answered. No repeated file paths, status badges or evidence IDs inside every node. Keep full traceability below and link it.

Place nodes on a 4px structural grid. Route through explicit orthogonal corridors, rounded elbows, separate attachment ports and off-stroke label masks. The local renderer rejects crossing/shared routes rather than supporting automatic bridges; reroute or split instead. Do not shrink labels to force a fit. Compare current/proposed meaning in aligned rows, and use stable positions when a direct topology comparison benefits from them.

The approved sample’s three views are an example, not mandatory tabs for every task. Real bug logic may need a flow and a build plan; settings work may also need containment. The default report must explain the substantive behavior, not just the implementation file graph.

## Diagrams in a task report

These rules apply to a report with `task_report`. They choose which views to draw and how to lay them out. The visual contract above still holds.

Which view answers which question:

| Question | View |
|---|---|
| Where does this sit among the things around it? | System context: `purpose` structure. Boxes for the owner, the host, the new or changed part and each thing it reads or writes. Label every connector with what passes along it. Draw one when the change adds or moves a part. |
| What happens, with decisions? | Flow, one view for each trigger. |
| What happens today? | The current flow. Compare mode requires it. Keep it as small as the evidence allows. |
| In what order are the tickets built? | No view when the order is a straight line. The ticket cards show it. Draw a delivery view only when tickets branch or join. |

Layout:

- Draw every view at most 880px wide. It then fits the reading column at full size, and the report shows no zoom controls and no scroll hint. Type stays 18px and 13px. Split a view that needs more room. A wider board still renders, with zoom, for a map that cannot be split.
- One view answers one question, and its title says which ("What happens when a session starts").
- The description under the title says when the flow runs, in one sentence. It does not explain the arrows or repeat the overview.
- Flow runs top to bottom. The normal path runs straight down. Exceptions branch to the right.
- A decision is a yes/no question. Yes leaves to the right and no leaves downward, in every view of the report. Phrase the question so that this holds.
- Two paths that reach the same result join in one node. Two results that differ get two nodes with different notes.
- An action names who acts ("Guard checks skill folders"). Use "you" for the owner, never "owner".
- Use the same word for the same thing in the views and in the text.
- Keep the focus color for the one or two nodes the change is about. The legend names only the marks that are not a standard shape: group, focus and dashed outlines.

## Evidence and approval boundaries

Necessary questions still use `grilling`; research and plan/task preparation precede a ready report. Evidence, exclusions, important unknowns and acceptance stay visible. The HTML is a projection, not authority. The workflow stops for real user approval of the identified revision before code. Approving the report style does not approve a represented application change.

## Quality checks

Validate schema, task/evidence references, current/proposed basis, explicit geometry, decision labels and source fingerprints. In a browser inspect actual font fit (including diamond interiors), branch fidelity, native size/Fit, alternate views, keyboard controls, evidence links, offline/no-script display and narrow-window scrolling. List unavailable checks in the task record.


## Own design contract

This guide is the workflow's own design contract, versioned with workflow-axa. Review changes to it through the team's normal versioned workflow.


## Explain and preserve the approved view

Use everyday action/result labels and explain necessary technical terms in visible context. Do not assume the reader knows the project, but retain precise evidence and original requirement terms in the technical section. A reader should be able to describe the proposed behavior and approval decision without the prior conversation. Report an unresolved meaning rather than guessing it to simplify the diagram.

For renderer/style maintenance, compare deterministic screenshots against a reviewed prior example with the same browser, fonts, viewport and data. Missing or mismatched references are not verification. Reference replacement requires deliberate review; do not make a test pass by automatically accepting its output. Keep semantic checks and the real user approval boundary.

## Optional UI screens

[UI-FLOW.md](UI-FLOW.md) extends the same report with source-backed screen previews joined by actions and control-linked decisions. This does not change the editorial shell or permit invented application styling. Non-UI flows keep this exact visual grammar. Use kit captures for actual appearance and label authorized schematics as approximate.
