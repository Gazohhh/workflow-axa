---
name: ui-design
description: "Use automatically for application UI work within workflow or ordinary requests: controls, pages, templates, interaction states, visual assets, native or rendered game UI. Preserve existing appearance and stop unapproved styling. Establish functionality-only, approved-kit or explicitly authorised design-authoring mode; do not redesign by default or block unrelated backend work."
---

# UI design boundary

Build agreed behaviour, reuse approved presentation, and leave missing design unfinished rather than invented. This skill selects design authority; it is not an automatic designer or another implementation workflow. For explicit catalogue work, [KIT.md](KIT.md) defines `kit-audit`, `kit-setup` and `kit-check`, with local templates and an optional read-only checker. These modes never manufacture project styles or approve components; setup still needs bounded approval.

## 1. Establish the affected surface

Apply the installed workflow's RULES.md gate and shared rule-maker `rules/design.md` first. Missing applicable rules or unresolved safety/authority conflicts block dependent changes. Bounded read-only inspection remains allowed. Do not launch rule-maker merely because no kit exists: a scoped functionality-only plan can be ready without one.

Identify the actual application areas, frameworks/versions, current task, effective project restrictions and approval. Include markup, templates, components, rendered/native UI, assets and state-dependent appearance—not just stylesheet files. Backend-only work skips this skill unless it changes an interface contract. A report-only request uses the existing local codebase-map renderer; see [CONTRACT.md](CONTRACT.md) for its narrow exemption.

## 2. Confirm the task source and mode per area

Use [CONTRACT.md](CONTRACT.md), and [KIT.md](KIT.md) when selecting/updating an actual catalogue. Default to **functionality-only** unless current, explicit project/task authority establishes **approved-kit** or **design-authoring** for this area. Never infer kit approval from a directory name, familiar class, installed library, screenshot, designer job title or general “make it work” request.

- **Functionality-only:** preserve existing presentation; reuse an explicitly approved component/pattern without restyling. New minimal semantic controls need an agreed behaviour and preview destination. No invented CSS, utility combinations, visual overrides or decorative layout. Record design pending where no approved design exists.
- **Approved-kit:** use actual approved components, variants and page patterns through supported APIs. Inspect the designated sources, not random legacy screens as design authority. Missing kit coverage is a gap; batch questions or obtain an explicit bounded functionality-only fallback.
- **Design-authoring:** obtain approval of the affected surfaces, references, allowed changes and acceptance criteria before creating/changing presentation. This mode is limited to this design task, not permanent global permission.

For a new substantive UI task, establish the exact design source and presentation mode with the owner before selecting appearance. An explicit task instruction or a still-valid recorded decision counts; a project DESIGN.md or general kit approval alone does not select the source/composition for this new task. Present the applicable existing source as a recommendation and ask once when selection is unresolved. No repeated question for every control or unchanged resumption. If neither a kit nor a plain preview is selected, leave UI integration blocked rather than defaulting to invented markup.

Use existing confirmed decisions. Invoke grilling through the workflow adapter for consequential gaps (preview access, layout, interaction, required kit coverage), not for every element. Independent behaviour work can continue only when already authorised.

## 3. Carry the boundary into the plan

Add a compact UI entry to the existing PLAN/STATUS checkpoint: mode and area; authority/reference; approved components/patterns; preview destination/access; prohibited changes or narrow exception; behaviour checks; design acceptance and release state. See [EXAMPLES.md](EXAMPLES.md). Do not create a kit, another task folder or a standalone UI manifest just to record these facts.

The existing PLAN/TODO and flowchart approval remains mandatory for substantive work, including ordinary requests routed without a slash command. For UI scope, call codebase-map with its optional screen-flow projection in the SAME report: actual/proposed screen states, connected actions, source references and design decisions on the relevant controls. Preserve the report shell and technical sections. An abstract source-selection chart is not a screen preview. A missing capture is marked unverified, not replaced by an invented approved-kit look.

Behaviour approval is not unseen design acceptance. Keep pending design and release limits visible.

## 4. Implement only the authorised work

Pass the mode, references, protected appearance, preview boundary and exceptions to every worker and specialist. Preserve existing selectors and runtime layout contracts; do not strip old styling or refactor unrelated markup. Native semantic controls, labels, validation, keyboard access and necessary state feedback are functional requirements—not optional polish. Do not add a styling reset to make a preview look plain.

Keep existing behaviour/presentation boundaries; do not invent a new component framework for a future designer. New interaction/layout choices and styling fixes outside the approved scope require a bounded decision. A newly found CSS class does not authorise its use.

## 5. Verify and hand off

Apply [VERIFY.md](VERIFY.md) to actual task-attributable changes, including new/deleted/binary files and approved component definitions. Run relevant behaviour/accessibility checks and inspect affected screen states when possible. Preserve approved visual references; a passing test or screenshot does not establish design acceptance.

On resume revalidate mode, sources, scope and approval; preserve settled decisions and legacy tasks. Report functionality, design acceptance and release readiness separately. Design-pending UI remains in its agreed preview, not silently shipped. Record necessary results in existing files and follow the artifact policy.
