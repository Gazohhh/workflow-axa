# Workflow AXA

The words this package uses in its skills, references and reports, and the one file that owns each repeated rule. `tools/validate.py` reads the `_Avoid_:` lines, the identifier list and the owner table, and reports each rejected synonym it finds in `skills/**/*.md` outside code spans and vendored upstream text.

## Language

### Approvals

**Agreement**:
The user's first approval: the agreed behavior, journeys, scope and acceptance of a task, before any plan.
_Avoid_: gate one

**Implementation approval**:
The user's second approval: the plan report with its tickets and checks, which permits code changes.
_Avoid_: gate two, plan gate

### Reports

**Report**:
The HTML page the package renders. "Review" names only the act of reviewing.

**Plan report**:
The report shown for implementation approval.
_Avoid_: HTML plan, approval report

"Task report" and "visual review" are not rejected: they name files (`TASK-REPORT.md`, `VISUAL-REVIEW.md`) and the act of reviewing.

**Delivery report**:
The report shown when a task ends, mapping each agreed requirement to its evidence.

**Screen diagram**:
The part of a report that shows current and proposed screens for a UI-visible change. It holds one of three kinds: capture, kit screen or sketch.

**Capture**:
A screenshot of the running application screen.

**Kit screen**:
A screen built from markup copied out of the project's design kit and shown with the kit's own styles.

**Sketch**:
A layout drawing of reused elements that shows structure, not the look.

### Work

**Task**:
The whole job the user asked for, with its records under `docs/plans/<task>/`.

**Ticket**:
One unit of a task with its own checks and status. In the report JSON, `tasks[]` is the ticket list; the name is historical.

**Checkpoint**:
The task record's current state: phase, approvals and what happens next.

**Lightweight edit**:
The route for an exact, low-risk change that nobody can notice. It skips both approvals; the checkpoint lists the files it may touch.

**Purpose statement**:
For a change a user sees on screen: who uses it, in what situation, their goal and what must stand out. Taken from CONTEXT.md and the code; asked when a missing part would change the result, otherwise written as `unknown`. Without a task, the user and goal the request or CONTEXT.md names stand in for it. UI elements are chosen by the job they do for that user.

**Small change**:
The route for a visible edit to text, order or visibility of existing elements on one screen, with no new element, file, data, interface or dependency. One owner yes to the named files and description replaces both approvals; there is no plan report. Unlike a lightweight edit, its effect is visible. Execute's "small route" (one ticket built by the main agent) is a different thing.

**Limited exception**:
A rules-readiness exception the user grants for one named piece of work while project rules are missing.
_Avoid_: scoped exception

### People and helpers

**User**:
The person in the chat.

**Owner**:
Whoever owns a file, design kit or rule; often the user, not always.

**Subagent**:
An agent started by the main agent. "Worker" is allowed for a subagent that builds.
_Avoid_: sub-agent

## Spelling

Prose uses American English (behavior, authorize, color, organization, license). Identifiers keep their spelling.

## Identifiers that keep their form

A hook, script or test parses, emits or asserts these exactly, or old records use them. The synonym report skips them.

- `Approval (gate two)`: checkpoint label parsed by `hooks/phase_gate.py`.
- `Reconfirmed (gate two)`: checkpoint label parsed by `hooks/phase_gate.py`.
- `Agreement (gate one)`: checkpoint label beside the parsed approval label, kept so existing records read the same.
- `## Current checkpoint`: heading parsed by `hooks/phase_gate.py`.
- `- Lightweight edit:`: checkpoint line parsed by `hooks/phase_gate.py`.
- `small route`: hook note in `hooks/phase_reads.py`, asserted by its test.
- `plan approval`: asserted in `skills/workflow-clarify/SKILL.md` by `tests/test_behavioral_cases.py`; "Plan approval record" is a report heading.
- `behavior agreement`: "Behavior agreement record" and status labels emitted by `skills/codebase-map/scripts/task_report.py`.
- `task overview`: report kind (`task-overview`) and the "SAVED TASK OVERVIEW" heading asserted by tests.
- `screen flow`: title and label emitted by `skills/codebase-map/scripts/screen_flow.py`.
- `ui_review`: report JSON key for the screen diagram.
- `schematic`: script value for a sketch.
- `capture`: script value for a capture.
- `kit`: script value for a kit screen.
- `review`: script value and `review.json`, `VISUAL-REVIEW.md` file names.
- `agreement`: report JSON key.
- `tasks[]`: report JSON list of tickets.
- `tickets[]`: report JSON list of tickets in the task record projection.
- `STATUS.md`: legacy task record read by hooks and scripts.
- `one-task exception`: text written into global instructions by `skills/rule-maker/scripts/activate_rules.py`.
- `bounded exception`: text emitted by `skills/rule-maker/scripts/activate_rules.py` and `readiness.py`.
- `behaviour-only`: UI mode value in `skills/codebase-map/scripts/screen_flow.py`.
- `authorised`: preview status value in `skills/codebase-map/scripts/screen_flow.py`.
- `CATALOGUE.md`: file name; `catalogue` is a key in the design-kit scripts.
- `cancelled`: ticket state and checkpoint phase parsed by `skills/workflow/scripts/ticket_records.py` and written by `record.py`.

## Rule owners

Each rule below is stated in several files today. The owner file states it in full; other files point to it.

| Rule | Owner file |
|---|---|
| Never write CSS | `skills/rule-maker/rules/DESIGN.md` |
| The question to ask when no existing style matches (DESIGN.md rule 4) | `skills/rule-maker/rules/DESIGN.md` |
| Never stage, commit or push unless asked ("Always" list) | `skills/workflow/SKILL.md` |
| Agreement is not permission to code | `skills/workflow/VISUAL-REVIEW.md` |
| Never install anything | `skills/rule-maker/rules/CORE.md` |
| A presented report is a snapshot and is not edited | `skills/workflow/VISUAL-REVIEW.md` |
| Read instruction files whole | `skills/workflow/SKILL.md` |
| What a check does not prove (loading, compliance) | `docs/EVALUATION.md` |
| Name only files you opened | `skills/workflow/RULES.md` |
