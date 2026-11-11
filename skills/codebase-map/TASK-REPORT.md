# Central engineering task report

Use optional `task_report` in schema 2 when the user requests a full engineering overview, or workflow-specify/workflow-deliver prepares one. Keep the existing flowchart, screen flow, comparison, scope and traceability. The bundled task_report.py helper validates and renders the added content; its scoped CSS leaves old reports unchanged.

PLAN, TODO, FINDINGS and DECISIONS (or their established equivalents) remain authoritative. Generate the JSON projection from those records, cite its source IDs and exact sections, and compare the projection to those records before presentation. Update records first; never hand-maintain an independent specification in HTML/JSON. Never edit a presented/approved HTML or JSON snapshot; retention follows `workflow/VISUAL-REVIEW.md` "Superseded review cleanup".

### Optional record-backed text, without copying it twice

For a new draft (`state: draft`), put `heading:Agreement` (or another exact Markdown heading) in a section `locator`, or `ticket:T1` in a ticket `locator`. The source ID must resolve to a Markdown file inside the task folder; tickets must cite `TODO.md` and use the labeled ticket format. This opt-in copies the heading's content into the section's `text`, or the ticket's What needs to happen/Technical details/How to verify into `specification` and What should work into `expected`. Source bullets and code markers are preserved as plain text, not interpreted as HTML. It refuses repeated/missing headings and ticket IDs. Legacy checkbox tickets still need authored report text; the tool never guesses their structure.

```bash
python -B skills/codebase-map/scripts/record_projection.py --task docs/plans/my-task --input docs/plans/my-task/reviews/draft.json --output docs/plans/my-task/reviews/draft-projected.json
python -B skills/codebase-map/scripts/record_projection.py --task docs/plans/my-task --input docs/plans/my-task/reviews/draft-projected.json --check
```

Use the new JSON for normal renderer validation and presentation. The tool changes no source records, tests, check results, graphs or approval. It never overwrites an existing file or touches an approved report. An agent must still author diagrams, check semantic accuracy and match requirements/acceptance. `--check` fails if a source field drifted.

## Fields

`task_report` has `phase` (planning/progress/delivery), `agreement`, `sections`, `tickets`, `checks` and `acceptance_results`, and optional `attention`. Delivery also requires `completion` (complete/partial/blocked). An awaiting-approval or approved plan requires `screen_change`: `visible` when users see any change on screen (order, text, which rows show, layout), which also requires an application `ui_review` screen diagram ([UI-FLOW.md](UI-FLOW.md)), otherwise `none`. Never copy a sibling task's report without checking this. Unknown keys inside these new objects fail validation; older top-level extension behavior is unchanged.

Every sourced object uses `source` (an existing supplied source ID) and `locator` (the specific record heading, line or result). Text is escaped; no Markdown, raw HTML, scripts or executable commands are evaluated. Paragraph breaks and line breaks remain readable. Write every prose field with the `simple-english` skill (`../simple-english/SKILL.md`, Plain mode and its workflow-axa adaptation) and run its self-check before rendering; keep exact commands, identifiers and contractual terms.

