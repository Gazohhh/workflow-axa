# Workflow AXA — 2.12.0

**One command:** `/workflow` (Claude plugin: `/workflow-axa:workflow`). The agent reads your repository, clarifies consequential choices, presents an offer and asks one question, then builds and checks the approved work. You can also ask it to **explain or review** code without creating task records or an offer.

## Start in 60 seconds

1. Ask what you want built, investigated or reviewed. Existing task records are reused.
2. For a substantive change, confirm the **behavior agreement**: what works, fails and stays unchanged. One-ticket work with no open choice skips this step, because the offer carries the agreement.
3. Read the **offer**: what changes, its paths and protected operations, what stays out and the checks. Answer the one question: *Show review.html first*, *Approve from this summary* or *Change something*. A lightweight edit's offer is one short message that asks only *Approve* or *Change something*. Click the answer, or type it after an offer shown as text. Only an approved offer lets application code change. The plan report, with current/proposed flows and real UI-kit references, is built when you ask for it.
4. Get a short result: implemented tickets, tests, review, remaining risks and anything requiring human acceptance.

Understand the system: [one-page architecture](docs/ARCHITECTURE.md). Test in new sessions: [fresh-run guide](docs/EVALUATION.md). Installation and migration: [UPGRADE.md](UPGRADE.md). Current proof and limits: [VALIDATION.md](VALIDATION.md).

## Current candidate: the offer model and a smaller package

Every change ends with an **offer** and **one question**. A lightweight edit gets the minimal offer (its files, its check and a one-line why); one-ticket work gets one ticket; larger work gets the full ticket list. The hook `hooks/approval.py` reads your answer from the conversation and lets through only the offer's paths and named operations. A later withdrawal or narrowing ends the approval; a stop only pauses it. Tasks approved before the offer model keep their Approval line when you list them with `legacy_inventory.py` at the upgrade ([UPGRADE.md](UPGRADE.md)). The plan report is built only when you ask for it. These changes have offline tests and a few live host runs; what is still unmet is listed in [CHANGELOG.md](CHANGELOG.md).

This repository has no CI workflow; run the checks below from a clone. Nothing here automatically installs a skill, launches a paid model or changes your real projects.

## Package contents

The other skills in your `/` menu are parts of `/workflow`; you rarely need to type them (`resume` for where things stand).

Full replacement package: **22 skills** (14 workflow-axa skills plus 8 that began as copies of other MIT projects and are now maintained here; the list is in `.claude-plugin/plugin.json`; credits in [VENDORED-SKILLS.md](VENDORED-SKILLS.md)), shared version-aware rules, rules-readiness, proactive grilling, approved flowchart reports, recoverable records and the artifact policy.

**Renamed skills (2.9.0).** No redirect skills are kept; use the new names:

| Old name | Now |
|---|---|
| `task-status` | `resume` (status mode) |
| `resume-task` | `resume` (continue mode; also `handoff`) |
| `workflow-doctor` | `rule-maker`, diagnose mode |
| `implement-spec` | `workflow-execute` (the copy is archived in `docs/archive/skills/`) |
| `retro` | archived; `tools/digest_sessions.py` stays in the source checkout (not in the release ZIP) |
| `simple-english` | reference text `skills/workflow/SIMPLE-ENGLISH.md` for Strict mode and CHECK requests; its plain-writing rules now live in `skills/workflow/WRITING.md` |

**New commands (2.9.0).** Only you start these:

- `/interrogate <plan | diff>`: two adversaries try to show a concrete failure; you get reproduced failures, unverified concerns and untested surfaces. It changes nothing.
- `/no-comments <files | diff>`: a reviewer gives each comment a verdict, you approve one offer, then deletions and reshapes are made without changing behavior.
- `/wait-what`: the last message again, in plain words, with the pending question unchanged. It never counts as an answer.
- `/spar <idea or decision> [quick|normal|thorough|N|until agreement <cap>] [<A> vs <B>] [keep a SPAR.md|conversation only]`: a fresh Claude and GPT spar with you about an idea or a decision until you can choose a next move. If you choose, it is kept in one readable SPAR.md; at the end you choose to turn it into a workflow plan, investigate an open question first, keep sparring, or leave it. It never implements. Set its default effort (normal until you change it) with `python -X utf8 -I skills/workflow/scripts/settings.py spar depth <effort>`.

