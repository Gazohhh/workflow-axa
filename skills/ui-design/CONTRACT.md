# Application UI contract: existing styles only

The shared `rule-maker/rules/DESIGN.md` is authoritative. This file spells out what each mode allows and how older records map onto it.

## Mode and permissions

| Mode | Permitted | Not permitted |
|---|---|---|
| behaviour-only | Data, events and logic inside existing interfaces; presentation stays as it is. | Any new CSS; changing markup or appearance. |
| reuse | New or changed elements that use only classes/IDs already defined in the project's stylesheets or present in its HTML (design kit first when there is one), mirroring the class **and** tag of the element they imitate; existing components used through their API. | New CSS of any kind (DESIGN.md rule 1); inventing class names; copying a component's internal DOM instead of using it. |
| blocked | Read-only investigation; DESIGN.md rule 4's exact question; independent logic and tests. | Building the unmatched element in any form until the user answers. |
| plain-by-instruction | For elements the user named: plain HTML with **no classes and no styling**, only under DESIGN.md rule 4's element-specific direct instruction/confirmation. | Any class, style or CSS on those elements; extending the permission to other elements. |

Component calls are fine: `<SaveButton onSave={save} />` reuses an existing component. A hand-written `<button class="...">` is fine only when an existing `<button>` in the project already uses exactly that class. A capital letter or Angular selector is not proof the component exists: find its definition. Do not change a reused component's internals. Keep existing functional selectors and runtime contracts.

## Finding the element to mirror

Look for the element that does the same job for the same user (DESIGN.md rule 4), in this order: the project's design kit or catalog (if named in its instructions), then components and templates in the same area, then the rest of the codebase. Record the chosen element as `file:line`, its tag, its classes and why it fits that job. A filename, folder or screenshot alone is not proof; the source file is. Projects without a design kit use existing code as the only source.

## Report diagram

Every UI-visible change, except the small change route (DESIGN.md "Verify and report"), shows a screen diagram in the same full codebase-map report, as SKILL.md step 3 and UI-FLOW.md describe. A missing diagram keeps the report a draft.

The codebase-map renderer may generate its own HTML/CSS/SVG report shell. That is report code, not application code, and gives no permission to style the application or build prototypes under a reports path.

## Older records

Keep previous files, identifiers and decisions as history. Before the next affected unit:

- `approved-kit` → **reuse** (the kit is the first source; existing code is now also allowed).
- `functionality-only` → **behaviour-only**.
- `design-authoring` → historical only: agent-written CSS is still not allowed; finish with reuse, or ask.
- Missing mode: decide it from the change (behaviour-only or reuse) and record it.

Do not delete prior HTML/CSS. A material conflict with stricter project rules is resolved explicitly; the stricter project rule wins until its owner changes it.

## Lifecycle

Keep authority, implementation, design acceptance and release readiness separate in the task records.
