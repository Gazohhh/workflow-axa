# Local flowchart design

## Scope and local files

This is codebase-map's own design procedure. Read it directly; do not resolve, invoke,
install, fetch or require an external diagram-design skill. Its absence is expected,
not a blocker and not a fallback exception. Matt's research, debugging, TDD, review,
grilling and other workflow routes remain unchanged.

The complete codebase-map folder contains this guide, [REPORT.md](REPORT.md),
[scripts/render_report.py](scripts/render_report.py),
[assets/report.css](assets/report.css), [assets/report.js](assets/report.js), and
[the synthetic example](examples/review.json). No upstream references, scripts,
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
- **Approved style: `workflow-editorial-v1`.** Minimal light, paper `#f5f5f5`, ink `#2d3142`, muted `#4f5d75`, accent `#bf4520`, accent tint `#f5e9e4`, rule `#cdd0d5`. Serif report heading; sans node names; mono for small technical labels. System-font mode; no font files or external requests. This is the owner-approved second sample, not an unapproved branded default.
- Default 1280px-wide drawing, natural height, 18px node names and 13px notes at 100%. Reuse this choice; adjust a bounded view to keep it readable rather than reopening a style interview. No animations, glow, shadows, oversized rounded cards or decorative grid.
- Allowed output: explicit schema-2 graph geometry and a small design rationale in the existing FINDINGS. The bundled renderer creates the final report. No application edits, global profile/style-guide mutations, installation, uploads, approval actions or new requirements.

The style is already approved; no automatic brand discovery, website fetching or repeated style interview. Reuse existing answers and the selected content. A truly new user-owned design/scope decision still goes to the owner. Alternative formats must not erase the requested flowchart. An attribute comparison can accompany the flow as a table, not replace it.

## Visual contract

Shapes carry meaning: oval/rounded terminator for start/result, modestly rounded rectangle for action, diamond for a genuine decision with 2–3 labelled exits. Groups collect members rather than implying runtime order. Keep one arrow meaning per view; the caption explains it. Independent controls are neither exclusive nor necessarily sequential. Do not add error/default branches without source support.

Use at most 9 nodes, 12 connectors and 2 focal nodes per view (the selected style’s budget, not a universal scientific limit). Split larger maps by the question being answered. No repeated file paths, status badges or evidence IDs inside every node. Keep full traceability below and link it.

Place nodes on a 4px structural grid. Route through explicit orthogonal corridors, rounded elbows, separate attachment ports and off-stroke label masks. The local renderer rejects crossing/shared routes rather than supporting automatic bridges; reroute or split instead. Do not shrink labels to force a fit. Compare current/proposed meaning in aligned rows, and use stable positions when a direct topology comparison benefits from them.

The approved sample’s three views are an example, not mandatory tabs for every task. Real bug logic may need a flow and a build plan; settings work may also need containment. The default report must explain the substantive behavior, not just the implementation file graph.

## Evidence and approval boundaries

Necessary questions still use `grilling`; research and plan/task preparation precede a ready report. Evidence, exclusions, important unknowns and acceptance stay visible. The HTML is a projection, not authority. The workflow stops for real user approval of the identified revision before code. Approving the report style does not approve a represented application change.

## Quality checks

Validate schema, task/evidence references, current/proposed basis, explicit geometry, decision labels and source fingerprints. In a browser inspect actual font fit (including diamond interiors), branch fidelity, native size/Fit, alternate views, keyboard controls, evidence links, offline/no-script display and narrow-window scrolling. Technical geometry checks do not prove user understanding or semantic completeness. List unavailable checks in the task record.


## Provenance, not a dependency

The owner approved the flowchart sample inspired by Cathryn Lavery's diagram-design
repository. This guide retains and localizes the workflow's own 2.2.0 design contract;
it is not a vendored copy or complete reimplementation of that upstream skill. The
approved renderer/style remain local and versioned with workflow-axa. No upstream
scripts, font files or complete skill tree are redistributed, and no installed
upstream invocation is claimed.

Historical design references, reviewed in the 2.2.0 work on 2026-10-14:
[skill](https://github.com/cathrynlavery/diagram-design/blob/main/skills/diagram-design/SKILL.md),
[flowchart grammar](https://github.com/cathrynlavery/diagram-design/blob/main/skills/diagram-design/references/type-flowchart.md),
[style](https://github.com/cathrynlavery/diagram-design/blob/main/skills/diagram-design/references/style-guide.md),
[connector primitives](https://github.com/cathrynlavery/diagram-design/blob/main/skills/diagram-design/references/primitives-core.md),
[output sizing](https://github.com/cathrynlavery/diagram-design/blob/main/skills/diagram-design/references/output-spec.md).
These are attribution only, not required reading during a task or an instruction to
follow upstream changes. Review changes to this local contract through the team's
normal versioned workflow.
