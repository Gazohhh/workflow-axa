---
name: ui-design
description: "Use automatically for application UI in workflow or ordinary requests. Enforce kit-only reuse: no agent-authored HTML/templates, CSS or inline styles. Verify selected real components, variants and patterns; block missing authority, never fall back to plain HTML. Inspect code-backed catalogues and preserve historical reports."
---

# UI: reuse, do not invent

Read shared rule-maker `rules/design.md` and [CONTRACT.md](CONTRACT.md). This is a permission/selection skill, not a designer or another implementation workflow. The normal rules-readiness gate, grilling, plan review and implementation approval remain in force.

## 1. Establish the surface and decision

Identify the task, framework versions, affected area/brand/platform, designated project sources, existing changes and applicable rules. Backend-only work skips this skill unless it changes UI contracts. A missing DESIGN.md filename is not a blocker when an equally authoritative source exists. The mere presence of that file, a catalogue or a familiar class is not selection/approval.

For a new substantive UI task, confirm the exact source and selected component/pattern IDs, variants and states. Reuse explicit owner choices or a still-valid same-task decision. Ask once when unresolved, batching consequential gaps through grilling. Do not ask again on every control or unchanged resume.

## 2. Select a permitted mode

- **behaviour-only:** authorised logic changes within an existing interface, preserving its markup and appearance. No new plain-HTML controls, previews or invented layout.
- **approved-kit:** import and wire the selected actual components/patterns using documented APIs/slots; reuse appearance, do not recreate their DOM or styles. An approved button is not approval for an invented page composition.
- **blocked/unselected:** missing design authority or kit coverage pauses that UI integration. Ask for a designated approved reference or leave it for the designer; independently approved logic/tests can continue.

Use [KIT.md](KIT.md) for `kit-audit`, `kit-setup`, `kit-check` and [LIVE-KIT.md](LIVE-KIT.md) for code-backed discovery. Setup can audit/propose wiring to existing preview tooling; it cannot create application presentation, install tools or approve new components. Designer changes are external inputs to reconcile, not permission for this agent to author HTML/CSS. A legacy functionality-only/design-authoring record cannot bypass the new boundary; see CONTRACT.md.

## 3. Prepare the existing plan/report

Keep one compact selection record in PLAN/STATUS: mode, area, authority, stable item/story IDs, component and example sources, variants/states, selected pattern, preview access and remaining design/release limits. No duplicate component inventory or new folder per selection. Use [EXAMPLES.md](EXAMPLES.md).

For substantive UI work, use local codebase-map's **same full HTML report**. Its screen-flow view shows real captures, interaction arrows and exact selected elements in Inspect screen: role, catalogue entry, variant/state, source/example and permitted content/behaviour changes. Captures must come from authorised existing tooling; no fabricated kit likeness or hand-built app mockup. Missing capture/source evidence means draft/unverified, not approval-ready. Read codebase-map/UI-FLOW.md for binding and snapshot checks. Do not alter the approved report shell.

Resolve material decisions, present the plan/report and stop for owner approval. Behaviour approval is not unseen design signoff. New ordinary UI requests use these gates even without a slash command.

## 4. Implement and verify only authorised reuse

Pass the same selected IDs, APIs, pattern, source revision, protected internals and preview permissions to workers. Do not use raw HTML, new native tags, CSS, inline style, arbitrary visual props or copied markup as substitutes. Preserve existing functional selectors and runtime contracts. Accessibility remains required; report a missing kit capability rather than invent a repair or ship an inaccessible substitute.

Use [VERIFY.md](VERIFY.md) on the actual final diff and relevant runtime states. Check source/variant/scope freshness, safe environment and build permissions before executing previews. A green scanner is not approval. Keep approved references and follow the artifact policy.

On update/deletion/resume, reconcile only affected sources/consumers. A missing component blocks its selection; a changed one needs review, not automatic reapproval. Preserve historical captures and decisions. Report behaviour verified, design accepted and release-ready separately. Never claim a live kit was installed or every host follows the rules unless actually checked.
