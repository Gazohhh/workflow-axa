# UI examples: existing styles only (D14)

## No design source

Owner: “Add notification settings.” The agent searches the kit and the existing code for each element. A toggle row already exists in `settings.page.html:40` (`ion-item` > `ion-toggle`), so the new row mirrors it with the same tags and classes. Nothing matches the time picker, so the agent asks exactly: “I couldn't find a matching style for the time picker. Is there an existing element I should mimic?” and stops that element. No new CSS, invented class, plain stand-in or mockup; plain HTML only if the owner explicitly says so.

## Explicit choice

Owner: “Use Settings/Form and Buttons/Primary, default size.” Inspect these exact sources and allowed composition. Record the selection once. Wire supported data/events and slots. Do not add a cosmetic div, spacing classes, a colour prop or an alternative button.

## Existing behaviour repair

Fix a selected dialog's save handler and tests without changing its DOM/style. A missing accessible name or focus behaviour that needs markup/style changes is a kit capability issue to report, not authority to author a substitute. No full kit setup is needed for an unchanged interface's logic fix.

## Component changed or deleted

Compare selected sources and actual catalogue. A changed appearance becomes needs-review, not approved after refreshing a hash. A deleted story/component is missing, not quietly replaced. Keep historical reviews and inspect consumers before any removal. Removing one usage from a screen does not delete the shared component.

## Report

Keep the existing report shell. Inspect screen lists E1 Save action → Buttons/Primary → medium/loading → actual component/example → content/data changes only. The captured screen and its provenance are reviewed together; an agent-written badge is not proof. Old schematic samples are historical examples, not an approved app design.

## Ordinary request and resumption

The global core routes UI work to this same skill without /workflow. Confirm live loading in the actual host; installation alone is insufficient. Pass selections and the no-HTML/CSS boundary to subagents. On a same-task resume reuse valid decisions, refresh affected sources and do not restart the interview unnecessarily.

## Blanket approval is not a missing-style answer

The agent asks the mimic question for a status message. It must not recommend a plain `<span>`. A reply "yes to all recommendations" leaves this element blocked: ask which existing element to mimic or request clarification of the user's intended answer. "Use plain unstyled HTML for this status message" is a direct element-specific instruction, not a precedent for other controls. Ordinary approval of an already-settled implementation plan still works normally.
