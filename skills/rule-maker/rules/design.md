# Application UI: reuse existing styles, never write CSS

The shared UI policy for ordinary requests, /workflow and delegated work (owner decision D14, from the owner's styling rules). It applies to application HTML/JSX/templates, page composition, CSS, visual properties, assets and native/rendered UI. Backend-only work needs none of it. Preserve existing presentation and user changes; do not strip styles or rewrite old interfaces.

## The rules

1. **No new CSS, ever.** Do not create, modify or inject CSS: no new stylesheet rules, no `<style>` blocks, no `style=""` attributes, no CSS-in-JS, theme overrides or arbitrary visual props. JavaScript style mutation, canvas/SVG or native attributes are not loopholes.
2. **Only existing styles.** Use only classes and IDs already defined in the project's stylesheets or already present in its HTML/templates: the design kit when the project has one, otherwise the existing code. A script hook is not styling: prefer a new `data-*` attribute that no stylesheet targets; never invent a class or ID for styling.
3. **Mirror the element, with its context.** A new element copies both the **class list** (all of it, no class dropped or added) and the **HTML tag** of the existing element it imitates, so it looks and behaves the same; `class_rules.py <root> --match <tag> <classes>` must find that existing element. Class and tag are not enough when its look depends on where it sits: list every rule that names the class (ui-design `scripts/class_rules.py`), and place the copy inside the same wrapper as any rule marked as needing context; also check rules of the new place that style its children (for example `.title div`). Compare the parent it comes from with the parent it goes into (`class_rules.py <root> --compare <from> <into>`): any layout or inherited text difference (a heading makes text bold), even a small one, means it is not a match; compare every placement you offer, before offering it. Ask rule 4's question; never recommend the copy anyway. An existing component (kit or code) is reused through its API, not rebuilt from its DOM.
4. **Search, then ask, then (only if told) plain.**
   - **Search** the existing code (and the design kit, if any) for an element that already does what the new element is for.
   - **Ask** when nothing matches, and stop that element, using exactly: *"I couldn't find a matching style for [element]. Is there an existing element I should mimic?"* You may list existing elements of the **same tag** the user could pick. Never offer new CSS (not even as a one-off exception), an invented class, or another tag's classes as options.
   - **Plain only on instruction.** Only when the user explicitly says to proceed without a match, or confirms no similar element exists, add the element as plain HTML with no classes and no styling. Record their words.
5. **Verify before finishing.** Check the final diff: no new CSS properties anywhere, and every class/ID used already exists in the project's source files. Name the file that defines each reused class.

## Where styles come from

- **Projects with a design kit** (a catalogue, Storybook, DESIGN_KIT.md or similar named in project instructions): search the kit first, then existing code. Read local ui-design/LIVE-KIT.md for code-backed catalogues.
- **Projects without one:** existing code is the source. The rules above apply unchanged; "no kit" is never permission to write CSS.

A filename, folder, screenshot or framework name alone does not prove which element to mirror; the decision is recorded in the task with the exact source file and element. Existing approved controls may internally render HTML/CSS; reusing them is not authoring those internals.

## Modes (recorded per UI task)

- **behaviour-only:** logic changes inside an existing interface; markup and appearance stay as they are.
- **reuse:** new or changed elements built only from existing classes/IDs/components, mirroring class and tag (rules 2–3).
- **blocked:** no matching element yet; the question in rule 4 is open. Independent logic and tests can continue.
- **plain-by-instruction:** the user explicitly allowed plain unstyled HTML for named elements (rule 4).

## Verify and report

Record each reused element with its source file in the existing task. Check task-attributable changes, including deletions and visual props, against the rules; static scans help but are not proof. Accessibility stays required: use an existing accessible element or ask; never ship an inaccessible substitute. Keep behaviour, design acceptance and release readiness distinct.

Every UI-visible change shows a **screen diagram** in the HTML plan report (codebase-map UI-FLOW.md): real captures of the current and proposed screens when they can be made safely, otherwise a clearly labelled layout sketch. A missing diagram makes the report a draft.

The codebase-map report renderer is a narrow exception: it generates its own HTML/SVG shell. That is not permission to style the application or to build application prototypes under a reports path.
