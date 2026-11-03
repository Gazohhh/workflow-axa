# Workflow AXA — 2.8.0-rc.1

## Start here

1. Type `/workflow` (plugin: `/workflow-axa:workflow`) followed by what you want. That's the only command you need.
2. It reads the code and asks you the questions only you can answer. The first run in a project may stop once to offer rule setup.
3. **Pause 1:** it describes what will be built. Reply "agree" or say what to change.
4. **Pause 2:** it shows the tickets and an HTML plan. Reply "approve" or say what to change. Small, settled changes ask both at once; "I don't need to see the plan, go" skips this pause.
5. It builds ticket by ticket with tests and reviews, then gives a delivery report: what was done, what was checked, what still needs you.

The other skills in your `/` menu are parts of `/workflow`; you rarely need to type them (`task-status` for where things stand, `retro` for a look back at past sessions).

Full replacement package: **twenty skills** (twelve workflow-axa skills plus eight vendored from Matt Pocock), shared version-aware rules, rules-readiness, proactive grilling, approved flowchart reports, recoverable records and the artifact policy.

## This update: `/workflow` routes to four phase skills

`/workflow` is now a small coordinator. It finds the task, checks rules readiness, reads the task's records and hands over to the phase skill those records call for. Each phase skill owns its procedure, checks its own entry conditions and can be invoked directly; a direct call is as safe as going through `/workflow`.

| Phase skill | What it does | Ends with |
|---|---|---|
| `workflow-clarify` | Traces real journeys, callers, failure and compatibility paths in current code, then asks only the user decisions that remain open | **Gate one — agreement** on behavior, scope, exclusions, journeys, acceptance and assumptions (PLAN plus a chat summary) |
| `workflow-specify` | Cuts the agreement into vertical tickets with dependencies, ownership, acceptance and test seams | **Gate two — implementation approval** of the specification, tickets, test strategy and HTML report |
| `workflow-execute` | Builds ready tickets, in parallel when their files don't overlap: test-first where agreed, ticket review on Standards and Spec, repair, integration checks, then a whole-feature review | A ticket ledger with evidence, handed to delivery |
| `workflow-deliver` | Checks every requirement, required check, changed file and review against current evidence; routes defects back instead of fixing them | The delivery record and an honest final report: verified, partial, not verified or waived |

**Two gates, not one.** Agreement permits the detailed plan, never code. Only gate two permits application code and tests. Answering grilling, opening the report or a generic “go” on an unseen plan approves neither. A later material change reopens only the affected agreement items or tickets; unrelated approved work continues. Tasks approved under the earlier single gate keep that authority for their recorded scope; nothing is re-asked or rewritten. Genuinely lightweight, exact, low-risk edits keep their short route; a small behavior or architecture change is not lightweight because few files change. Gate definitions: [VISUAL-REVIEW.md](skills/workflow/VISUAL-REVIEW.md).

**Writing.** Human-facing prose still follows the existing [WRITING.md](skills/workflow/WRITING.md), now with a meaning-preservation check and a cold-reader reconstruction test. Skills and agent instructions follow the bundled `writing-for-agents` for structure. No new writing skill, linter or other dependency is added.

**Central report (optional).** A schema-2 report may carry an additive `task_report` object: request, agreement, specification, per-ticket specifications, decisions, risks, checks, acceptance results and delivery, each citing its source record. PLAN/TODO/FINDINGS/DECISIONS stay authoritative; the report is a dated projection, not approval. Reports without `task_report` render as before. Contract: [TASK-REPORT.md](skills/codebase-map/TASK-REPORT.md).

`workflow-execute` adapts Implement Spec's ticket-graph method locally. It never branches, commits, merges or touches a tracker, and it does not invoke or alter the upstream skill. The four phase skills read the shared policies in the installed `workflow` folder, so they need the whole package, not a single copied folder. **Bundled specialists.** Matt Pocock's `grilling`, `tdd`, `code-review`, `writing-for-agents`, `codebase-design` and `domain-modeling` (plus `implement-spec` and `retro` as references) ship as separate skills in this package (plugin names `workflow-axa:<name>`), copied at a pinned commit under their MIT license ([VENDORED-SKILLS.md](VENDORED-SKILLS.md)). Each keeps the upstream text and ends with a workflow-axa adaptation. The phases load these sibling skills, so an upstream change, a removed skill or a host's same-named command can't change the workflow; `tools/vendor_specialists.py` regenerates them after a reviewed upstream update. Optional installed specialists (`research`, `diagnosing-bugs`, `prototype`, `pr`, `wizard`) block only the step that needs them. This candidate also contains rc.8's Windows verification fixes.

## UI policy (2.8, owner decision D14): never write CSS; reuse existing classes

Agents **never create, modify or inject CSS**: no stylesheet rules, no `<style>` blocks, no `style=""`. They use only classes and IDs that already exist in the project's stylesheets or HTML: the design kit when there is one, otherwise the existing code. A new element copies both the class name and the HTML tag of the existing element it imitates. Existing components are reused through their API, never rebuilt from their DOM.