`code-review` also checks comments and reader load, and adds a blast-radius step when anything outside the diff reads what changed. That step follows `skills/code-review/BLAST-RADIUS.md`: it proves the facts a change is safe because of as far as running code allows, or marks them unproven, and looks where a search stops. Planning records those safety assumptions, every recipe except new-project names the step, and "what could this break?" gets the same report as an inspection. The interrogate, no-comments, reader-load and wait-what ideas were adapted from pstack and Matt Pocock's skills without copying text. The blast-radius method and the Unslop tells (below) adapt pstack text under its MIT licence ([VENDORED-SKILLS.md](VENDORED-SKILLS.md)).

When the work makes something a person reads, such as a message, report, dashboard or document, code review, plan review and `/spar` start with an output read. A fresh reviewer sees only the finished output and who reads it, says which question each part answers, and names the obvious questions left out. The owner gets those in one question before delivery, except the ones that the agreement or the approved offer excludes in words. Agent instructions and rewordings that keep the content are left out. Rule, with its other cases (plans, no subagents): "Output read" in [AUDIT.md](skills/workflow/AUDIT.md).

## This update: `/workflow` routes to four phase skills

`/workflow` is now a small coordinator. It finds the task, checks rules readiness, reads the task's records and hands over to the phase skill those records call for. Each phase owns its procedure and entry conditions. Direct invocation must satisfy the same conditions.

| Phase skill | What it does | Ends with |
|---|---|---|
| `workflow-clarify` | Traces real journeys, callers, failure and compatibility paths in current code, then asks only the user decisions that remain open | **Agreement** on behavior, scope, exclusions, journeys, acceptance and assumptions (PLAN plus a chat summary) |
| `workflow-specify` | Cuts the agreement into vertical tickets with dependencies, ownership, acceptance and test seams | The **offer** and the one question; the owner's answer is the implementation approval |
| `workflow-execute` | Builds ready tickets, in parallel when their files don't overlap: test-first where agreed, ticket review on Standards and Spec, repair, integration checks, then a whole-feature review | A ticket ledger with evidence, handed to delivery |
| `workflow-deliver` | Checks every requirement, required check, changed file and review against current evidence; routes defects back instead of fixing them | The delivery record and an honest final report: verified, partial, not verified or waived |

**The offer and the one question.** Agreement permits the offer, never code. Only the owner's answer to the one question approves an offer, and only an approved offer permits application code and tests. A later material change reopens only the affected agreement items or tickets; unrelated approved work continues. Tasks approved before the offer model keep that authority for their recorded scope when the owner listed them in the legacy inventory; nothing is re-asked or rewritten. A lightweight edit still gets the minimal offer; a small behavior or architecture change is not lightweight because few files change. Definitions: [VISUAL-REVIEW.md](skills/workflow/VISUAL-REVIEW.md).

**Writing.** Human-facing prose still follows the existing [WRITING.md](skills/workflow/WRITING.md), with a meaning-preservation check, a required Unslop check against the numbered tells in the same file, and a cold-reader reconstruction test. The Unslop check never rewrites application UI text, error messages or translations. An outside source named for a method, formula, number, threshold or standard carries its URL (offline: file and page) and the words read there, or says unverified, also in question cards and offers. Skills and agent instructions follow the bundled `writing-for-agents` for structure. No new writing skill, linter or other dependency is added.

