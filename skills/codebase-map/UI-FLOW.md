# Screen flows inside the existing report

This is an optional extension of schema 2, not a new template. Keep report.css, report.js, the header, comparison, boundaries, task list, acceptance, approval and technical evidence. Non-UI reports render as before. Use `ui_review` only when actual UI is in scope or the owner explicitly requests a labelled illustration. The latter never becomes a requirement of the original task.

## Before rendering

Use local ui-design to establish the task source, mode, preview permission and meaningful interaction choices. Reuse an explicit task choice or valid same-task record; otherwise ask before choosing the design. A project DESIGN.md is evidence to inspect, not automatic selection. No kit is not automatic permission for plain application HTML. Preview authoring does not permit implementation.

For an approved kit, show authorised PNG captures of the actual components in the relevant states. Obtain them only through allowed tooling and safe sample data; no browser, app build, server, credentials or paid service starts merely because the renderer needs an image. Name source/kit revision, capture context and limits in the supplied records. A static capture shows appearance, not verified behaviour or responsive/device performance. Do not stretch or crop away important errors, states or controls.

For historical/draft demonstrations, the renderer retains structured **schematic** support; it is not a permitted fallback for new application UI work. The report labels it “Layout sketch — not a component capture”. It is not a styled prototype or proof of the kit's look. Missing required kit captures keep approval-ready approved-kit work blocked; other authorised work can continue.

## Projection

See the complete [report example](examples/ui-review/review-r2.json) and [example notes](examples/ui-review/README.md). Keep existing schema-2 fields. The optional `ui_review` contains:

- `kind`: `application` for the actual task, or `illustration` for a separately labelled demonstration outside the original implementation scope.
- `title`, `summary`, `limit`, `mode`: `unselected` / `blocked` / `behaviour-only` / `approved-kit` (legacy `functionality-only` and `design-authoring` are historical/draft only); `open_first` optionally selects the UI tab on initial viewing. Non-UI default behaviour is unchanged.
- `authority`: `status` confirmed/unconfirmed, source ID, locator, summary identifying task selection.
- `preview`: proposed/authorised status, source ID, locator, summary and destination/access boundary.
- `acceptance`: pending/accepted and summary; accepted also needs an actual supplied source and locator. Structure checking never authenticates consent. Release readiness is not inferred.
- `screens`: up to six with `id`, title, description, current/proposed state, x/y/width/height, `sources`, requirement/evidence/task IDs and decision IDs. They are source-backed projections, not independent specifications.
- `representation`: `capture` plus `capture` source ID (role `ui-capture`, local static PNG), or `schematic` plus structured `content` entries. Schematic entries allow only heading/text/checkbox/input/button/message, plain label, optional value/boolean flags and decision ID. No raw HTML, arbitrary styles, event handlers, CSS classes, URLs or scripts. Native-looking drawings are explicitly approximate, not actual browser controls.
- Captured screens can add `markers` with a mapped decision ID and `position: [xFraction, yFraction]` on the original image (0–1). Their full-size details preserve the uncropped source.
- `transitions`: from/to IDs, short action/outcome label, explicit orthogonal points and label position. Reuse the existing validated connector conventions. Screen boundaries must not be crossed.
- `decisions`: ID/title/question, two to four options, screen IDs, status open/selected/deferred. Selected choices require selection and source/locator/summary. Deferred choices state the reason and remain pending; they do not permit styling.

Coordinates use the same 4px grid and maximum 1600×1600 board as normal flows. Screens are 280–560px wide and 280–720px high. Avoid miniaturising text to fit; split larger flows into a meaningful reviewed subset and explain omitted paths. Sketches have at most six rows and must have room for their labels. Every decision maps to its affected screens. The viewer provides enlarged source/details links, not application actions.

## Approval

Proposed screen drawings require explicit preview permission even in draft reports. Without it, omit the screen view and surface the missing choice in the normal report. Approved-kit mode always needs actual captures, never a lookalike schematic. A recorded accepted design cannot retain an unselected source or unresolved design choices.

For actual application UI, awaiting-approval requires confirmed approved-kit selection, an authorised preview location, exact element/pattern references and no open material UI decisions. There is no new functionality-only/plain-markup or design-authoring approval route. A behaviour-only repair preserving existing UI can use the normal report without adding a proposed screen view; do not manufacture a kit or redesign merely to report that repair. See the strict reference fields below.