| Situation | Behaviour |
|---|---|
| Existing interface logic fix | Keep its markup and appearance; change only the agreed behaviour. |
| New or changed element | Search the design kit (if any) and the existing code for an element with the same purpose; mirror its class and tag; record it as `file:line`. |
| Nothing matches | Stop that element and ask: "I couldn't find a matching style for [element]. Is there an existing element I should mimic?" |
| You explicitly allow plain HTML, or confirm nothing similar exists | Add that element as plain HTML with no classes and no styling; your words are recorded. |
| No design kit in the project | Same rules, with existing code as the only source. "No kit" never means "write CSS". |
| Ordinary prompt without /workflow | Same rules when the shared rules are loaded. Verify actual host loading; installation alone is not proof. |

Before finishing, the agent lists each class it used with the file that defines it and confirms no CSS was added.

**Every UI-visible change gets a screen diagram** in the HTML plan report: current and proposed screens with the interaction arrows, from real captures when they can be taken safely, otherwise a layout sketch labelled as a sketch. The report's own renderer is a narrow exception for report styling; it gives no permission to style the application.

## The project kit is real code, not another HTML mockup

[Live-kit guide](skills/ui-design/LIVE-KIT.md): use the project's existing framework components and adjacent examples. Generate its current catalogue and technical references through existing tooling. Keep project instructions short: catalogue location, owner and project constraints. Do not manually maintain several copies of a component/style inventory.

An optional **read-only local Storybook index inspector** reports selected example identities, missing sources and metadata changes. It does not install/run Storybook or discover every transitive import. [Kit workflow](skills/ui-design/KIT.md) supports audit/setup/check of existing sources. Actual Altinstar/Cheflabels kits are not supplied or invented by this package; connecting each real project's tooling is separately scoped work.

Human acceptance stays recorded once. Component edits can refresh current previews after rebuild; they do not renew approval or rewrite historical review captures. Deleted sources cause affected selection checks to fail, not a guessed replacement.

## Entry points

```text
/workflow-axa:workflow <goal>
/workflow-axa:workflow-clarify <task>
/workflow-axa:workflow-specify <task>
/workflow-axa:workflow-execute <task>
/workflow-axa:workflow-deliver <task>
/workflow-axa:rule-maker audit|setup|update
/workflow-axa:ui-design <UI task>
/workflow-axa:ui-design kit-audit|kit-setup|kit-check <area or catalogue>
/workflow-axa:workflow-doctor
/workflow-axa:task-status <task>
/workflow-axa:resume-task <task>
/workflow-axa:plan-review <task>
/workflow-axa:codebase-map explain|current|proposed|compare <scope>
```

Plugin syntax is shown; standalone names depend on the host. The main sequence is **rules readiness → find/reuse task → clarify (inspect current code, grilling, agreement: gate one) → specify (tickets, test seams, full HTML report: gate two) → execute (tickets, reviews, integration) → deliver (evidence reconciliation and final report)**. Each phase skill refuses to start without its prerequisites and names the phase that must run first. Kit setup or rule setup does not approve application changes. Backend work does not require a kit.

## Install and check

Replace the complete plugin or all **twenty complete skill folders** together: `workflow`, `codebase-map`, `task-status`, `resume-task`, `workflow-doctor`, `plan-review`, `rule-maker`, `ui-design`, `workflow-clarify`, `workflow-specify`, `workflow-execute`, `workflow-deliver`, and the vendored `grilling`, `tdd`, `code-review`, `writing-for-agents`, `codebase-design`, `domain-modeling`, `implement-spec` and `retro`. Keep them as siblings from the same version; a phase skill without its matching `workflow` folder stops and reports the gap. Preserve separately installed Matt skills and actual user modifications after review. Use one stable active installation, start fresh sessions, then check from the installed package:

```bash
python -X utf8 skills/rule-maker/scripts/audit_installation.py --check-global
python -X utf8 skills/rule-maker/scripts/activate_rules.py --check
```

These read-only checks do not repair settings or prove loading. Existing correct references remain valid when the install path stays fixed. For missing references, use the activation helper's preview/apply procedure after reviewing it. No host hook, auto-updater or tool sandbox is installed.

[Upgrade guide](UPGRADE.md) · [Validation](VALIDATION.md) · [Central report contract](skills/codebase-map/TASK-REPORT.md) · [Strict reuse scenarios](tests/behavioral/STRICT-KIT.md) · [UI report contract](skills/codebase-map/UI-FLOW.md).

## Compatibility and limits

Non-UI report behaviour is unchanged; `task_report` is optional and additive. Historical HTML and task files remain intact. Old UI draft/illustration inputs remain readable, but old permissive modes cannot generate a newly approval-ready application report; add real kit selections/capture provenance instead. JSON is optional as the authoritative kit format: existing Markdown catalogues can be projected inside the report input without another maintained file.

Original rc.6 HTML samples remain as **historical schematic demonstrations, not the current permission policy or project-kit evidence**. See their example README. No replacement styled application sample is manufactured in this release.

This candidate's package and test results are pending and will be recorded in [VALIDATION.md](VALIDATION.md); recorded results concern observed tooling only. Live Claude/Codex/T3 compliance and real project-kit execution are not established here. A model can still disobey instructions; no absolute guarantee is claimed. No application source, real kit, user profile, memory or project instructions were changed by creating this archive.
