# Workflow AXA

The words this package uses in its skills, references and reports, and the one file that owns each repeated rule. `tools/validate.py` reads the `_Avoid_:` lines, the identifier list and the owner table, and reports each rejected synonym it finds in `skills/**/*.md` outside code, HTML comments and the identifiers listed below. The formerly copied skills are checked like every other skill.

## Language

### Approvals

**Agreement**:
The user's first approval: the agreed behavior, journeys, scope and acceptance of a task, before any plan.
_Avoid_: gate one

**Implementation approval**:
The owner's answer to the one question that approves an offer (its files, operations and checks). It permits only the changes the offer lists. It has no waiver.
_Avoid_: gate two, plan gate

**Offer**:
What the agent asks the owner to approve: the behavior summary, the paths and protected operations it may touch, the exclusions, conditions and checks. It is recorded under `docs/plans/<task>/offers/` with an id and changes only through `record.py offer`; a change to its content makes a new offer. Every offer ends with the one question (*Show review.html first*, *Approve from this summary*, *Change something*).

**Legacy task**:
A task approved before the offer model, which the owner listed with `legacy_inventory.py` at the upgrade. It keeps its `Approval:` line, checked by `hooks/phase_gate.py`. A task not on that list uses offers only.

### Reports

**Report**:
The HTML page the package renders. "Review" names only the act of reviewing.

**Plan report**:
The optional HTML report of an offer, built on *Show review.html first* or when the owner asks for it.
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
An exact, low-risk change that nobody can notice. It needs no separate agreement but is still asked: it gets the minimal offer (its files, its check and a one-line why) and the one question, then one review and the short delivery.

**Purpose statement**:
For a change a user sees on screen: who uses it, in what situation, their goal and what must stand out. Taken from CONTEXT.md and the code; asked when a missing part would change the result, otherwise written as `unknown`. Without a task, the user and goal the request or CONTEXT.md names stand in for it. UI elements are chosen by the job they do for that user.

**Interrogation**:
An adversarial check the user starts with `/interrogate`: other agents try to show a concrete failure of a plan or a pinned change. A failure counts only when another agent reproduces it on a pristine copy. It reports and changes nothing.

**Blast radius**:
What a change can break outside itself, beyond the callers a search lists. Code-review step 4b reports it on a diff, planning records it as safety assumptions, and "what could this break?" asks for it directly. Method: `skills/code-review/BLAST-RADIUS.md`.

**Safety fact**:
A fact a change is safe because of, such as "this call only drops cache entries that nothing reads". Before the diff exists it is a safety assumption with the check that could falsify it. Review proves it on the evidence ladder (step 1 stated, step 5 reproduced) or marks it unproven.

**Unslop check**:
The required writing check that removes the patterns that make text read as machine-written, run before the cold-reader check. It never changes application UI copy, error messages or translations, and "Keep the meaning" wins over every tell. Owner of the rules and the tells: `skills/workflow/WRITING.md`.

**Spar**:
A session the user starts with `/spar`: a fresh Claude and GPT spar with the owner about an idea or a decision until the owner can choose a next move. It is its own skill, not part of the workflow, though it can be used during a task. Its optional record, when the owner keeps one, is `docs/spar/<date>-<topic>/SPAR.md`. Turning it into a workflow plan is the owner's choice at the end, as `skills/spar/SKILL.md` step 5 and `SPAR-FILE.md` "Where it lives" say. It never plans the HOW in tickets or implements.

**Comment debt**:
A misleading or stale comment outside the lines an approved change edits. It is listed in FINDINGS, not fixed; `/no-comments` is how the user cleans it up.

**Small change**:
The former route for a small visible edit, now absorbed into the one-ticket offer: one ticket, its offer and the one question, with the plan report only when the owner asks. The term stays for old records with a `Small change:` line. Execute's "small route" (one ticket built by the main agent) is a different thing.

**Limited exception**:
A rules-readiness exception the user grants for one named piece of work while project rules are missing.
_Avoid_: scoped exception

**Recipe**:
The order of steps for one kind of job (bug, feature, ui, refactor and so on), in `skills/workflow/flows/`. The router picks one from `flows/INDEX.md`; the skills it names do the work.

