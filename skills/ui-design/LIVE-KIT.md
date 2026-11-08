# One code-backed catalogue, not copied UI

A kit is a project-local preview of **the actual framework components and approved patterns**. React renders its React components; Angular/Ionic renders its components. The workflow report is a saved projection/capture, not another implementation of those controls. Existing project sources are required; this package contains no project kit and installs no preview tools.

## Single sources

| Information | Authoritative location |
|---|---|
| Current appearance/behaviour | Real component, styles/theme and dependencies. |
| Examples, variants and states | Existing adjacent framework stories/tests/examples importing the component. |
| Current catalogue/reference inventory | Generated from that code/examples through existing approved tooling. |
| Purpose, approved scope and exceptions | One designated approval/usage record; human decisions are not inferred from code. |
| Project entry point | A short pointer in current project instructions or DESIGN.md, not a copied CSS/property list. |
| Historical task review | The presented report and captured sources, preserved unchanged. |

Rebuilding/reloading the existing catalogue reflects component changes. A new input/state may require changing the adjacent example or test. Do not promise that human approval or intended use regenerates itself. An automatically generated index may still be stale; inspect the actual checkout and required source/preview checks.

## Setup sequence through ui-design

1. `kit-audit <area>` finds designated real components, the application's development route and build-mode mechanisms, existing preview tooling and authority. Search is inventory, not approval. No installation, routes, builds or captures without permission.
2. `kit-setup <area>` proposes the development kit route (next section), the page anatomy and coverage check below, a DESIGN.md shaped by `templates/DESIGN.md` when the project has no equivalent record, and safe preview/verification. Setup is not application implementation approval. After approval, normal execution may add the minimum framework example and registration that render real components or mirror existing tags, classes and wrappers. A missing example alone is not a designer blocker. New visual designs, styling, dependencies or custom preview infrastructure remain outside that reuse scope; name the specific gap before dependent work. Do not install a tool merely to satisfy this skill.
3. `kit-check <catalogue>` checks selected sources/scope. A Markdown catalogue remains valid; do not force conversion. If a JSON profile is used, it is a generated projection or the sole existing catalogue, not another independently maintained truth source.
4. Check claimed variants against their renderer and real callers, including host wrappers/styles. A declared type or enum is not proof of a working example. Identify absent, inert and context-dependent variants in the plan before approval; preserve distinct existing variants. Record exact selections in the existing task, generate the existing review with captured screens and per-element references, obtain normal approval, then wire only selected supported component APIs.

## Development access and production exclusion

The default kit is **one development-only page inside the real application**, for example `/design-kit`. Register it only in development builds or environments, outside authentication guards and account initialization, and render it inside the application's real layout, providers and global styles with local synthetic data, without starting production services. Each application or client build has one kit: a client build's kit includes that client's overrides and enabled modules. Use a separate preview server only when the framework cannot host a development route, and state that reason in the setup proposal. Do not build a fake login or require customer credentials to inspect a kit.

Use the framework's existing build-mode and route mechanisms to omit preview registration and preview-only imports from production. Hiding a menu item, checking a user role, or redirecting after importing the kit is insufficient. Shared production components remain shared; exclude the preview entry and its sample data. Treat unknown build mode as unavailable. Do not add a dependency or a second design system for this boundary.

Trace route parents, providers, imports and every supported production configuration during audit. Include access/exclusion in the implementation plan and checks: a fresh logged-out development browser opens the kit with backend requests blocked; direct production URLs cannot open it; production output contains no preview entry or synthetic sample data. Builds still require the project's authorization. Missing runtime/build evidence stays unverified. Existing authenticated or production-reachable previews require a scoped route revision, not an authentication workaround.

## Page anatomy and coverage

The kit page follows design.md like any other screen: existing classes and components only.