| Object | Fields and meaning |
|---|---|
| `agreement` | `status`: approved/waived/legacy/not-required/not-approved/unknown; `summary`. Approved/waived needs exact `revision`, actual `response`, `source`, `locator`. Legacy (a pre-2.8 single-gate approval) and not-required (a lightweight edit) cite their record with `source`/`locator`, may name a `revision`, and never carry an invented `response`. Unapproved/unknown may cite a source but must not claim an approved revision/response. This is behavior/scope authority, separate from checkpoint.approval, which means implementation-plan authority. |
| `sections[]` | `id`, `title`, `text`, `source`, `locator`. IDs: request, goals, non-goals, specification, decisions, risks, testing, optional milestones, and delivery when applicable. All except milestones/delivery are required for a central overview. An older report may carry one `agreement` section in place of goals and non-goals; never both. What each one holds is under "What goes where". Split paragraphs for readability. |
| `attention[]` | Optional, at most three. `text`, `source`, `locator`. One short line for each thing the owner did not approve or would not expect, such as the agent doing more than was approved. Shown beside the status as "Read first", with a link to the decisions. The decisions section explains it in full. |
| `tickets[]` | `task`, `specification`, `expected`, `source`, `locator`. Exactly one specification for each existing tasks[].id; existing task relationships, acceptance links, affected files and outcome remain in tasks. Describe implementation responsibility and expected behavior here, not another task status. Both texts are shown as the ticket description. Put in `expected` only what no acceptance item of the ticket already states. A behavior that must hold belongs in an acceptance item with its check. |
| `checks[]` | `id`, `title`, `kind` (test/review/inspection), `status` (passed/failed/red/stale/limited/blocked/not-run; red = failed before the change, as the test-first plan expects, shown as "Failed before the change, as expected" and never cited as acceptance evidence; stale = passed on files that changed since), `expected`, `actual`, `limits`, `source`, `locator`; optional exact `command`. Name the relevant source/runtime identity in locator/limits. Reviews keep Standards and Spec findings distinct, with links to their fixes/rechecks. |
| `acceptance_results[]` | `acceptance` (existing acceptance ID), `status` (verified/partial/failed/unverified/waived/superseded), `checks` (check IDs), `note`, `source`, `locator`. Verified needs at least one passed check and no failed/unrun evidence among its references. Failed needs a failed check. Waiver and superseded (descoped) must cite the actual decision in note/source and are not a pass; superseded cites no checks. These are the report values of workflow-deliver's verdicts. |

During planning, checks/results may be empty. An approval-ready implementation report requires recorded approved/waived behavior agreement. A draft may honestly show an unresolved agreement. A new implementation plan still follows the normal real-response approval gate.

## What goes where

The page follows the design-doc order: context and scope, goals and non-goals, the design, alternatives considered, cross-cutting concerns. The implementation plan follows as a sixth section. Each fact has one home.

| Field | Shown as | Write here | Do not write here |
|---|---|---|---|
| `understanding` | Lead under the title | The outcome, in one or two sentences | The request again |
| `attention[]` | "Read first" beside the status | Each surprise in one short line | The explanation. It belongs in decisions |
| `request` | Context and scope | The problem as the owner met it, the facts about today, one sentence on what is built | Goals, design detail |
| `goals` | Goals | One paragraph for each outcome. Each must be checkable | How it is built |
| `non-goals` | Non-goals | One paragraph for each thing that could be a goal and is left out on purpose | A negated goal such as "must not crash". Things that exist and stay as they are |
| `specification` | The design, Overview | The approach, the main trade-off, what happens on failure | Ticket detail, test detail |
| `comparison[]` | The design, Before and after | One row for each situation the owner will notice | Anything else about current behavior. This table is its only home |
| `boundaries[]` | The design, Constraints | What exists and must stay as it is | Things that are not built. Those are non-goals |
| `decisions` | Alternatives considered | One paragraph for each decision: what was chosen, what it was chosen over, and why | A non-goal again. An invented alternative or reason |
| `risks` | Cross-cutting concerns | One paragraph for each risk or limit that applies across the design. Security, privacy and observability when the records say something about them | A constraint again. An invented statement |
| `testing` | The work, How it is tested | The test approach | Each check again |
| `tickets[]` | The work, one card each | See the fields table | |

## Layout

A report with `task_report` uses the owner's report design (`assets/report-style.css` and `assets/report-extra.js`, used unchanged; `report-style-compat.css` maps the older token names the screen diagram uses; `report-style-plan.css` holds the few additions for this layout). Reports without `task_report` keep the earlier layout unchanged.

