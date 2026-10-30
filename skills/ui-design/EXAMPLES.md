# Small examples and decision records

Illustrations, not new project requirements. Keep actual answers in the existing PLAN/STATUS and relevant TODO/FINDINGS; do not copy this entire file into a task.

## Notification preferences without a kit

User asks for saved notification settings. Inspect existing settings behaviour and settle real questions (persistence, permissions, validation). The plan names an existing authorised developer preview. Implement the agreed behaviour with a labelled native checkbox and submit button through the application's existing framework. No new classes, CSS, icons, cards or custom switch. Existing global CSS can still style the markup; observe it, do not reset it.

A short checkpoint could be:

```text
UI: functionality-only, notification preview.
Authority: approved task R2; developer preview /dev/preferences, verified not shipped.
Reuse: existing SettingsForm behaviour, no approved presentation kit.
Boundaries: no styling or new public navigation; no component library install.
Functionality: persistence/validation tests passed; keyboard check pending.
Design: pending designer review. Release: not ready.
Next: complete the approved checks, then designer handoff.
```

These example paths are not present or approved in the user's project. If a real preview is unavailable, request a location decision before integrating new UI; do not fabricate one.

## Approved kit, missing variant

Project guidance explicitly approves `PrimaryButton` for primary submissions. Reuse its supported variant and behaviour. Do not copy its DOM or add arbitrary padding/colour props. If the request needs a destructive confirmation not covered by approved patterns, batch the missing interaction/design decision. Do not silently drop from approved-kit into plain HTML; obtain a bounded fallback or defer that portion.

## Existing component bug

Fix the approved event/state bug while retaining its markup, classes and visual props. Check existing success/error states. No new designer signoff is required merely because this is a new session. If preserving semantics requires changing the rendered element, inspect consumers and agree the affected presentation/interaction—not mechanical tag mirroring.

## Exact styling repair

A clipping fix really needs a CSS change. Ask for the bounded repair with expected impact and checks. Record that approval; do not redesign neighbouring controls, replace the style system or change unrelated references. Keep the original mode and name the exception, rather than silently switching the entire project to design-authoring.

## Designers introduce the approved kit later

Inspect its real components and explicit approval, available states, versions and patterns. Select approved-kit for the agreed next scope and add the source to existing project references. Prior functionality-only work remains design-pending until deliberately revisited. Publishing the kit does not approve all interfaces that use it.

## Rendered game UI

Unity/Pixi/Three code may update an existing progress indicator according to its approved behaviour. New colours, materials, motion, positions or iconography are visual design decisions even without CSS. No automatic fallback from a game interface to a new web overlay.

## Workflow review

Generate the existing approved flowchart with codebase-map. It may retain its local CSS/SVG styling while application work remains functionality-only. Its feature-flow arrows do not approve component spacing or a new screen mockup. The report and application have separate design authority.