- **One page, grouped by element type.** Components and repeated elements appear one under another on a single page, grouped by what they are (for example actions, forms, lists, overlays, feedback, icons, layout), never by owner, module or page. A module's or client's own components and elements sit in the same groups as core ones. No per-client or per-module sections or tabs, no whole-page sub-pages or framed page previews, and no separate index page. A view with its own layout (login, public upload) contributes its elements to the groups; email and PDF views are not screen UI and are excluded with that reason.
- **One example per component and per repeated pattern.** A repeated wrapper, block, row, grid or text helper gets its own example with its own title. The title names the element (`Dashboard tile`, `Content list`), never a module, client or page (`Intervat dashboard blocks`); one icons example covers every icon, whoever uses it. Never fold several patterns into one bulk caption. A part used only inside one parent (a modal header, a tile's title, a tab link) is labelled inside that parent's example with its own class label, never given an example that repeats the parent; it gets its own example only when it is also used on its own elsewhere.
- **Each example defines its pattern, in one block:** a title; one short definition line naming where it comes from (the component and its props or slots, or the stylesheet that owns the classes) and the base `tag.class` with its modifier classes, nothing else: no caller lists, line numbers, findings or notes (those go in the task's FINDINGS); then every variant and state rendered inside its real wrappers, each with a small label beside it naming its exact classes or props (for example `main-btn dark-btn`, `disabled`). The reader sees which class gives which look without opening the code. Interactions give local, visible feedback on the page.
- **Tokens and icons come first:** colours, type, spacing and similar values read from the running stylesheet (never copied into the page). Each colour token shows a swatch of its colour beside its name when an existing element can show one without CSS; otherwise its name and value. Each icon class used in the views is rendered on its own, with its glyph and its exact class as its label (`i.fal.fa-check`), never a sentence listing icon names; an alias of another icon still shows its own glyph, never an empty slot.
- **Labels are classes or props, not prose:** a label is the variant's exact class list or props (`button.btn.l-btn`, `:readonly="true"`, `direction="inbound"`), never a description such as "nothing selected" or "opens on click". Reasons, sources and notes belong in the definition line or nowhere. Each label sits directly under its own variant, grouped with it in one existing wrapper, so it is visibly closer to its own variant than to the next one, framed variants (cards, lists, dialogs, toasts) included.
- **Elements, not pages:** a page shell or page template contributes its inner elements as separate examples; never render a whole page, layout or dashboard as one example. Every state an element has is shown as its own variant: list its state classes from its stylesheet (for example `.btn-loading`, `.selectric-open`, `.active`, `.is-invalid`) and render each, open states included; an active or selected item sits among its real siblings. Third-party widgets show their open interface (a date picker's calendar, a cropper's crop editor, not only its preview), or that state is excluded with its reason. Nothing extra sits beside a variant unless its label names it. Concretely: dropdowns, multi-selects, menus, croppers and loading states render open or active, never closed with a note that they open on click. Variants of one example share the same real wrapper. Overlays (modals, dialogs, menus) are rendered open with their real markup, filled with fake content (no empty list body or half-empty dialog), placed in the page flow as their own example: their content markup in its real wrappers, not a trigger button only, and never by opening the real overlay with its script and copying it. Nothing on the kit page may sit fixed or sticky over other content at any moment, page load included: no open backdrop, no overlay over the app header or top bar. If an element's real classes make it cover other content, show it in a state or wrapper where it cannot; if no existing class allows that, exclude it with that reason.
- **Everything renders correctly:** every example shows visible, styled output with realistic fake text, short enough that nothing is cut off or runs into its neighbour at the kit's width. No empty example or empty value cell, no raw translation keys (`Laravel::...`) anywhere in the page markup (hidden dialogs included), no framework placeholder text, no unstyled element, no clipped or overflowing element. A note in a definition line never excuses a defect: fix it, or exclude the element with its reason. An element that needs a stylesheet the kit's layout does not load gets that stylesheet; if loading it would restyle the rest of the page, the element is excluded with that reason instead of shown broken. One example per pattern: no duplicates across groups.
- **Server-dependent components render as on their real page:** with fixture data, and with the stylesheets and scripts the real page loads for them, while backend requests stay blocked. Mark only what genuinely cannot render, such as a native-only control, with a visible reason on the page.

This anatomy overrides earlier kit decisions: when an older task or approved plan recorded tabs, an example picker, one example at a time, a coverage or index page, full-page previews or a separate preview server, start a new kit task and reopen those decisions under this anatomy instead of carrying them forward. Coverage is the generated test, never a page or category. A reference kit the owner points to (for example another project's kit) shows how each element is defined: copy its definition line, class labels, variants and DESIGN.md sections. Never copy its navigation: tabs, an example picker, one-example-at-a-time views or full-page previews become this one stacked page. Before building the rest, compare one finished example against this anatomy and the reference.

**Coverage rule:** every component, and every element pattern (tag plus full class list) used two or more times in the application's views and its enabled modules' views, appears on the kit page or is listed with a reason in an exclusion list kept beside the kit's examples. A project test generated from the views (not a page) fails on any uncovered pattern without an exclusion. Keep it out of DESIGN.md and never maintain it by hand. Coverage shows presence in the kit, not approval: new and uncovered patterns are candidates for the owner.

**Done when** checked against the served application, not only the source:

- The served build contains the current sources the kit renders (components, module views, layouts). A stale build is a setup gap: update it with the project's own sync tooling, or report it before claiming results.
- The kit page opens logged out in a real browser with no server error, no console error and no request to an outside host except owner-allowed ones (for example a font service). Real components that load third-party scripts or CDN modules get a local stand-in or a visible reason, never a live outside request.
- Every action that would write (delete, save, submit) is stopped or answered with fixture data, so the kit can never change real data.
- In the production configuration the kit route does not exist, checked with the framework's own route listing or a request.
- A full-page visual review, done before claiming results: screenshot the whole page top to bottom in consecutive segments with no gaps (step by the viewport height minus any fixed header, so no strip hides under it), plus the first seconds after a fresh load. Give the reviewer this anatomy section as its checklist, and split a long page so each reviewer sees at most about 50 segments, look at every segment, and fix every breach of the anatomy above (prose labels, bulk lists, whole pages, empty or trigger-only examples, broken or unstyled rendering, leaked keys, escaping sticky bars, duplicates). Prefer a reviewer that did not build the page. Repeat until a full pass finds none.
- Each application's or client's DESIGN.md follows `templates/DESIGN.md` section by section, with the usage decisions drafted from real callers and marked as candidates until the owner approves them. How the kit page is built and how coverage runs belong in the kit's own source comments or the project's AGENTS.md pointer, not in place of those sections.

## Optional read-only Storybook index adapter

For an already generated local v4/v5 `index.json`:

```bash
python -X utf8 skills/ui-design/scripts/inspect_kit_index.py --root /path/to/project --index path/to/index.json
python -X utf8 skills/ui-design/scripts/inspect_kit_index.py --root /path/to/project --index path/to/index.json --story buttons-primary--loading --catalogue path/to/kit.json --item primary-button --scope src/settings
```

It returns current story IDs/labels, local source existence/fingerprints and preview reference suffixes on stdout. With `--previous` it lists added/removed/changed index metadata; that older input must already exist. No output files, network, source execution or plugin installation. A story selection bound to the optional existing catalogue checks the entry and its dependencies/scope; the story source must be among its declared sources. Unknown formats, virtual import paths or missing files require review, not guessed resolution. The index is not a dependency parser: a deleted export inside an existing file or a broken component import requires actual project compilation/story checks. Tags never establish approval.

Use the project's existing dev/build verification process to generate/validate its catalogue. The workflow does **not** automatically wire this adapter into an unseen repository or claim an auto-refresh service is running. Avoid a new snapshot for every rerun; use existing tool output paths and the artifact policy.

## Manual designer edits: detect drift without rewriting DESIGN.md

The next UI workflow checks **Git changes**, not conversation memory and not every page:

```bash
python -X utf8 skills/ui-design/scripts/design_drift.py --root /path/to/project
```

After a real, owner-reviewed initial design reconciliation, the designated existing policy file may contain **one** baseline pointer:

```markdown
<!-- workflow-axa-design-baseline: <reviewed full Git commit SHA> -->
```

The tool compares that commit with the **current checkout**, including committed, staged, unstaged and untracked UI files. It reports changed paths and whether shared/global CSS changed (then examine dependent consumers). It never edits files, approves a style or infers intent. Don't update the marker on every CSS change: move it only as part of an explicit review that covered the changes. Worktrees/teammates use the Git SHA from the checked-out project, not a per-machine cache. If the baseline is absent, unavailable, or the repository isn't accessible, output **baseline-unknown** and do an initial targeted inspection. A filename-level change list is not a CSS dependency graph; investigate selector/component effects and actual runtime as needed.

Routine changes to existing token values or styles should appear directly in the project's **real components/kit** without transcribing those values into DESIGN.md. Keep only approval, intended use, Figma references and exceptions in that document. A new component/variant is discovered as a candidate and requires a human decision before becoming approved; the kit example may need one-time registration.

## Change and deletion handling

- Same component, changed internals: current preview updates through existing tooling; targeted review establishes whether appearance/contract changed. A hash change is not automatically design rejection or renewed approval.
- New variant/story: candidate until its coverage is approved; top-level catalogue status does not grant it consent.
- Removed usage: update that screen only; do not delete a shared component used elsewhere.
- Renamed/moved source: preserve a stable entry ID when intended; update actual imports/references through the approved change. No automatic replacement.
- Deleted component/story: surface missing references and consumers; affected reuse pauses. Do not hide broken stories to make checks pass.
- Changed theme/brand/dependency: check affected coverage, not just the leaf component file.
- Old review: preserve its embedded capture and source identity. Current generated references cannot rewrite what was presented.
- Inaccessible source/runtime, unknown ownership or permission: report the gap and stop the dependent action, not unrelated authorised logic.

## What the owner sees

In the unchanged HTML report's **Inspect screen** section, each element names its role, exact catalogue entry/variant/state, code/example references and intended content/event change. A pattern entry identifies composition. Real captures are labelled as captures; source checks do not prove the image actually used those components. Capture records and actual preview inspection supply that evidence. No “approved kit” badge is inferred from a file name, screenshot or agent assertion.

Background guidance: [stories](https://storybook.js.org/docs/get-started/whats-a-story), [Autodocs](https://storybook.js.org/docs/writing-docs/autodocs), [generated index](https://storybook.js.org/docs/configure/user-interface/sidebar-and-urls). These are optional tooling references, not runtime dependencies or authorisation to install anything.
