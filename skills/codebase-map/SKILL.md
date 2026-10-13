---
name: codebase-map
description: "Create a local Miro-style HTML codebase or feature flowchart when the user requests a map, flow, diagram, current/proposed view or comparison, or when workflow requests its preimplementation visual approval report. Inspect actual code and link evidence. Visualization only: never implement, approve work or launch an architecture-refactoring workflow."
---

# Codebase map

Produce an evidence-linked offline HTML/SVG view and editable source, not an external Miro board. Use this skill for visualization, not for general code explanations without a diagram request. The workflow may invoke it for its required approval gate; do not call workflow recursively.

## 1. Establish the view and evidence

Read applicable project instructions. Resolve the actual repository/worktree and relevant local changes; inspect the behavior's owner, entrypoints, alternate paths and relevant tests/docs before depicting current relationships. Reuse task findings only after checking freshness. Do not invent missing context, dependencies or product features. Keep static inspection, runtime observation, inference and unknowns distinct.

Choose **current** by default for “show me how it works”; **proposed** for an explicitly supplied/requested future design; **compare** for a current-versus-selected-plan review. A proposal is not approved because it has a diagram. For greenfield work depict the verified existing integration point/absence, not a fictional old implementation. Missing access blocks claims about existing code; label an explicitly requested hypothetical design as such.

Use the task's existing requirements, decisions, PLAN, TODO and FINDINGS where present. Draw the actual feature/user/data/call flow, not generic workflow phases. Choose the relevant representation and use short domain labels with technical references below. For large systems produce an overview and separately scoped detail views; keep each map small and readable.

## 2. Build the projection

Read [REPORT.md](REPORT.md). Create the JSON projection with source references, understood outcome, requested requirements, current/proposed nodes and labelled relationships, mapped tasks, exclusions, acceptance and evidence limits. Every proposed change maps to justified work; current/inferred relationships need inspected evidence. Unknowns stay visible. Do not add refactor candidates merely to improve the diagram.

For a workflow approval review, require the resolved plan revision and complete PLAN/TODO/acceptance mapping before marking `awaiting-approval`. Unresolved material decisions mean `draft`. The final understanding/approval question belongs to the owning workflow, not a new grilling interview here. Reuse settled answers. Standalone current views need no implementation plan or extra task scaffold.

## 3. Render, inspect and open

Use the bundled standard-library renderer and assets, not runtime CDN libraries or an unapproved install. Source JSON lives in the allowed source root; report output goes in the authorized task artifact folder or a unique local temporary directory. No application edits, migrations, tests written, publication or external uploads. Explicit no-file instructions take precedence; do not render a file without permission.

Run the renderer, check its supplied-source manifest, and inspect the actual HTML where browser tooling is available. Check text/arrow legibility, the flow's semantic fidelity, evidence and current-versus-proposed status. Script checks do not prove code understanding. Never claim a browser check you could not run. If Python/renderer/browser support is unavailable, disclose the actual missing capability and use only a user-approved alternative; it never waives implementation approval.

Request default-browser opening with `--open` when supported; report accepted/failed/unverified accurately and provide the absolute artifact path. A headless environment may provide the artifact without opening it. Never install or upload just to make opening work.

## 4. Return without implementing

Return mode, revision/state, source/report paths, inspection/supplied-source-check results, opener result and unresolved limits. This skill does not authenticate approval, edit the approval record or start coding. There is deliberately no approval button or agent connection in the HTML. The owner shows the report, waits for the user's response and records authority before implementation. A standalone map ends after artifact delivery.

Local examples are synthetic and labelled as such. [REPORT.md](REPORT.md) documents commands, projection fields and validation limits.