**Central report (optional).** A schema-2 report may carry an additive `task_report` object: request, agreement, specification, per-ticket specifications, decisions, risks, checks, acceptance results and delivery, each citing its source record. PLAN/TODO/FINDINGS/DECISIONS stay authoritative; the report is a dated projection, not approval. For new drafts, `skills/codebase-map/scripts/record_projection.py` can freeze exact headings and labeled tickets into report text and check drift without overwriting a snapshot. Reports without `task_report` render as before. Contract: [TASK-REPORT.md](skills/codebase-map/TASK-REPORT.md).

`workflow-execute` owns ticket execution. It never branches, commits, merges or touches a tracker. The four phase skills read the shared policies in the installed `workflow` folder, so they need the whole package, not a single copied folder. **Bundled specialists.** `grilling`, `tdd`, `code-review`, `writing-for-agents`, `codebase-design` and `domain-modeling` ship as separate skills in this package (plugin names `workflow-axa:<name>`). The plain-English rules (formerly `simple-english`) live in `skills/workflow/WRITING.md`, which the workflow uses for every report and delivery message; `skills/workflow/SIMPLE-ENGLISH.md` keeps the Strict and CHECK modes. Each is one text maintained in this package and keeps its MIT `LICENSE` (VENDORED-SKILLS.md). The phases load these sibling skills, so a removed skill or a host's same-named command cannot change the workflow. Optional installed specialists named in `skills/workflow/SPECIALISTS.md` (`research`, `diagnosing-bugs`, `prototype`, `pr`, `wizard`) block only the step that needs them, and are checked only when that step runs. This candidate also contains rc.8's Windows verification fixes.

## UI policy: the CSS switch, off by default; reuse existing classes

Each machine has one CSS switch in `~/.workflow-axa/settings.json`, and it starts off. While it is off, agents write no CSS, and the hook refuses a styling write. Only your Yes to the exact question turns it on (`python -X utf8 -I <workflow>/scripts/settings.py css on`); a project's DESIGN.md with `css: never` keeps it off there. Either way, agents reuse only classes and IDs that already exist in the design kit or the existing code, mirroring the class and tag of the element they imitate, and ask which element to mimic when nothing matches. The full rules, including the plain-HTML exception and ordinary prompts without /workflow, are in the shared [DESIGN.md](skills/rule-maker/rules/DESIGN.md).

**Every UI-visible change gets a screen diagram** in the plan report, whenever one is built: current and proposed screens with the interaction arrows, from real captures when they can be taken safely, otherwise a layout sketch labeled as a sketch. The report's own renderer is a narrow exception for report styling; it gives no permission to style the application.

## The project kit is real code, not another HTML mockup

