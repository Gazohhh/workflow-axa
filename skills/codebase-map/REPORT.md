# Offline flowchart report contract

Design the flow locally using [FLOWCHART-DESIGN.md](FLOWCHART-DESIGN.md); no separately installed diagram skill is required. Python 3.10+ standard library packages that explicit layout into local HTML/SVG; it does not install or invoke skills. Copy this complete skill folder for a standalone installation. The output has no CDN, fonts, telemetry, uploads or approval action. Edit the JSON and render a new revision; this is not a collaborative whiteboard.

## Run

From the plugin root, use a **new** output filename:

```powershell
python -X utf8 skills/codebase-map/scripts/render_report.py --root skills/codebase-map/examples --input skills/codebase-map/examples/review.json --output skills/codebase-map/examples/local-preview.html --open
python -X utf8 skills/codebase-map/scripts/render_report.py --root skills/codebase-map/examples --check skills/codebase-map/examples/local-preview.html
```

For real work substitute the actual source root, task JSON and authorized artifact path. Quote paths with spaces. CLI paths resolve from the current directory; source paths inside JSON are root-relative POSIX paths. Input must be inside root; output parents must already exist, output must be .html/.htm, and existing files are never overwritten. Source references outside root, symlink escapes and oversized inputs are rejected. Do not claim a listed source path was inspected unless it actually was.

Exit 0: rendered/check matched; 1: freshness mismatch/missing sources; 2: invalid input or filesystem error. `--open` requests browser launch, not proof of display. An opener failure leaves the artifact intact and grants no implementation permission.

Default zoom is 100% native size inside a locally scrollable panel. Native radio inputs select view/100/125/150/Fit, including without JavaScript. Fit may reduce text and is optional, never the mandatory reading size. Progressive script adds mouse drag, centered entry on narrow screens, focused-canvas +/−/F/0 and evidence-detail opening. A native “Go to start” link works without JavaScript. Keyboard arrows and touch use native scrolling. No executable application controls.

## Schema 2

[examples/review.json](examples/review.json) is a complete synthetic example with current, proposed and build-dependency views. The example is not an actual feature authorization.

| Field | Contract |
|---|---|
| `schema_version` | `2`. New renders deliberately reject schema 1 with migration instructions. |
| `title`, `revision`, `understanding` | Plain text identifying the task, exact plan revision and understood outcome. |
| `mode` / `state` | current/proposed/compare; inspection/draft/awaiting-approval/approved/superseded. Current-only uses inspection. |
| `snapshot` | Repository label, optional branch/worktree, inspection basis and limits. Do not call uncommitted work a clean HEAD snapshot. |
| `boundaries`, `open_decisions` | Text arrays for exclusions and unresolved material decisions. Open decisions prevent approval-ready state. |
| `sources` | `id`, existing root-relative `path`, `role`. Approval-ready needs plan/todo/findings roles. Only hashes/paths, not source contents, are copied automatically. |
| `requirements` | `id`, `text`, `origin` identifying an actual request/answer/policy. |
| `evidence` | `id`, `claim`, `kind` static/runtime/design, source IDs, `locator`, `limits`. Design intent is not observed runtime/code. |
| `acceptance` | `id`, observable `text`, requirement IDs and concrete `verification`. |
| `tasks` | `id`, `title`, requested/prerequisite `kind`, justified `reason`, affected `areas`, requirement/evidence/acceptance IDs, `depends_on` task IDs. Cycles and unmapped work fail validation. |
| `comparison` | Array of `label`, `current`, `proposed`, requirement/evidence/task ID arrays. Required for compare. This aligned summary supports, never replaces, the flowchart. |
| `default_view` | Graph ID. Compare opens a **proposed flow**, not a build checklist, table or settings hierarchy. |
| `graphs` | Up to six individually scoped views. Compare includes current and proposed kinds; multiple graphs of a kind are allowed. |
| `approval` | Approved state only: matching revision, real record reference and response. Structure validation is not authentication. |

### Graph and geometry

Each graph has `id`, `kind` current/proposed, `purpose` flow/delivery/structure/technical, short `tab`, `title`, `description`, integer `width`/`height`, `nodes`, `edges`. State the arrow meaning and any inference/proposal limits in the description. Default width 1280, appropriate natural height; allowed board bounds are 400–1600 wide, 240–1600 high. These bounds keep one view readable, not an invitation to fill it.

