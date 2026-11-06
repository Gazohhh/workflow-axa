# Workflow AXA — 2.8.0-rc.16

## Current update: report input preflight

The report renderer now checks input with `--validate-input` before creating a file. It checks schema, sources and wording without files, Python caches or browser opening. Report producers record the final path and approval-wait checkpoint before their final check and render. Existing rendering and protected report replacement stay unchanged.

Release metadata now matches the package version. The parallel record test handles workers that refuse a busy lock before reading stdin and always reaps its children. Authored host scenarios remain unrun until actual host evidence exists. See VALIDATION.md for current checks and limits.

## Earlier candidate: explicit revision naming

Plans now document the existing r1, r2 naming convention. Historical labels can be reconciled with explicit owner authority while preserving the original report and approval words. The hook is unchanged; native Claude recovery passed in the Hooqd evaluation. Broader project acceptance remains partial.

## Earlier candidate: approval wording and transcript compatibility

Implementation approval can coexist with pending visual acceptance. The gate now separates checkpoint status from the quoted answer while preserving provenance, fingerprints and refusal/withdrawal checks. The retro digest accepts modern host records. Local regression tests and a native Claude scoped-write test pass. Broader project evaluation remains partial.

## Earlier candidate: framework references and setup routing

Live evaluation exposed two helper failures: React component names were rejected as element references, and screenshot timeouts escaped as exceptions. References now preserve source component names as inert text, and a timeout returns a clear failure while preserving completed captures. A setup answer explicitly routes through rule-maker. The five-project evaluation remains in progress; these changes do not grant approval or prove complete visual coverage.

## Earlier candidate: source-backed design-kit examples

Approved kit work can add small framework examples that reuse real components and existing markup patterns. Check variants against their renderers and real callers, and capture settled presentation states. Setup still requires implementation approval. No new styling or preview dependencies are introduced. The five-project Claude Code evaluation is pending; package checks do not establish live behavior.

## Earlier candidate: approval recovery and quiet waiting

The rc.4 candidate added registration protocol checks, precise revision parsing, workspace-bound report approval, completed-question presentation evidence and reliable whole-read checks. Approval waits end without workflow Stop feedback. External host goals require the recovery in `skills/workflow/TASK-FOLDER.md`; this package cannot cancel another Stop evaluator. CANDIDATE-REVIEW.md and VALIDATION.md preserve that checkpoint's evidence and limits.

## Earlier candidate: readable tickets and bounded permissions

Full replacement of the available rc.2 source bundle. This candidate addresses the owner's supplied TODO/protocol and reported live-trial gaps without redesigning the workflow. See [candidate review](CANDIDATE-REVIEW.md), [validation](VALIDATION.md), [upgrade](UPGRADE.md), and [six targeted live cases](RC3-CASES.md).

- Readable labelled tickets; legacy checkboxes and revision-qualified IDs remain supported. Implemented is not verified; missing device acceptance and owner-removed work are not test passes.
- Explicit paid-evaluation budgets include orchestration, child calls and the retro. Vague reassurance, unresolved placeholders and agent proposals do not grant a cap. No billing enforcement is claimed.
- D14 reuse remains: never write CSS. Do not recommend plain HTML or infer its scoped exception from a blanket yes.
- Reconcile evidenced legacy report approvals without inventing revision IDs. Unresolved authority goes to a focused question, never a suggestion to bypass the hook.
- Partial-read warnings resolve the actual installed root, including Git Bash paths, arbitrary release names and quoted spaces.

No new skill, external dependency, global installation or project migration. Existing reports/styles, pinned specialists and task-history files remain unchanged. The owner reported that the older baseline was overwritten: test this candidate by itself unless a separate trusted comparison copy is available and approved. D7–D10 and prior delivery acceptance are not answered by this release.

## Start here

1. Type `/workflow` (plugin: `/workflow-axa:workflow`) followed by what you want. That's the only command you need.
2. It reads the code and asks you the questions only you can answer. The first run in a project may stop once to offer rule setup.
3. **Pause 1:** it describes what will be built. Reply "agree" or say what to change.
4. **Pause 2:** it shows the tickets and an HTML plan. Reply "approve" or say what to change. Small, settled changes ask both at once; an explicit waiver requires a task/revision-bound plan in chat and the whole actual answer. It is not an agent-selected shortcut.
5. It builds ticket by ticket with tests and reviews, then gives a delivery report: what was done, what was checked, what still needs you.

