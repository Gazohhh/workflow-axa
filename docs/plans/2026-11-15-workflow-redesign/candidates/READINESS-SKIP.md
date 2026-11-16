# Candidate text: rules readiness becomes "set up / skip for this task" (activate at T17)

Candidate-only under the §14 transition rule: written and reviewed in T11, not referenced by any active file, applied together with the offer checker at the T17 cutover. Each block is an exact replacement; T17 applies them and runs the rules tests. Contract C-RULES-1.

## skills/rule-maker/rules/READINESS.md — §3 state table, row NEEDS_SETUP

Old:
> | NEEDS_SETUP | Known, bounded rule coverage is absent/incomplete. Ask the user to choose setup, limited exception, read-only inspection or stop. |

New:
> | NEEDS_SETUP | Known, bounded rule coverage is absent/incomplete. Name the gaps and ask one question: *Set up rules now* (recommended) or *Skip for this task*. Read-only work continues while the owner decides; only writes wait. |

## skills/rule-maker/rules/READINESS.md — "The missing-rules message"

Old: the paragraph beginning "> I found the shared standards, but this project has no established instructions" through "Which do you choose?"

New:
> I checked the project rules. Missing for this task: <the named gaps, for example "no test command, no ownership notes">. The rules that exist still apply.
>
> *Set up rules now* (recommended) or *Skip for this task*?

## skills/rule-maker/rules/READINESS.md — §4 heading and first sentence

Old: `## 4. A limited exception is not "ignore rules"` and "Record in the existing task/checkpoint or, for a no-file request, the current conversation: approving response, reason, exact omitted requirements, …"

New: `## 4. Skip for this task is not "ignore rules"` and "*Skip for this task* records a limited exception: in the existing task/checkpoint or, for a no-file request, the current conversation: the owner's answer, the exact named gaps it waives, the task and its root/worktree, and that it ends with the task. Existing project rules, protections, ownership and approved commands stay binding. Silence, "looks good" or an earlier approval is not a skip. Delivery names the actual gaps (for example "verification commands were not established"), not a generic "no rules"."

## skills/rule-maker/rules/START.md — readiness sentence

Old: "Missing prerequisites produce a clear stop, not invented conventions."

New: "Missing rules lead to the readiness question (set up now, or skip for this task), never to invented conventions; read-only work continues while it is open."

## skills/workflow/SKILL.md — §1

Old: "If missing: offer setup, limited exception, read-only inspection or stop."

New: "If rules are missing or weak: name the gaps and ask *Set up rules now* or *Skip for this task*; read-only work continues meanwhile, writes wait for the answer."

## skills/workflow/RULES.md — the blocking sentence

Old: "When readiness blocks, **ask only the readiness choice and stop**."

New: "When rules have gaps, **ask only the readiness question** (set up now / skip for this task); read-only work continues, writes wait for the answer."

## skills/resume-task/SKILL.md (later the `resume` skill) — step 1

Old: "Revalidate limited exceptions and changed inputs."

New: "Revalidate a recorded *Skip for this task* (its named gaps) and changed inputs; an unchanged skip is not asked again."

## skills/workflow/SPECIALISTS.md — worker handoff

Add to the handoff list: "the rules state and, after a skip, the named gaps it waives and the rules that still apply".

## Global blocks (skills/rule-maker/scripts/activate_rules.py; owner-only activation)

Old:
> Missing/insufficient rules: STOP and offer minimal setup,
> a specific one-task exception, read-only inspection or stop.

New:
> Missing/insufficient rules: name the gaps and ask "set up rules now" or
> "skip for this task"; read-only work continues, writes wait for the answer.

The installed global copies change only through `activate_rules.py --apply` / `global_policy.py --apply`, each with the owner's OK (T26 release handoff).

## skills/rule-maker/rules/READINESS.md — new projects

Old: "An empty new project needs an agreed minimal setup before scaffolding"

New: "An empty new project gets the same question: an approved minimal setup, or *Skip for this task* with its named gaps listed; either way the scaffolding itself still needs its own approval"

## skills/rule-maker/rules/READINESS.md — §6 acceptance sentence

Old: "All unclassified missing prerequisites block the affected action."

New: "A missing tool or check follows the workflow's named fallbacks; only the conditions in FALLBACKS.md "What may pause work" pause the dependent action."