Each node has `id`, short `label`, `note` (may be empty), `shape` start/action/decision/result/group, `x`, `y`, `width`, `height`, optional boolean `highlight`, `basis`, `change`, `evidence`, `tasks`. Group nodes may have an `items` array. Start/result are terminators, actions modest rectangles, decisions diamonds. Use explicit `\n` for at most two short label/note lines. The renderer does not auto-shrink text. Diamond labels must fit their interior, not merely their bounding rectangle. Details belong in evidence records.

Each edge has `from`, `to`, `label` (empty only for an unambiguous continuation), explicit `points: [[x,y], ...]`, basis/change/evidence/tasks. Nonempty labels require `label_position: [center_x, baseline_y]`. A decision has 2–3 distinct labelled exits. Each path segment is horizontal or vertical; rounded elbows are generated from the points. Do not substitute two diagonal endpoints and expect automatic layout.

Structural coordinates are integers divisible by four. Nodes stay within the board with padding and do not overlap. Each connector attaches to a distinct permitted boundary port, at least 12px from another port. Diamond ports are its cardinal vertices. Paths leave outward, do not pass through any node or cross/share another route, and labels sit on opaque masks clear of nodes and routes. Crossings/automatic bridge glyphs are intentionally unsupported: reroute or split a view. At most 9 nodes, 12 edges and 2 highlights per view. These are the adopted design budget, not scientific universals.

Example decision fragment (all referenced IDs must exist in the full report):

```json
{
  "id": "check", "label": "Either score\nnegative?", "note": "",
  "shape": "decision", "x": 512, "y": 320, "width": 256, "height": 160,
  "highlight": true, "basis": "proposed", "change": "modified",
  "evidence": ["E1"], "tasks": ["T2"]
}
```

Basis: observed/inferred/unknown/proposed. Change: unchanged/added/modified/removed. Existing relationships require static/runtime evidence, unknowns require `uncertainty`; that text is surfaced outside collapsed details. Current graphs cannot contain future modifications. Changed future behavior is proposed and task-mapped. Edges need evidence too. A quoted intended behavior does not prove runtime correctness.

Delivery views use `task_id` on task nodes, matching the single task reference, and `precondition: "approval"` on a prerequisite start node. Delivery edges are checked against dependencies among the shown tasks. For a focused subset, declare omitted prerequisite IDs in graph `external_dependencies`; these are displayed below the diagram. Preserve the task dependency set; an approval node describes a required gate, not a completed approval or additional TODO. Do not infer concurrency from two tasks without a dependency. Shared-file ownership remains governed by the workflow.

## Migration from 2.1 / schema 1

Existing HTML remains unchanged and its schema-1 source manifest is still accepted by `--check`. New rendering uses schema 2 only; it does not auto-convert the old component grid into assumed user behavior.

1. Preserve the old reviewed HTML/JSON and authoritative plan revision. Do not overwrite a reviewed artifact.
2. Reuse requirements, evidence, tasks, acceptance, limits and source paths after reconciling freshness. Correct material source ambiguities only through the owner’s decision process.
3. Use the local FLOWCHART-DESIGN.md guide to produce focused views with ids, purpose, explicit positions/shapes/routes, `default_view`, and aligned `comparison`. Remove old `row`/`col`/`group` layout fields; no stale renderer fallback.
4. Save a new presentation revision/path, render and inspect. A presentation-only restyle does not create application approval or require reapproving unchanged application scope already approved. A semantic change does.

## Source of truth, safety and limits

PLAN/TODO/FINDINGS/DECISIONS remain authoritative. Hashes include saved input JSON and all supplied sources, including uncommitted bytes. `--check` detects changes/missing supplied files, not omitted/new files, fabricated evidence, semantic correctness, trustworthy approval or malicious manifest modification. Source paths and report text may be sensitive; sanitize evidence before sharing.

The input is escaped text, not raw HTML/SVG/CSS. No input script/URL is executed. Geometry checks catch common defects; actual browser label measurements and review remain required. Print displays all diagrams; expand required technical details before printing. No PDF export or browser installation is implied. A successful structural check is not a complete accessibility/usability audit or proof of agent obedience.


## Maintaining the approved presentation

The package's tools/visual_regression.py captures the stable bundled fixture and compares screenshots read-only. See package tests/VISUAL-REGRESSION.md for the controlled-environment protocol. These maintenance tools are not required by a standalone map installation; retain existing browser/manual checks when unavailable. Never update an approved screenshot automatically, substitute image equality for semantic review, or claim screenshots establish user comprehension. Keep generated timestamps outside the compared view.