The other skills in your `/` menu are parts of `/workflow`; you rarely need to type them (`task-status` for where things stand, `retro` for a look back at past sessions).

Full replacement package: **21 skills** (12 workflow-axa skills plus 9 vendored: eight of Matt Pocock's and `simple-english`; the list is in `.claude-plugin/plugin.json`), shared version-aware rules, rules-readiness, proactive grilling, approved flowchart reports, recoverable records and the artifact policy.

## This update: `/workflow` routes to four phase skills

`/workflow` is now a small coordinator. It finds the task, checks rules readiness, reads the task's records and hands over to the phase skill those records call for. Each phase owns its procedure and entry conditions. Direct invocation must satisfy the same conditions; this is an instruction requirement, not proof of equal live-host enforcement.

| Phase skill | What it does | Ends with |
|---|---|---|
| `workflow-clarify` | Traces real journeys, callers, failure and compatibility paths in current code, then asks only the user decisions that remain open | **Gate one — agreement** on behavior, scope, exclusions, journeys, acceptance and assumptions (PLAN plus a chat summary) |
| `workflow-specify` | Cuts the agreement into vertical tickets with dependencies, ownership, acceptance and test seams | **Gate two — implementation approval** of the specification, tickets, test strategy and HTML report |
| `workflow-execute` | Builds ready tickets, in parallel when their files don't overlap: test-first where agreed, ticket review on Standards and Spec, repair, integration checks, then a whole-feature review | A ticket ledger with evidence, handed to delivery |
| `workflow-deliver` | Checks every requirement, required check, changed file and review against current evidence; routes defects back instead of fixing them | The delivery record and an honest final report: verified, partial, not verified or waived |

**Two gates, not one.** Agreement permits the detailed plan, never code. Only gate two permits application code and tests. Answering grilling, opening the report or a generic “go” on an unseen plan approves neither. A later material change reopens only the affected agreement items or tickets; unrelated approved work continues. Tasks approved under the earlier single gate keep that authority for their recorded scope; nothing is re-asked or rewritten. Genuinely lightweight, exact, low-risk edits keep their short route; a small behavior or architecture change is not lightweight because few files change. Gate definitions: [VISUAL-REVIEW.md](skills/workflow/VISUAL-REVIEW.md).

**Writing.** Human-facing prose still follows the existing [WRITING.md](skills/workflow/WRITING.md), now with a meaning-preservation check and a cold-reader reconstruction test. Skills and agent instructions follow the bundled `writing-for-agents` for structure. No new writing skill, linter or other dependency is added.

**Central report (optional).** A schema-2 report may carry an additive `task_report` object: request, agreement, specification, per-ticket specifications, decisions, risks, checks, acceptance results and delivery, each citing its source record. PLAN/TODO/FINDINGS/DECISIONS stay authoritative; the report is a dated projection, not approval. Reports without `task_report` render as before. Contract: [TASK-REPORT.md](skills/codebase-map/TASK-REPORT.md).

`workflow-execute` adapts Implement Spec's ticket-graph method locally. It never branches, commits, merges or touches a tracker, and it does not invoke or alter the upstream skill. The four phase skills read the shared policies in the installed `workflow` folder, so they need the whole package, not a single copied folder. **Bundled specialists.** Matt Pocock's `grilling`, `tdd`, `code-review`, `writing-for-agents`, `codebase-design` and `domain-modeling` (plus `implement-spec` and `retro` as references) ship as separate skills in this package (plugin names `workflow-axa:<name>`), copied at a pinned commit under their MIT license ([VENDORED-SKILLS.md](VENDORED-SKILLS.md)). `simple-english` (AminBlg/SimpleEnglish, MIT) ships the same way; the workflow uses it for every HTML report and delivery message. Each keeps the upstream text and ends with a workflow-axa adaptation. The phases load these sibling skills, so an upstream change, a removed skill or a host's same-named command can't change the workflow; `tools/vendor_specialists.py` regenerates them after a reviewed upstream update. Optional installed specialists (`research`, `diagnosing-bugs`, `prototype`, `pr`, `wizard`) block only the step that needs them. This candidate also contains rc.8's Windows verification fixes.

## UI policy (2.8, owner decision D14): never write CSS; reuse existing classes

Agents **never create, modify or inject CSS**: no stylesheet rules, no `<style>` blocks, no `style=""`. They use only classes and IDs that already exist in the project's stylesheets or HTML: the design kit when there is one, otherwise the existing code. A new element copies both the class name and the HTML tag of the existing element it imitates. Existing components are reused through their API, never rebuilt from their DOM.

| Situation | Behaviour |
|---|---|
| Existing interface logic fix | Keep its markup and appearance; change only the agreed behaviour. |
| New or changed element | Search the design kit (if any) and the existing code for an element with the same purpose; mirror its class and tag; record it as `file:line`. |
| Nothing matches | Stop that element and ask: "I couldn't find a matching style for [element]. Is there an existing element I should mimic?" |
| You explicitly instruct plain HTML for the named element, or directly confirm no similar element in answer to its mimic question | Add only that element without classes/styling; record the question and full answer. The agent must not recommend plain HTML or infer this exception from a blanket yes. |
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

Replace the complete plugin or all **21 complete skill folders** together (the list in `.claude-plugin/plugin.json`): `workflow`, `codebase-map`, `task-status`, `resume-task`, `workflow-doctor`, `plan-review`, `rule-maker`, `ui-design`, `workflow-clarify`, `workflow-specify`, `workflow-execute`, `workflow-deliver`, and the vendored `grilling`, `tdd`, `code-review`, `writing-for-agents`, `codebase-design`, `domain-modeling`, `implement-spec`, `retro` and `simple-english`. Keep them as siblings from the same version; a phase skill without its matching `workflow` folder stops and reports the gap. Preserve separately installed Matt skills and actual user modifications after review. Use one stable active installation, start fresh sessions, then check from the installed package:

```bash
python -X utf8 skills/rule-maker/scripts/audit_installation.py --check-global
python -X utf8 skills/rule-maker/scripts/activate_rules.py --check
```

These read-only checks do not repair settings or prove loading. Existing correct references remain valid when the install path stays fixed. For missing references, use the activation helper's preview/apply procedure after reviewing it. No host hook, auto-updater or tool sandbox is installed.

## Checks and release (source checkout)

The release ZIP holds what an installation needs: `.claude-plugin/`, the registered skills, `hooks/`, `LICENSE`, `docs/DESIGN.md` and these documents. It leaves out `tests/`, `tools/`, task records (`docs/plans/`) and evaluation output, so run the checks from a clone of the repository:

```bash
python -X utf8 -m unittest discover -s tests -p "test_*.py"
python -X utf8 -I tools/validate.py
python -X utf8 -I tools/verification_summary.py --run --write VALIDATION.md
python -X utf8 -I tools/build_release.py
```

`validate.py` also fails when this README, the current CHANGELOG entry, UPGRADE or VENDORED-SKILLS state a skill count or a package or rules version that differs from the manifests. `verification_summary.py` rewrites only VALIDATION's current section; browser, visual and host checks stay NOT_RUN unless you pass their results. `build_release.py` writes `workflow-axa-<version>.zip` with sorted entries and fixed timestamps, prints its files and SHA-256, and refuses files whose names look like secrets (a name check only: it does not scan file contents). It writes to `dist/` when Git ignores that folder, otherwise to `.artifacts/release/`. The project's own code is MIT licensed ([LICENSE](LICENSE)); vendored skills keep their own licence files.

[Upgrade guide](UPGRADE.md) · [Validation](VALIDATION.md) · [Central report contract](skills/codebase-map/TASK-REPORT.md) · [Strict reuse scenarios](tests/behavioral/STRICT-KIT.md) · [UI report contract](skills/codebase-map/UI-FLOW.md).

## Compatibility and limits

Non-UI report behaviour is unchanged; `task_report` is optional and additive. Historical HTML and task files remain intact. Old UI draft/illustration inputs remain readable, but old permissive modes cannot generate a newly approval-ready application report; add real kit selections/capture provenance instead. JSON is optional as the authoritative kit format: existing Markdown catalogues can be projected inside the report input without another maintained file.

Original rc.6 HTML samples remain as **historical schematic demonstrations, not the current permission policy or project-kit evidence**. See their example README. No replacement styled application sample is manufactured in this release.

Test and validator results, with the commit and environment they ran on, are in the "Current verification" section of [VALIDATION.md](VALIDATION.md); older results there are history. Recorded results concern observed tooling only. Live Claude/Codex/T3 compliance and real project-kit execution are not established here. A model can still disobey instructions; no absolute guarantee is claimed. No application source, real kit, user profile, memory or project instructions were changed by creating this archive.
