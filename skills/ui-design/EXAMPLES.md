# UI examples under strict kit reuse

## No design source

Owner: “Add notification settings.” Agent: “I can implement the approved settings logic, but this screen has no selected approved controls/layout. Which existing kit or pattern should I use, or should I leave the UI for the designer?” No plain form, CSS reset, temporary public route or mockup is created.

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