## Durable reviews versus disposable checks

Review HTML/JSON are requested deliverables, not generic test output. Use the project's review-page location or the existing task folder. Preserve every presented/approved revision according to project rules. The renderer refuses existing outputs intentionally: do not bypass that protection or invent another task root. Revise an unpresented draft only when its ownership and the writer's rules allow it.

For optional browser/visual verification, apply the active workflow ARTIFACTS.md/global policy. These tools may require a fresh child directory to avoid overwriting evidence; place it under the stable task output parent. After comparing, preserve approved references and necessary failure/proof images, then remove only the current operation's eligible temporary captures. Do not retain every identical successful comparison or create an extra manifest outside what the test tool actually needs.

## Additive record context (2.6; schema 2 stays valid)

Existing schema-2 input requires no migration or new fields. Existing HTML is never rewritten; schema-1 HTML manifests remain checkable. A new render of schema-1 layout still requires the deliberate layout migration documented above. None of these checks interprets arbitrary Markdown, authenticates decisions or proves agent compliance.

Ordinary approval reviews remain the default. For a specifically requested task-status illustration, set `report_kind: "task-overview"` and supply `checkpoint`. This is a saved projection of the existing task record, not a dashboard to regenerate per checkpoint. It does not ask for new approval or grant implementation authority. Preserve the selected `revision` exactly, even when a legacy review uses another filename/phase alias. The task overview labels the comparison as a historical baseline versus reviewed scope; a flow is not current-implementation evidence just because it is approved. In current-only mode, the inspected flow still needs fresh code evidence.

| Optional field | Meaning and requirements |
|---|---|
| `report_kind` | `review` (default) or `task-overview`. The latter requires a sourced checkpoint; it is not an approval-mode bypass. |
| `checkpoint` | `as_of` (actual known time or explicit unknown), `source` (supplied source ID), `locator` (current record section), `next_action`, and the three state objects below. |
| `checkpoint.approval` | `status`: approved/waived/not-approved/unknown; `revision`: exact covered revision for approved/waived, otherwise null/omitted; `summary`: authority and limits in plain language. An approved report must match this revision and still needs its existing `approval` record/response. |
| `checkpoint.implementation` | `status`: not-started/in-progress/implemented/partial/unknown; `summary`: supported work state and evidence/limitations. |
| `checkpoint.verification` | `status`: not-run/in-progress/blocked/passed/failed/limited/unknown; `summary`: checks and any owner acceptance still outstanding. Passed automated checks alone must not conceal pending owner acceptance. |
| `revision_log` | Ordered array of `revision`, optional `review` alias, `change`, `reason`, `status` (proposed/presented/approved/superseded/rejected/withdrawn/unknown), `source` and `locator`. One row per agreement, presentation aliases in that row. Keep exact identifiers; no automatic sorting by filename or invented missing history. Review aliases are escaped text, not executable URLs. |
| Task `outcome` / `outcome_note` | Optional sourced status: planned/in-progress/implemented/verified/blocked/removed/superseded/not-applicable/unknown. A note explaining the evidence or owner decision is required. Removed/superseded work is labelled as not a passed test. Without a status, the task is only a scope description, not a completion claim. |

Use the existing PLAN checkpoint, or established STATUS.md in a legacy task. Keep the revision log in existing PLAN/DECISIONS (or existing legacy equivalent). Do not create a JSON state file or new Markdown file to feed this feature. Generate the requested report input from those records; no competing task database or duplicate handwritten history.

[The task-overview example](examples/task-overview.json) adds context to the unchanged synthetic flowchart. Its legacy [STATUS.md](examples/STATUS.md) is deliberately separate from the older pending review. It demonstrates a later recorded fixture approval without altering the old HTML. It is not real user approval or runtime evidence.

The renderer continues exclusive creation. Do not bypass an existing-output refusal to edit a presented/approved snapshot, or create retry-named reports automatically. An unpresented draft may be replaced only through explicitly authorised ownership-safe operations; a saved overview remains an as-of snapshot. Normal progress belongs in the task record/chat, not more HTML files.

A source hash change after a checkpoint update does not by itself invalidate unchanged approved scope. `--check` only reports byte differences; the agent must distinguish expected progress, material changes and missing authority. Keep presented history intact and ask only about genuinely unresolved authority.
