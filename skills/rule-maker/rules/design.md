# Application UI: strict kit reuse — no agent-authored presentation

This is the shared **kit-only** policy for ordinary requests, /workflow and delegated work. It applies to application HTML/JSX/templates, page composition, CSS, visual properties, assets and native/rendered UI. Backend-only work needs no kit. Preserve existing presentation and user changes; do not strip styles or rewrite old interfaces.

## Select before implementation

Load local **ui-design** before dependent planning/edits. For each new substantive UI task, establish the exact component/pattern source, selected entries, variants, states, area and preview access. An explicit owner choice or still-valid same-task decision counts; do not ask again for every control. DESIGN.md, a folder name, a screenshot, an installed framework or an approval label alone is not proof of a usable selection. If the source is missing, conflicting, stale, inaccessible or incomplete, **STOP affected UI integration and ask**. Independently authorised logic/read-only work can continue.

- **behaviour-only:** repair or extend authorised logic without adding/replacing interface markup or changing existing presentation. Do not create plain controls as a fallback. Existing interface preservation does not retroactively approve that screen for reuse elsewhere.
- **approved-kit:** reuse the selected real components through supported APIs and approved composition patterns. Wiring approved imports, events, data and documented slots is allowed; writing new native tags, wrappers, copied DOM or layout to reproduce them is not. Existing approved controls may internally render HTML/CSS; reuse is not authoring those internals.
- **blocked/unselected:** leave the missing UI work pending. Ask for the exact approved source or defer to the designer. There is no plain-HTML fallback, silent substitution or speculative styled prototype.

## Hard boundary for application work

Do **not** create, modify or inject application CSS, inline styles, style blocks, CSS-in-JS, arbitrary utility classes, theme overrides or new visual assets. Do **not** invent HTML, JSX/TSX native-element structure, Angular/Blade/Vue templates, cosmetic wrappers or page layouts. A reusable component's supported approved variant is allowed; an arbitrary colour/spacing/size prop is not. SDK/native attributes, canvas/SVG, Unity/Pixi/Three visuals and JavaScript DOM/style mutation are not loopholes. Preserve established runtime rendering mechanisms; do not change their visual contract without a separate policy decision.

A feature request, implementation approval, kit setup, a legacy design-authoring mode or 'make it work' does not waive this boundary. Even accessibility or clipping repairs must identify a missing approved component capability and stop the dependent edit rather than introducing unapproved markup/styles or shipping an inaccessible substitute. A genuinely necessary new design or component goes to the designated designer/maintainer. Revising this policy is separate explicit rule-maintenance work, not an automatic exception offered by the agent.

## Code-backed kit; short project pointers

Use the designated project-local catalogue of actual framework components and examples. Read local ui-design/LIVE-KIT.md. Component code and adjacent examples define current appearance; generate the inventory from those sources, never maintain parallel hand-written property/style lists in several Markdown files. Project instructions point to the catalogue and retain project constraints. Human approval/intended-use decisions still need a single recorded source. A source change does not renew consent automatically. Check missing/deleted components, consumers, story references, dependencies and theme/brand scope before reuse; no guessed replacements or automatic deletion/migration.

## Verify and report

Record selections in the existing task. Check actual task-attributable changes, including deletions and visual props, against the boundary. Check accessible behaviour and relevant states through existing approved controls. Static scans are review aids, not proof of compliance. New source changes need targeted reconciliation; historical approvals/reports remain unchanged. Keep behaviour, design acceptance and release readiness distinct.

The approved **codebase-map report renderer** is a narrow exception: generate its existing HTML/SVG shell and embed authorised real captures/component references. Do not rewrite its theme, run raw application markup inside it, create application prototypes under a reports path, or use report maintenance as application styling permission. Current UI decisions come from kit references, not from invented mockups. Older schematic reports remain historical illustrations, not implementation authority.