0. Header: masthead (project and revision), title, the `understanding` lead, then one box with the status tag and status sentence and one "Read first" line for each `attention` row. The status sentence is built from the agreement status and the phase (planning: plan state such as "Waiting for your OK on this plan"; progress: checkpoint implementation/verification and next action; delivery: "Delivered: complete/partial/blocked"). The at-a-glance row shows tickets and checks verified, the open questions only when there are any, and the as-of date when a checkpoint has one. No tile repeats the masthead or shows an empty value.
1. Context and scope: the agreement summary, then the request section.
2. Goals and non-goals: two lists side by side. An older report shows its one agreement text here.
3. The design: Overview (specification), the diagrams, Before and after (the comparison rows as situation, today and after the change, without traceability links), Constraints (boundaries).
4. Alternatives considered: the decisions section, one item for each paragraph.
5. Cross-cutting concerns: the risks section, then evidence limits and open questions only when there are any.
6. The work: one summary line in planning, the delivery, testing and milestones sections, then one card per ticket. A card has the title, the description (specification, then expected), "Done when" with the acceptance items of the ticket, "Touches" with its files, and any outcome. Each acceptance item is listed in full under the first ticket that names it, with how it is checked and its result; another ticket that names it shows one line that links to it. An acceptance item that no ticket names is listed after the cards. "Depends on" is shown only when the order is not a straight line, that is when some ticket depends on something other than the ticket before it. Checks and reviews follow (status, expected, observed, limits, command).
7. Reference (collapsed): provenance note, agreement record and response, plan approval record, checkpoint, revision history, one requirements table (requirement, source, the tickets and checks that cover it), one table with the reason, evidence and dependencies of each ticket, the evidence behind the before and after rows, source attribution for every sourced object under the label the page shows, evidence, node/edge records and source fingerprints.

A numbered contents list links sections 1 to 6 and highlights the one being read.

Rules for every part:

- Say each fact once. Link to it from elsewhere.
- Address the owner as "you". The agent is "the agent".
- Leave out a heading, tile, table or list that would be empty.
- Refer to a section by the title the page shows.

## Progress and delivery

Use `report_kind: task-overview` with the existing sourced checkpoint for delivery. Include every acceptance result, the final delivery section and an explicit completion state. Complete is permitted only with implemented work, applicable agreement/plan authority (approved, waived, legacy or not-required), every acceptance verified or superseded with at least one verified, every recorded check passed including at least one review, every task outcome terminal (verified/removed/superseded/not-applicable), every requirement covered by an acceptance item, no open decision and checkpoint verification passed. Partial/blocked output is valid and must explain unfinished or unverified work. An owner waiver, unavailable environment or known limitation cannot be disguised as verified completion.

The delivery section explains requested/agreed/implemented work, completed and open tickets, changed files/components, check and review outcomes, known limitations and follow-ups. Link exact evidence through checks and acceptance_results. Actual UI design acceptance and release readiness remain separate when relevant; reuse the existing UI screen-flow and kit source contract.

Snapshot timing follows VISUAL-REVIEW.md "Saved reports are snapshots"; delivery reuse follows workflow-deliver step 8. Progress updates normally remain in the records. Plan revision changes only when the agreement changes; a new dated progress snapshot may project the same plan revision. Before naming the final report in task records, run `render_report.py --root <root> --input <json> --validate-input`. Fix errors in the same input until it passes. Record the final destination, run preflight again against the final source records, then render once. An older draft may use `--replace-unpresented` only while unpresented, unapproved and unnamed in source records (no `-v2`/`-v3` copies). A failed opening does not remove those protections. Once the user has seen it, a change gets a new file. The renderer refuses the replacement when a supplied source file names the report (a planned path in those records is also protected) or the report is approved. It runs the wording check before it writes. Wording problems never block a valid report, but `--open` waits until none remain.

## Verification

Validate through render_report.py and its freshness check. Inspect actual rendering at desktop and narrow widths, section navigation and long content. Check every displayed claim against its cited record and actual execution.