[Live-kit guide](skills/ui-design/LIVE-KIT.md): use the project's existing framework components and adjacent examples. Generate its current catalog and technical references through existing tooling. Keep project instructions short: catalog location, owner and project constraints. Do not manually maintain several copies of a component/style inventory.

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
/workflow-axa:rule-maker diagnose
/workflow-axa:resume status|continue|handoff <task>
/workflow-axa:interrogate <plan | diff>
/workflow-axa:no-comments <files | diff>
/workflow-axa:wait-what
/workflow-axa:spar <idea or decision> [quick|normal|thorough|N|until agreement <cap>] [<A> vs <B>] [keep a SPAR.md|conversation only]
/workflow-axa:plan-review <task>
/workflow-axa:codebase-map explain|current|proposed|compare <scope>
```

Plugin syntax is shown; standalone names depend on the host. The main sequence is **rules readiness → find/reuse task → clarify (inspect current code, grilling, agreement) → specify (tickets, test seams, the offer and the one question: implementation approval) → execute (tickets, reviews, integration) → deliver (evidence reconciliation and final report)**. Each phase skill refuses to start without its prerequisites and names the phase that must run first. Kit setup or rule setup does not approve application changes. Backend work does not require a kit.

## Install and check

Replace the complete plugin or all **22 complete skill folders** together (the list in `.claude-plugin/plugin.json`): `workflow`, `codebase-map`, `resume`, `plan-review`, `rule-maker`, `ui-design`, `workflow-clarify`, `workflow-specify`, `workflow-execute`, `workflow-deliver`, and the bundled `grilling`, `tdd`, `code-review`, `writing-for-agents`, `codebase-design` and `domain-modeling`, the user commands `interrogate`, `no-comments`, `wait-what` and `spar`, and the app-checking skills `verify-app` and `reproduce-bug`. Keep them as siblings from the same version; a phase skill without its matching `workflow` folder stops and reports the gap. Preserve separately installed skills and actual user modifications after review. Use one stable active installation, start fresh sessions, then check from the installed package:

```bash
python -X utf8 skills/rule-maker/scripts/audit_installation.py --check-global
python -X utf8 skills/rule-maker/scripts/activate_rules.py --check
```

These read-only checks do not repair settings. What these checks do not prove: [docs/EVALUATION.md](docs/EVALUATION.md). Existing correct references remain valid when the install path stays fixed. For missing references, use the activation helper's preview/apply procedure after reviewing it. These check commands install no hook, auto-updater or tool sandbox; the plugin's own hooks stay registered through `hooks/hooks.json`.

**Skill descriptions missing from the skill list.** Claude Code gives the skill list a total budget of about 1% of the context window. When many plugins are installed, it drops the descriptions of the least-used skills and shows only their names. A workflow-axa skill then still loads by name, but the agent may not pick it on its own. To fix this, raise `skillListingBudgetFraction` in your Claude Code settings, or use the `skillOverrides` setting with `"name-only"` for plugins you rarely use. Both are your own settings; this package does not change them.

## Checks and release (source checkout)

The release ZIP holds what an installation needs: `.claude-plugin/`, the registered skills, `hooks/`, `LICENSE`, `docs/DESIGN.md`, `docs/ARCHITECTURE.md`, `docs/EVALUATION.md`, `README.md`, `CHANGELOG.md`, `UPGRADE.md`, `VALIDATION.md` and `VENDORED-SKILLS.md`. It leaves out `tests/`, `tools/`, task records (`docs/plans/`) and evaluation output, so run the checks from a clone of the repository:

```bash
python -X utf8 -m unittest discover -s tests -p "test_*.py"
python -X utf8 -I tools/validate.py
python -X utf8 -I tools/verification_summary.py --run --write VALIDATION.md
python -X utf8 -I tools/build_release.py
```

`validate.py` also fails when this README, the current CHANGELOG entry, UPGRADE or VENDORED-SKILLS state a skill count or a package or rules version that differs from the manifests. `verification_summary.py` rewrites only VALIDATION's current section; browser, visual and host checks stay NOT_RUN unless you pass their results. `build_release.py` writes the installable `workflow-axa-<version>.zip` with sorted entries, fixed timestamps and filename-based secret checks (not a content scan). The project's own code is MIT licensed ([LICENSE](LICENSE)); the formerly copied skills keep their own license files. Credits: [VENDORED-SKILLS.md](VENDORED-SKILLS.md).

[Upgrade guide](UPGRADE.md) · [Validation](VALIDATION.md) · [Central report contract](skills/codebase-map/TASK-REPORT.md) · [Strict reuse scenarios](tests/behavioral/STRICT-KIT.md) · [UI report contract](skills/codebase-map/UI-FLOW.md).

## Compatibility and limits

Non-UI report behavior is unchanged; `task_report` is optional and additive. Historical HTML and task files remain intact. Old UI draft/illustration inputs remain readable, but old permissive modes cannot generate a newly approval-ready application report; add real kit selections/capture provenance instead. JSON is optional as the authoritative kit format: existing Markdown catalogs can be projected inside the report input without another maintained file.

Original rc.6 HTML samples remain as **historical schematic demonstrations, not the current permission policy or project-kit evidence**. See their example README. No replacement styled application sample is manufactured in this release.

Test and validator results, with the commit and environment they ran on, are in the "Current verification" section of [VALIDATION.md](VALIDATION.md); older results there are history. What these results do not prove: [docs/EVALUATION.md](docs/EVALUATION.md). No application source, real kit, user profile, memory or project instructions were changed by creating this archive.
