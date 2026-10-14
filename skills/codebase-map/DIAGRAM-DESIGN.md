# Diagram-design integration

## Provider and setup

Use Cathryn Lavery’s `diagram-design`, not Matt’s similarly purposed architecture workflow.
Source: https://github.com/cathrynlavery/diagram-design/tree/main/skills/diagram-design
Reviewed on 2026-10-14: main, skill metadata 2.6. No immutable commit or installed-agent execution is asserted by this package.

At authorized setup, reuse one installed copy or install the complete skill (not only SKILL.md):

```powershell
npx skills add https://github.com/cathrynlavery/diagram-design --skill diagram-design
```

The installer executes third-party code and may download packages. Never run it automatically during a review. A native marketplace install is another route documented upstream; do not enable duplicate physical copies. Confirm the actual host identifier, provider, enabled/model-invocation policy and required references. The workflow’s `check_specialists.py --only diagram-design` inventories files but not host execution. A standalone codebase-map follows these checks itself; it needs no duplicate checker or recursive workflow invocation.

Required design references: `SKILL.md`, `references/style-guide.md`, `references/type-flowchart.md`, `references/primitives-core.md`, `references/output-spec.md`, `references/layout-budget.md`; load `semantic-patterns.md` when behavior matters and the matching type reference for secondary structures. Keep the full installed tree so those branches are available. Inspect upstream `scripts/self_check.py` before executing it within the authorized local test scope; browser/dependency installation is not implied. Its script check permits only its own canonical motion controller, whereas the workflow shell uses a hashed local viewer plus an inert source manifest. Do not claim that the final shell passes that different contract or remove provenance/security to satisfy it. The upstream checker can assess an authorized standalone static diagram export; this final shell uses the supplied workflow validation/browser suite. Record which artifact and checker actually ran. See [upstream checker](https://github.com/cathrynlavery/diagram-design/blob/main/skills/diagram-design/scripts/self_check.py).

## Approved call brief

Pass once per visualization phase:

- The requested outcome, audience, approved answers, current code evidence, task/acceptance IDs and unresolved limits.
- Primary actual feature/process flow. Additional build-dependency and structural views only when useful. A diagram of the agent’s workflow does not substitute for the feature.
- **Approved style: `workflow-editorial-v1`.** Minimal light, paper `#f5f5f5`, ink `#2d3142`, muted `#4f5d75`, accent `#bf4520`, accent tint `#f5e9e4`, rule `#cdd0d5`. Serif report heading; sans node names; mono for small technical labels. System-font mode; no font files or external requests. This is the owner-approved second sample, not an unapproved branded default.
- Default 1280px-wide drawing, natural height, 18px node names and 13px notes at 100%. Reuse this choice; adjust a bounded view to keep it readable rather than reopening a style interview. No animations, glow, shadows, oversized rounded cards or decorative grid.
- Allowed output: explicit schema-2 graph geometry and a small design rationale in the existing FINDINGS. The bundled renderer creates the final report. No application edits, global profile/style-guide mutations, installation, uploads, approval actions or new requirements.

The upstream first-run style gate is satisfied by this recorded explicit choice; no automatic brand discovery or website fetching. Reuse existing answers and the selected content. A truly new user-owned design/scope decision still goes to the owner. The specialist’s general freedom to suggest alternative formats must not erase the requested flowchart. An attribute comparison can accompany the flow as a table, not replace it.

## Visual contract

Shapes carry meaning: oval/rounded terminator for start/result, modestly rounded rectangle for action, diamond for a genuine decision with 2–3 labelled exits. Groups collect members rather than implying runtime order. Keep one arrow meaning per view; the caption explains it. Independent controls are neither exclusive nor necessarily sequential. Do not add error/default branches without source support.

Use at most 9 nodes, 12 connectors and 2 focal nodes per view (the selected style’s budget, not a universal scientific limit). Split larger maps by the question being answered. No repeated file paths, status badges or evidence IDs inside every node. Keep full traceability below and link it.

Place nodes on a 4px structural grid. Route through explicit orthogonal corridors, rounded elbows, separate attachment ports and off-stroke label masks. The local renderer rejects crossing/shared routes rather than supporting automatic bridges; reroute or split instead. Do not shrink labels to force a fit. Compare current/proposed meaning in aligned rows, and use stable positions when a direct topology comparison benefits from them.

The approved sample’s three views are an example, not mandatory tabs for every task. Real bug logic may need a flow and a build plan; settings work may also need containment. The default report must explain the substantive behavior, not just the implementation file graph.

## Gates that remain outside this specialist

Necessary questions still use `grilling`; research and plan/task preparation precede a ready report. Evidence, exclusions, important unknowns and acceptance stay visible. The HTML is a projection, not authority. The workflow stops for real user approval of the identified revision before code. Approving the report style does not approve a represented application change.

## Quality checks

Validate schema, task/evidence references, current/proposed basis, explicit geometry, decision labels and source fingerprints. In a browser inspect actual font fit (including diamond interiors), branch fidelity, native size/Fit, alternate views, keyboard controls, evidence links, offline/no-script display and narrow-window scrolling. Technical geometry checks do not prove user understanding or semantic completeness. List unavailable checks in the task record.

References: [upstream skill](https://github.com/cathrynlavery/diagram-design/blob/main/skills/diagram-design/SKILL.md), [flowchart grammar](https://github.com/cathrynlavery/diagram-design/blob/main/skills/diagram-design/references/type-flowchart.md), [style](https://github.com/cathrynlavery/diagram-design/blob/main/skills/diagram-design/references/style-guide.md), [connector primitives](https://github.com/cathrynlavery/diagram-design/blob/main/skills/diagram-design/references/primitives-core.md), [output sizing](https://github.com/cathrynlavery/diagram-design/blob/main/skills/diagram-design/references/output-spec.md). Upstream is referenced, not bundled. No font redistribution.
