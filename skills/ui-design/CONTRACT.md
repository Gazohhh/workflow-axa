# Strict application UI reuse contract

The shared `rule-maker/rules/design.md` is authoritative for this package. This file explains its scope and backward compatibility. Missing authority blocks affected work, not independent read-only/backend activity.

## Mode and permissions

| Mode | Permitted | Not permitted |
|---|---|---|
| behaviour-only | Approved data/events/logic inside existing interfaces, keeping presentation intact. | New raw controls, native-tag wrappers/templates, CSS, inline styles or cosmetic changes. |
| approved-kit | Selected approved real components and documented variants, states, slots and composition patterns. | Recreating their DOM; changing internals; arbitrary visual props/classes; assembling a new unapproved layout. |
| blocked/unselected | Read-only investigation and questions; separately authorised independent logic. | Dependent UI integration, invented replacements, plain HTML fallback or silent kit setup. |

Component calls are not a ban on JSX: `<ApprovedSaveButton onSave={save} />` can be valid when that component/API/pattern is selected. A newly authored `<button>`/`<div>` or copied class/tag structure is not a substitute. Custom elements/Angular component selectors need the same source verification; a capital letter or selector name is not approval. Do not change the component's internals even when it is approved for use. Bind existing runtime styles only through the already-approved mechanism; do not introduce new style writes to solve a feature request.

The agent must never create, modify or inject application CSS, inline style, raw HTML/templates, new presentational JSX structure, tokens, decorative assets or visual overrides in these modes. The same boundary covers native/game presentation. Generic implementation or designer-task language does not grant a new exemption. Missing functionality or an accessibility/style defect goes to the designated maintainer. Changing this strict policy requires explicit, separately scoped policy maintenance; do not offer it as the routine fallback.

## Source selection

Confirm the task's kit/reference and intended composition once; an explicit task instruction or valid same-task decision counts. A filename, existing class, screenshot or designer title is not authority. Search existing code to understand behaviour or verify the designated API, not to choose an arbitrary design standard. When there is no full kit, a precisely identified, approved existing component/pattern can serve as a bounded source. A selected button does not select a complete screen layout.

Capture metadata identifies source, variant/state, brand/theme, viewport and current revision. Verify kit availability and sources against the actual checkout. A generated catalogue is not automatically fresh just because it has a URL. Missing/deleted references pause dependent UI work; no similar-looking substitution. Preserve approval decisions once, separately from generated current observations.

## Preview and report boundary

Preview access is explicit: existing development surface, safe data, intended audience and permitted commands. No new preview route, standalone application, Storybook install, feature-flag system or public screen is created merely because a report needs a capture. A document or report path does not make application markup exempt.

The approved local codebase-map renderer may generate its existing HTML/CSS/SVG reporting shell and include real PNG captures and a structured component selection table. This is the **only routine HTML/CSS generation exception**. It is report code, not app code. No raw app HTML/CSS/scripts are accepted by its data inputs. The report theme/assets require separate explicit package-maintenance scope to change.

No fabricated application look is used to fill a missing capture. Historical schematic support is retained to read/render earlier draft demonstrations; it is not authorisation for new application design. New approval-ready application reports require selected current kit references and real captures. Existing historical HTML remains untouched.

## Compatibility with earlier task records

Keep previous files/identifiers and decisions as history. Before the next affected unit:
- `functionality-only` is treated as **behaviour-only**; its former plain-markup permission is no longer active.
- `approved-kit` still requires the exact selected/current sources, variants, scope and pattern.
- `design-authoring` is a historical description, not a current permission for agent-authored presentation. Pause those writes and explain the stricter policy; do not silently execute earlier style plans or erase them.
- Missing mode: ask for the relevant source/selection, not another folder.

Do not retroactively delete prior HTML/CSS. Do not repeatedly ask after a valid selection remains unchanged. Material conflicts with stricter or older project rules must be resolved explicitly; a general rules-readiness exception cannot waive the UI boundary.

## Lifecycle

Keep authority, implementation, design acceptance and release readiness separate in existing task records. Human-approved component changes can update the live kit through its existing tooling; they do not silently alter historical reviews or approve new variants. Source hashes are freshness checks, not proof of consent or evidence that the screenshot was truly rendered by those components. Verify the rendering trace where required.