A standalone visual request stops after delivery. The owning workflow records real approval in the existing task documents. Viewer links, zoom, option exploration and opening a page do not approve work. No approve button, model callback, telemetry, network fetch or application endpoint is added.

## Safety, output and compatibility

The complete report is still offline. Static PNGs are bounded, structurally checked and embedded as data; no arbitrary SVG/HTML uploads execute. Per-image limit 2 MB, total captures 4 MB, whole report 8 MiB. Use reviewed, sanitised captures; the renderer does not scrub personal information from pixels. PNG sources participate in the same freshness manifest as plans and code. Image tags are enabled only for this data-only extension.

Old saved HTML remains unchanged, and non-UI or historical/draft input remains readable. New application-approval UI inputs require the rc.7 fields below and the complete renderer; older renderers may ignore fields, so verify the selected-element details and current tool version rather than assuming forward support. Presented reports are never overwritten. Render the new projection only when the plan/review actually changes, preserving the task and approved history. This feature adds no new UI manifest or separate prototype app.

Inspect default/zoom/Fit, source links, keyboard access, small screens, long labels, image aspect ratio and missing images. Browser checks verify structure/interaction; human design acceptance and live host behaviour remain separate. Without JavaScript, radio tabs, readable native-size scrolling and native details remain available; UI Fit requires the optional viewer enhancement.

## Strict kit references for new application approvals (rc.7)

The existing shell, styles, diagrams, source sections and viewer remain unchanged. Application UI now follows strict kit reuse: no agent-authored HTML/CSS/inline-style fallback. `behaviour-only` and `blocked` are accepted mode labels; `functionality-only` and `design-authoring` are retained only for historical/draft compatibility, not new implementation authority.

A newly generated application UI report in `awaiting-approval`/`approved`, or claiming accepted design, requires `approved-kit`, real captures and these additional data-only fields:

- `ui_review.kit_binding`: `{ "source": "KIT", "scope": "src/settings" }`. The source is the selected local catalogue using ui-design/CATALOGUE.md's JSON profile. A catalogue's status does not authenticate consent. For an authoritative Markdown or other local catalogue, add `projection` containing the same schema-1 catalogue structure inside this existing report input; keep `source` pointing to that actual record. This is a generated projection, not another maintained file or a requirement to migrate the project catalogue. Review semantic correspondence; the checker cannot derive it from prose.
- Each screen's `elements`: one to twenty objects with exactly `id`, `item`, `role`, `variant`, `state`, `example_source`, `example_locator`, `changes`. `item` must resolve to the chosen kit; variant/state must be declared (use literal `not-applicable` only when the entry has no such options). `example_source` identifies a supplied actual example covered by that entry's sources. `changes` explains content/event wiring, not permission to style. Include the approved composition pattern, not only individual controls.
- Each captured screen's `capture_context`: `source`, `locator`, `summary`, `capture_sha256`, `inputs`. Reference the existing findings/evidence, explain environment/viewport/brand and limitations, and list `{path, sha256}` for the source inputs used in that capture. Include selected components, examples, theme and listed transitive dependencies; extra actual input references are allowed. No additional capture-record file is required. A source hash change must not be “fixed” by rewriting the capture's recorded inputs without recapture/evidence.
- A capture marker can use `{ "element": "E1", "position": [0.5, 0.4] }` to open that exact element row. Existing decision markers remain supported. IDs are scoped per screen.

**Inspect screen** shows exactly which entry, variant/state, example, component source and intended change is selected. Labels distinguish captures from missing provenance; checked source references are not proof that a component actually produced the screenshot. Verify the rendering evidence and actual human decision. The renderer rejects missing/deleted/stale/out-of-scope or unapproved selected inputs and unknown variants. It snapshots listed kit dependencies for future `--check`; it does not discover every dynamic dependency or perform runtime tests.

Existing historical HTML is never rewritten. Legacy/draft schematic examples remain readable and visibly non-authoritative. No new application layout sketches or styled mockups are invented to replace missing captures. No source badge grants application implementation or release permission.
