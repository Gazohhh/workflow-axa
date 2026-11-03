# Specialists

The workflow coordinates; specialists supply the discipline for one kind of work. Use the route below, not a homemade substitute. Load only the specialist the current step needs.

## This package's own (always available)

Copies of Matt Pocock's skills, shipped as separate skills in this package (plugin names `workflow-axa:<name>`), each ending with a **workflow-axa adaptation** section. Phases load them from their sibling folders, so an upstream change, a removed skill or a same-named skill installed elsewhere (or a host's built-in `code-review`) can't change the workflow. Provenance and updating: VENDORED-SKILLS.md at the package root.

| When | Read | Used by |
|---|---|---|
| Every new substantive goal or material change; any new consequential choice | `grilling` (`../grilling/SKILL.md`) | `workflow-clarify` step 2 |
| Test-first work at an agreed seam | `tdd` (`../tdd/SKILL.md`) | `workflow-execute` step 4 |
| Reviewing code changes (Standards and Spec, kept separate) | `code-review` (`../code-review/SKILL.md`) | `workflow-execute` steps 6 and whole-feature review |
| Writing or reviewing skills and agent instructions | `writing-for-agents` (`../writing-for-agents/SKILL.md`) | reviews of instruction changes |
| An interface, seam or module boundary is in question | `codebase-design` (`../codebase-design/SKILL.md`) | `workflow-specify` step 1 |
| A term, owner or domain boundary is unclear or changing | `domain-modeling` (`../domain-modeling/SKILL.md`) | any phase |
| Ticket-graph execution (reference for the local adaptation) | `implement-spec` (`../implement-spec/SKILL.md`) | `workflow-execute` (never run as written) |
| A retrospective over one or many sessions, when the user asks | `retro` (`../retro/SKILL.md`) | user-invoked |

A detailed prompt is not an exemption from grilling; an unchanged approved task is not re-interviewed.

## Optional installed specialists

These stay external; use them only when installed, and never install them yourself ([SETUP.md](SETUP.md)). Check availability when a step needs one; a missing one blocks only that step: say so once, record it, and continue independent work or ask for an approved fallback. Use the qualified name the host shows: an unrelated skill with the same name is not this one.

| When | Invoke | Boundaries |
|---|---|---|
| External research: docs, APIs, primary sources | `research` | Cited findings go to FINDINGS. No second report. Promise no background result. |
| A bug, failure or performance regression needs a diagnosis | `diagnosing-bugs` | Authorize diagnostic writes first; no production probes, destructive commands, fixes or installs beyond approval. No reproduction means no verified cause. |
| The user authorizes a throwaway prototype | `prototype` | Bounded files and cleanup in the plan; strict UI reuse still applies; no commit or production integration. |
| A pull-request description is requested | `pr` | Draft from real evidence; never open, publish or merge without separate permission. |
| An approved procedure needs human-run setup steps | `wizard` | Only approved stages; the human runs interactive steps; protect secrets. |

Before each call, pass: task and approval paths, the exact question or work unit, settled answers, allowed writes, relevant files or diff, output location ([ARTIFACTS.md](ARTIFACTS.md)) and applicable rules (RULES.md, with any exact exception). Only the task owner writes task records; specialists and subagents return evidence. Without subagents, run sequentially and label a self-review as such.

[specialists.json](specialists.json) lists the upstream catalogue for teams that also install Matt's skills; the read-only [checker](scripts/check_specialists.py) inventories installed roots. Installed is not invoked, and invoked is not a correct result.

## Manual workflows are never chained in

`grill-me`, `implement`, `implement-spec`, `to-spec`, `to-tickets`, setup and handoff are user-run workflows upstream; some commit or publish to a tracker. Don't call them automatically or strip their invocation flags. PLAN/TODO stay the records. When the user asks, mirror progress to their tracker as one generated update from the records; never keep a second list by hand. If the user explicitly chooses one, confirm only the integration boundaries that are still open.

`workflow-execute` owns this package's local adaptation of Implement Spec.

## Local routes

- **Phase skills** `workflow-clarify`, `workflow-specify`, `workflow-execute`, `workflow-deliver`: this package's procedures, picked by `workflow` or invoked directly.
- **`codebase-map`**: flowcharts and the HTML plan report ([VISUAL-REVIEW.md](VISUAL-REVIEW.md)). It never implements, approves, grills or calls back into the workflow. Don't use Matt's `improve-codebase-architecture` just to draw a flow.
- **`ui-design`**: load it before planning any application UI, even behavior-only UI changes. Its rule: never write CSS; reuse only classes/IDs that already exist (design kit or existing code), mirroring class and tag; when nothing matches, ask which existing element to mimic; plain unstyled HTML only on the user's explicit instruction. Pass its mode, approval source and preview limits to every worker. Code review checks markup, visual props and removed styling, not just CSS additions.
- **Optional helpers** (skill-creator, webapp-testing): [OPTIONAL-HELPERS.md](OPTIONAL-HELPERS.md); never prerequisites.

Every route: pass the output folder and protected paths from ARTIFACTS.md; each worker cleans only its own scratch. If the host can't apply a specialist's boundaries without conflict, don't run it unchanged: record the conflict and confirm a fallback with the user.
