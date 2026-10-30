# Screen flows inside the existing report

This is an optional extension of schema 2, not a new template. Keep report.css, report.js, the header, comparison, boundaries, task list, acceptance, approval and technical evidence. Non-UI reports render as before. Use `ui_review` only when actual UI is in scope or the owner explicitly requests a labelled illustration. The latter never becomes a requirement of the original task.

## Before rendering

Use local ui-design to establish the task source, mode, preview permission and meaningful interaction choices. Reuse an explicit task choice or valid same-task record; otherwise ask before choosing the design. A project DESIGN.md is evidence to inspect, not automatic selection. No kit is not automatic permission for plain application HTML. Preview authoring does not permit implementation.

For an approved kit, show authorised PNG captures of the actual components in the relevant states. Obtain them only through allowed tooling and safe sample data; no browser, app build, server, credentials or paid service starts merely because the renderer needs an image. Name source/kit revision, capture context and limits in the supplied records. A static capture shows appearance, not verified behaviour or responsive/device performance. Do not stretch or crop away important errors, states or controls.

When there is no capture or approved appearance, use an explicitly authorised **schematic** only as a proposed layout. The report labels it “Layout sketch — not a component capture”. It is not a styled prototype or proof of the kit's look. Missing required kit captures keep approval-ready approved-kit work blocked; other authorised work can continue.

## Projection

See the complete [report example](examples/ui-review/review-r2.json) and [example notes](examples/ui-review/README.md). Keep existing schema-2 fields. The optional `ui_review` contains:

- `kind`: `application` for the actual task, or `illustration` for a separately labelled demonstration outside the original implementation scope.
- `title`, `summary`, `limit`, `mode`: `unselected` / `functionality-only` / `approved-kit` / `design-authoring`; `open_first` optionally selects the UI tab on initial viewing. Non-UI default behaviour is unchanged.
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

For actual application UI, awaiting-approval requires confirmed mode/source, an authorised preview location and no open material UI decisions. Functionality-only can be approved with final visual design explicitly deferred; it cannot silently become a public release. Approved-kit review requires real captures, not a claimed exact schematic. Design-authoring previews remain proposals until the named design revision is accepted.

A standalone visual request stops after delivery. The owning workflow records real approval in the existing task documents. Viewer links, zoom, option exploration and opening a page do not approve work. No approve button, model callback, telemetry, network fetch or application endpoint is added.

## Safety, output and compatibility

The complete report is still offline. Static PNGs are bounded, structurally checked and embedded as data; no arbitrary SVG/HTML uploads execute. Per-image limit 2 MB, total captures 4 MB, whole report 8 MiB. Use reviewed, sanitised captures; the renderer does not scrub personal information from pixels. PNG sources participate in the same freshness manifest as plans and code. Image tags are enabled only for this data-only extension.

Old inputs need no new fields; old saved HTML remains unchanged. UI projections require the full rc.6 renderer: older renderers may ignore this optional extension, so verify the UI screens tab is present rather than assuming forward support. Presented reports are never overwritten. Render the new projection only when the plan/review actually changes, preserving the task and approved history. This feature adds no new UI manifest or separate prototype app.

Inspect default/zoom/Fit, source links, keyboard access, small screens, long labels, image aspect ratio and missing images. Browser checks verify structure/interaction; human design acceptance and live host behaviour remain separate. Without JavaScript, radio tabs, readable native-size scrolling and native details remain available; UI Fit requires the optional viewer enhancement.