**Fallback**:
The named substitute when something a recipe needs is missing, from `skills/workflow/FALLBACKS.md`. The agent says it once, records it, and keeps going; only the conditions listed there pause work.

### Rules

`docs/RULE-CONTRACTS.md` labels each main rule of a skill with one of these three kinds.

**Hard rule**:
A rule that must always hold. A break is a defect, even when the result looks right.

**Procedure**:
The expected order of steps. The agent records a justified deviation.

**Judgment call**:
A decision the agent makes with a stated criterion. Two good runs can differ.

**CSS switch**:
The one setting per machine, in `~/.workflow-axa/settings.json`, that says whether styling may be written. It starts off; missing or invalid means off. Only the owner's Yes to the exact question turns it on, and a project's DESIGN.md with `css: never` keeps it off there.

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
- `small route`: defined in `skills/workflow-execute/SKILL.md` step 3.
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
| No CSS while the CSS switch is off | `skills/rule-maker/rules/DESIGN.md` |
| The question to ask when no existing style matches (DESIGN.md rule 4) | `skills/rule-maker/rules/DESIGN.md` |
| Never stage, commit or push unless asked ("Always" list) | `skills/workflow/SKILL.md` |
| Agreement is not permission to code | `skills/workflow/VISUAL-REVIEW.md` |
| Never install anything | `skills/rule-maker/rules/CORE.md` |
| A presented report is a snapshot and is not edited | `skills/workflow/VISUAL-REVIEW.md` |
| Read instruction files whole | `skills/workflow/SKILL.md` |
| What a check does not prove (loading, compliance) | `docs/EVALUATION.md` |
| Name only files you opened | `skills/workflow/RULES.md` |
| The blast-radius method (safety facts, where grep stops, evidence ladder, probes) | `skills/code-review/BLAST-RADIUS.md` |
| The Unslop check: when it runs and what it never changes | `skills/workflow/WRITING.md` |
| The Unslop tells | `skills/workflow/WRITING.md` |

## Places that write for a person

Each place below writes text a person reads, and points to `skills/workflow/WRITING.md` for how to write it. None restates the rules. A test keeps this list and the pointers in step.

| Place | What it writes |
|---|---|
| `skills/grilling/SKILL.md` | Every decision question to the owner |
| `skills/spar/SKILL.md` | The start card, frame line, progress lines, conclusion and handoff question |
| `skills/spar/SPAR-FILE.md` | A kept SPAR.md and the conclusion |
| `skills/wait-what/SKILL.md` | The plain explanation |
| `skills/resume/SKILL.md` | Status and handoff |
| `skills/rule-maker/AUDIT.md` | Audit proposals and findings |
| `skills/rule-maker/DIAGNOSE.md` | Diagnose results |
| `skills/ui-design/SKILL.md` | Kit findings and report content; application UI copy stays excluded |
| `skills/interrogate/SKILL.md` | The three lists |
| `skills/code-review/SKILL.md` | The review report |
| `skills/code-review/BLAST-RADIUS.md` | The impact report |
| `skills/plan-review/SKILL.md` | Plan findings |
| `skills/codebase-map/SKILL.md` | Report text |
| `skills/codebase-map/TASK-REPORT.md` | Task report prose fields |
| `skills/codebase-map/scripts/render_report.py` | Its plain-English advice |
| `skills/workflow-clarify/SKILL.md` | The agreement request |
| `skills/workflow-specify/SKILL.md` | Tickets, the offer inputs and the one question |
| `skills/workflow-execute/SKILL.md` | Progress and ticket summaries |
| `skills/workflow-deliver/SKILL.md` | Delivery records and the final reply |
| `skills/workflow/SKILL.md` | Route notices |
| `skills/workflow/TASK-FOLDER.md` | Task records and handoffs |
| `skills/workflow/VISUAL-REVIEW.md` | Review report text |
| `skills/writing-for-agents/SKILL.md` | Which Unslop tells apply to agent documents |
| `skills/domain-modeling/SKILL.md` | Glossary entries and ADRs |
| `skills/no-comments/SKILL.md` | Its final report |
