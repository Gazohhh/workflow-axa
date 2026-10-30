# Application UI: no invented presentation

Applies to application markup, controls, page composition, interaction states, styling, assets and native/rendered UI. Load for UI work even when no CSS edit was requested. Backend-only work needs no kit. Existing interface fixes preserve appearance; this policy does not authorise stripping existing styles, rewriting old code or installing design tools.

## Shared default and local route

Use the installed local **ui-design** skill before dependent application planning/edits, including ordinary requests and delegated work. It applies this policy; it does not automatically design. Missing/inaccessible route or unexplained project-policy conflicts block affected UI work, not unrelated read-only/backend tasks. Reuse confirmed decisions after checking freshness.

For each new substantive UI task, confirm the specific source and mode before choosing appearance. An explicit task instruction or a still-valid same-task decision is sufficient; discovering DESIGN.md, an approved kit or an old screenshot is not by itself that task selection. Ask once with the relevant recommendation when unresolved; do not reopen settled decisions. Functionality-only is a restriction on authority, not automatic permission to create plain markup anywhere.

Select a mode per affected area in the existing task record:

- **functionality-only (default):** build approved behaviour, preserve existing presentation, and reuse only explicitly approved components/patterns. New minimal semantic markup is allowed within the agreed functionality-only scope and authorised preview destination. Design remains pending where no approved presentation exists.
- **approved-kit:** use designated, approved real components, supported variants and composition patterns for their intended purpose. A directory/library named ui-kit, familiar class, existing tag or screenshot alone does not establish this authority. Local ui-design/KIT.md defines the catalogue workflow; new entries remain candidates until their exact source/variant/scope is approved. An optional machine-readable catalogue is never mandatory for a valid existing kit. Missing coverage needs a decision, not invented styling or silent fallback.
- **design-authoring:** create/change presentation only within an explicitly approved design task or named narrow repair. Define area, references, allowed changes and acceptance; it is not permanent global styling permission.

No task scaffolding merely to determine a mode. Agree new preview placement/access before integration; do not create routes, feature flags, standalone prototypes, reset styles or new dependencies without scope approval. A preview must not silently ship or become public. A feature-flow review approves behaviour, not unseen appearance.

## What “no new styling” covers

No new/modified CSS rules, style tags, inline styles, CSS-in-JS, arbitrary utility/class combinations, theme overrides, visual component props, decorative wrappers/layout, icons or visual assets without the required design authority. SVG, canvas, native attributes, Unity/Pixi/Three presentation and configuration are not loopholes. Preserve existing approved runtime geometry/state behaviour; material changes require the appropriate scope, not a blanket ban on all rendering updates.

Inspect designated sources and their APIs; do not select arbitrary legacy markup as the design standard. Existing class names are not an approval list. Prefer component reuse over copying its rendered tags. Functional IDs/labels/test hooks may be used for their purpose, not to introduce hidden styling.

Plain markup still requires useful labels, validation, keyboard/focus behaviour and accessible feedback. Global CSS may affect it; do not add resets to make it look neutral. Do not copy incorrect semantics just to match a tag. Batch consequential missing design/interaction decisions through grilling; no invented question quota or repeated approval of settled choices.

## Completion and exemptions

Record mode, authority/reference, allowed component/pattern scope, preview boundary and exceptions in existing records. Review actual markup/visual changes and relevant states, not CSS filenames alone. An automated diff scan or screenshot cannot approve a design. Preserve accepted visual references; do not replace them to make a failing comparison pass.

Report functionality, design acceptance and release readiness separately. Design-pending UI is not a finished interface. Resume/recheck changed scopes or kit versions without bulk migration or automatically restyling past work.

Normal workflow reports retain the approved local codebase-map renderer/assets. This narrow exemption is not permission to style application prototypes under a reports path, change the report theme or impose its visual style on applications.

Sources (principles, not mandatory remote reads): [native HTML controls](https://www.w3.org/WAI/WCAG21/Techniques/html/H91), [form labels](https://www.w3.org/WAI/tutorials/forms/labels/), [CSS inheritance](https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Cascade/Inheritance), [components with usage guidance](https://design-system.service.gov.uk/components/). The three modes and approval rules are team policy, not claims that these sources prescribe this workflow.

For substantive UI planning, the normal full HTML report includes the local codebase-map screen-flow extension: screen previews joined by actions and meaningful design decisions, with sourced kit captures or explicitly authorised labelled schematics. Preserve the established report shell, evidence and approval stop. Ordinary UI requests use the same policy; only saying /workflow must not determine whether design authority is checked. A screen sketch approves neither appearance nor app implementation.
