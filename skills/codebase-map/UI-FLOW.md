# Screen flows inside the existing report

This is an optional extension of schema 2, not a new template. Keep report.css, report.js, the header, comparison, boundaries, task list, acceptance, approval and technical evidence. Non-UI reports render as before. Use `ui_review` only when actual UI is in scope or the owner explicitly requests a labeled illustration. The latter never becomes a requirement of the original task.

## Before rendering

Use local ui-design to establish the task source, mode, any preview environment permission and meaningful interaction choices. Reuse an explicit task choice or valid same-task record; otherwise ask before choosing the design. A project DESIGN.md is evidence to inspect, not automatic selection. No kit is not automatic permission for plain application HTML. Preview authoring does not permit implementation.

## Kit screens (the default when the project has a design kit)

When the project has a design kit page (Blade, Angular/Ionic, React or any other stack that renders in a browser), show the current **and** proposed screens as **kit screens**: real kit markup with the kit's own styles, live in the report. Problems in layout, spacing and wording are visible at once; a sketch hides them.

1. **Get the developer's local kit address.** Ask for it ("What is the address of the design kit on your local site?") unless the task records already name it for this session. Every developer's setup differs: never guess one, and never write the address into the repository, DESIGN.md or the report. Starting their dev server is theirs to do unless the project's rules let you.
2. **Save the rendered kit page** into the task's output folder (ARTIFACTS.md) inside the repository: `python -X utf8 scripts/kit_snapshot.py <kit-url> [<kit-url> ...] <out>/kit-snapshot.html --width <px>`, with the width the app is used at: 1280 for a desktop admin, 390 for a phone app. The report shows the screens at that width. It uses the installed Edge or Chrome through Python Playwright, blocks every request to another site, and writes one script-free file: the rendered elements (shadow roots included), the stylesheets and the fonts actually used. A kit that shows one example or category at a time takes the address of each example the screens need; capture only those, so the report stays under 8 MiB. An example the kit shows only after a click (a page preview, an open dialog) is captured with `--click '<selector>'`, for example `--click 'text=Open page preview'`. Read the printed summary: a font or image over budget is named there; say so under the screen.
3. **Compose each screen** as a small `.html` file holding only body markup: copy the kit elements the screen needs **whole** out of the snapshot (tag, every class, inline style, wrappers and any `<template shadowrootmode="open">` inside them, keeping its first line `<style data-kit-shadow-ref="…"></style>`: that is the component's own style, and the renderer refuses a copy without it), then change only the fake text. Build **every** screen of the flow this way, current and proposed, including menus, headers and dialogs the kit shows; the current one is rebuilt from kit parts with fake data, never saved from the real page. Put them in the task folder (`screens/<name>.html`) so the plan keeps them.
4. **Reference them** in the report: sources with role `kit-snapshot` (the saved page) and `kit-screen` (each composed file), and on each screen `"representation": "kit", "kit_snapshot": "<source id>", "kit_markup": "<source id>"` instead of `content` or `capture`.

The renderer refuses a kit screen that uses any tag, class, inline style or image that is not in the snapshot, and names each one. Never add it to make the check pass: ask the owner "I couldn't find a matching style for [element]. Is there an existing element I should mimic?" A `<style>` with CSS, a script, an event handler or a link is refused too.

In the report each kit screen is a scaled live frame in the flow (Inspect opens it at full size, at the snapshot width). Frames run **no scripts**: menus, toggles and popups show the state the copied kit example shows (the kit shows states open), so copy the example in the state the screen needs. Only inlined fonts and Typekit may load (Typekit also requests its own `p.typekit.net` stylesheet when the report opens). The page's own stylesheets stay inside the frame; the report shell is unchanged.

Use a sketch (below) only when there is no kit, the kit page cannot be reached, Playwright for Python or a browser is missing, or the kit has no example of that part of the screen. A sketch next to kit screens needs `sketch_reason` naming the missing kit part (the owner sees it); say the rest in `preview.summary`. Never install anything to avoid the sketch.

## Captures and sketches

Capture the current screen as an authorized PNG when it can be opened safely (a local static page: `scripts/screenshot_report.py`); use its narrow (500px) image for a screen card, because a full-width page shrinks to unreadable size there. Obtain them only through allowed tooling and safe sample data; no browser, app build, server, credentials or paid service starts merely because the renderer needs an image. Name source/kit revision, capture context and limits in the supplied records. Do not stretch or crop away important errors, states or controls. Report a capture as appearance only, never as evidence of behavior or device performance.

When neither a kit screen nor a real capture can be made safely, use the structured **schematic** (layout sketch) built only from the reused elements; every UI-visible change needs one of the three. The report labels it “Sketch · not a screenshot”. It is not a styled prototype or proof of the kit's look. Legacy approved-kit work without real captures stays blocked; other authorized work can continue.

## Fast source-backed styled previews (optional)

When the owner wants to **see the real existing styling** without authoring a prototype, add `ui_review.quick_previews` to the **same schema-2 projection**. The report renders a compact gallery plus **expandable full-size frames**; larger/multiple changes do not need to fit in the flowchart's little screen cards. This is a separate visual reference underneath the screen flow, not another implementation or approval gate.

Each item is exactly:

```json
{"id":"save-card","title":"Existing save card","html_source":"UI_HTML","selector":".save-card","css_sources":["UI_CSS"],"note":"Current component style; future wiring described in T2."}
```

Declare `UI_HTML` and `UI_CSS` in the report's existing `sources`. `html_source` must be an **existing local .html example/template**. `selector` supports `#id`, `.class`, `tag.class` or `tag#id` and selects the complete subtree, including its wrapper when that wrapper is selected. `css_sources` are **existing compiled `.css` files**, not SCSS source files or invented styles. Choose only the needed CSS; no installation, new page, app runtime or screenshots are required. A report-only 20px body padding improves legibility; it never alters application styles.

The renderer sanitizes source markup into inert elements (removes event handlers, links, media and executable tags), isolates the real CSS in a sandboxed `srcdoc` iframe with no network/script/form permission, fingerprints all supplied sources and keeps historical reports immutable. These are **static HTML/CSS samples**: Angular/Ionic/React components needing framework execution, runtime state, compiled SCSS, generated classes, external fonts/images or layout depending on absent ancestors can look incomplete. Label those limits; use a genuine captured screenshot or the project's existing preview when fidelity matters. Never invent markup or add a second style source to force a preview. If the required sources are unavailable, skip this gallery and retain the existing schematic/capture plus references; don't block the whole planning task merely for a sample.

Use up to six small examples; group by component or interaction rather than adding full page copies. The small frame shows context; "Expand full-size sample" provides a scrollable larger view. The screen flow and source/decision mapping remain unchanged. Report page sizes stay bounded by the existing 8 MiB check.

## Projection

See the complete [report example](examples/ui-review/review-r2.json) and [example notes](examples/ui-review/README.md). Keep existing schema-2 fields. The optional `ui_review` contains:

- `kind`: `application` for the actual task, or `illustration` for a separately labeled demonstration outside the original implementation scope.
- `title`, `summary`, `limit`, `mode`: `behaviour-only` / `reuse` / `plain-by-instruction` (current), `unselected` / `blocked` (not approval-ready), legacy `approved-kit`, `functionality-only`, `design-authoring` (historical; ui-design CONTRACT.md maps them). An `application` review always opens on the screen diagram; `open_first` only applies to illustrations.
- `authority`: `status` confirmed/unconfirmed, source ID, locator, summary identifying task selection.
- `preview`: proposed/authorised status, source ID, locator, summary and destination/access boundary.
- `acceptance`: pending/accepted and summary; accepted also needs an actual supplied source and locator. Release readiness is not inferred.
- `quick_previews` (optional): source-backed static HTML/CSS fragments, as described above. Not the complete proposed page.
- `screens`: up to six with `id`, title, description, current/proposed state, x/y/width/height, `sources`, requirement/evidence/task IDs and decision IDs. They are source-backed projections, not independent specifications.
- `representation`: `kit` plus `kit_snapshot` and `kit_markup` source IDs (roles `kit-snapshot` and `kit-screen`, see "Kit screens"), `capture` plus `capture` source ID (role `ui-capture`, local static PNG), or `schematic` plus structured `content` entries. Schematic entries allow only heading/text/checkbox/input/button/message, plain label, optional value/boolean flags and decision ID. No raw HTML, arbitrary styles, event handlers, CSS classes, URLs or scripts in schematic controls; only the optional source-backed quick-preview extractor can show existing classes. Native-looking drawings are explicitly approximate, not actual browser controls.
- Captured screens can add `markers` with a mapped decision ID and `position: [xFraction, yFraction]` on the original image (0–1). Their full-size details preserve the uncropped source.
- `transitions`: from/to IDs, short action/outcome label, explicit orthogonal points and label position. Reuse the existing validated connector conventions. Screen boundaries must not be crossed.
- `decisions`: ID/title/question, two to four options, screen IDs, status open/selected/deferred. Selected choices require selection and source/locator/summary. Deferred choices state the reason and remain pending; they do not permit styling.

- `elements` (no `kit_binding`): one to twenty existing elements the screen copies, each exactly `{id, source, locator, tag, classes, context, changes}`: a supplied source ID, its `file:line`, the tag, the class list (empty when it has none), the wrapper it needs to look the same (`"inside div.dashboard-info-line-chip"`, or `"none: no rule needs context"`; ui-design `scripts/class_rules.py` lists the rules) and the content or wiring change. Required on every proposed screen in `reuse` mode. With a legacy `kit_binding`, use the strict kit fields below instead.
  Keep the source tag/component identifier, such as `ion-chip`, `SwatchTile` or `Form.Group`; do not replace a framework component with an inferred DOM tag to satisfy validation. This is an escaped reference, not executable markup or automatic source verification.

Coordinates use the same 4px grid and maximum 1600×1600 board as normal flows, but keep a screen board at most 1160px wide (two or three screens of 280–360px per row; wrap a longer flow to a second row) so a laptop window shows every screen without sideways scrolling. Screens are 280–560px wide and 280–720px high. Avoid miniaturizing text to fit; split larger flows into a meaningful reviewed subset and explain omitted paths. Sketches have at most six rows; a sketch screen is at least 120 + 48 × rows px high; labels and values are single-line and at most 42 characters, and about 7px per character (9 for headings) must fit the screen width less 48px. The checker reports every screen's problems in one run; fix them all before rendering again. Every decision maps to its affected screens. The viewer provides enlarged source/details links, not application actions.

## Approval

A proposed screen drawn as a labeled sketch inside this offline report needs no permission: never ask for it, and set `preview.status: not-needed` (its source and locator name where the report is saved), not `authorised`. A proposed screen *captured* from a running preview needs recorded preview authority (`preview.status: authorised`). A UI-visible change without a screen diagram keeps the report a draft. Legacy approved-kit mode always needs actual captures, never a lookalike schematic. A recorded accepted design cannot retain an unselected source or unresolved design choices.

For actual application UI, awaiting-approval requires a current mode, confirmed authority, `preview.status: authorised` for a captured proposed screen (otherwise `not-needed`), the copied elements for `reuse` screens and no open material UI decisions. A behaviour-only repair preserving existing UI can use the normal report without adding a proposed screen view; do not manufacture a kit or redesign merely to report that repair. See the strict reference fields below.

A standalone visual request stops after delivery. The owning workflow records real approval in the existing task documents. Viewer links, zoom, option exploration and opening a page do not approve work. No approve button, model callback, telemetry, network fetch or application endpoint is added.

## Safety, output and compatibility

The complete report is still offline. Static PNGs are bounded, structurally checked and embedded as data; no arbitrary SVG/HTML uploads execute. Per-image limit 2 MB, total captures 4 MB, whole report 8 MiB. Use reviewed, sanitized captures; the renderer does not scrub personal information from pixels. PNG sources participate in the same freshness manifest as plans and code. Image tags are enabled only for this data-only extension.

Old saved HTML remains unchanged, and non-UI or historical/draft input remains readable. New application-approval UI inputs require the fields below and the complete renderer; older renderers may ignore fields, so verify the selected-element details and current tool version rather than assuming forward support. Presented reports are never overwritten. Render the new projection only when the plan/review actually changes, preserving the task and approved history. This feature adds no new UI manifest or separate prototype app.

Inspect default/zoom/Fit, source links, keyboard access, small screens, long labels, image aspect ratio and missing images. Browser checks verify structure/interaction; human design acceptance and live host behavior remain separate. Without JavaScript, radio tabs, readable native-size scrolling and native details remain available; UI Fit requires the optional viewer enhancement.

## Reused elements

Application UI follows rule-maker DESIGN.md. Current modes and the `elements` list are described above; `functionality-only` and `design-authoring` are retained only for historical/draft compatibility, not new implementation authority.

A **legacy** `approved-kit` report (a project catalog bound with `kit_binding`) in `awaiting-approval`/`approved`, or claiming accepted design, needs real captures and these additional data-only fields:

- `ui_review.kit_binding`: `{ "source": "KIT", "scope": "src/settings" }`. The source is the selected local catalog using ui-design/CATALOGUE.md's JSON profile. For an authoritative Markdown or other local catalog, add `projection` containing the same schema-1 catalog structure inside this existing report input; keep `source` pointing to that actual record. This is a generated projection, not another maintained file or a requirement to migrate the project catalog. Review semantic correspondence; the checker cannot derive it from prose.
- Each screen's `elements`: one to twenty objects with exactly `id`, `item`, `role`, `variant`, `state`, `example_source`, `example_locator`, `changes`. `item` must resolve to the chosen kit; variant/state must be declared (use literal `not-applicable` only when the entry has no such options). `example_source` identifies a supplied actual example covered by that entry's sources. `changes` explains content/event wiring, not permission to style. Include the approved composition pattern, not only individual controls.
- Each captured screen's `capture_context`: `source`, `locator`, `summary`, `capture_sha256`, `inputs`. Reference the existing findings/evidence, explain environment/viewport/brand and limitations, and list `{path, sha256}` for the source inputs used in that capture. Include selected components, examples, theme and listed transitive dependencies; extra actual input references are allowed. No additional capture-record file is required. A source hash change must not be “fixed” by rewriting the capture's recorded inputs without recapture/evidence.
- A capture marker can use `{ "element": "E1", "position": [0.5, 0.4] }` to open that exact element row. Existing decision markers remain supported. IDs are scoped per screen.

**Inspect screen** shows exactly which entry, variant/state, example, component source and intended change is selected. Labels distinguish captures from missing provenance; checked source references are not proof that a component actually produced the screenshot. Verify the rendering evidence and actual human decision. The renderer rejects missing/deleted/stale/out-of-scope or unapproved selected inputs and unknown variants. It snapshots listed kit dependencies for future `--check`.

Legacy/draft schematic examples remain readable and visibly non-authoritative. A layout sketch is drawn only from reused elements and never stands in for a capture the legacy kit mode requires; no styled mockups. No source badge grants application implementation or release permission.
