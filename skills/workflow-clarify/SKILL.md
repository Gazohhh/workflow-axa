---
name: workflow-clarify
description: "Agree a task's behavior before planning: trace journeys, callers and failure paths, and grill only for open user decisions. Use for a new goal, a scope change or a contradictory answer."
---

# Workflow clarify

Turn a request into a behavior agreement the user confirms. No tickets, offers or code.

Read shared policies from sibling `../workflow/`, including its "Always" list. Stop if missing; never use another skills root's copy.

**Before you start**, check: rules are READY, or a recorded LIMITED_EXCEPTION covers this phase within its limits (`workflow/RULES.md`); the task is found and checkpointed (`workflow/TASK-FOLDER.md`), or the router left only its identity open: then ask "separate task or revision?" as Q1 of your first round, saying a separate task is best in a fresh chat; word the other questions so they hold for either answer, save the round as TASK-FOLDER.md's "identity pending" row says, and never ask it alongside approvals; explain-only and lightweight edits are not clarify work (`workflow/SKILL.md` §2–3). If an agreement covers this revision, go to `workflow-specify`; an approved offer follows Next. Application UI, meaning anything a user sees on screen (order, text, which rows or items show, layout or styling): first read `../ui-design/SKILL.md` and `../rule-maker/rules/DESIGN.md`, then trace. Options you offer include new CSS only when the machine CSS switch is on (`rule-maker/rules/DESIGN.md` rule 1).

## 1. Trace the journeys

For a new task or a new request on existing work, apply `../workflow/SKILL.md` §3 before tracing: pick the recipe and show its `Recipe:` line, then record it in the checkpoint (while identity is pending, with that round); reuse a pick already shown for this same request.

A **journey** is one actor getting one outcome: trigger → steps → what they see. For each actor the request touches, trace in code and record in FINDINGS (J-IDs, E-IDs):

1. **Owner and callers**: the code that owns the behavior, every other caller or entry point that reaches it, and the data and settings it reads. A caller no journey explains is a question.
2. **Failures**: what the actor sees on bad input, missing permission, offline or failed dependency, timeout, cancel, retry.
3. **Compatibility**: saved data, old callers, public interfaces, versions; whether the change extends or replaces what exists.
4. **State and timing**: remembered after closing or across devices; applies now or on the next action.
5. **Limits**: allowed dependencies or cost, target environments, privacy, stated exclusions.
6. **Purpose and screen** (UI only): the **purpose statement** (`workflow/TASK-FOLDER.md` Agreement). A missing part that would change the result becomes a step 2 question; never invent product intent. Then each new element, the existing one doing that job for that user (`file:line`, tag, classes, why) and what `python -X utf8 -I ../ui-design/scripts/class_rules.py <project-root> <classes>` prints. A `[needs context]` rule, or a layout difference shown by `--compare <from-parent> <into-parent>`, means no match: ask DESIGN.md rule 4's question.

Find related documents through the AGENTS.md index and `python -X utf8 -I ../rule-maker/scripts/docs_check.py <project-root> --changed <named or traced files>` (`../rule-maker/DOCS.md`). Read those first; record them and suspected contradictions in FINDINGS (E-IDs).

Done when every journey's owner and callers are traced and related documents found, or the missing access is recorded. Ask direction or access blockers once their dependencies are traced, and keep tracing the rest.

## 2. Grill

Read `../grilling/SKILL.md` now, before writing any question, and run it on what step 1 found.

Done when its stop rules hold ("Break it before stopping").

## 3. Write the agreement

Write `## Agreement` in PLAN with `workflow/scripts/record.py replace-section` (`workflow/WRITING.md` rules):

- requirements (R-IDs), each with where it came from;
- what happens for each actor, including failures, and step 1's purpose statement;
- what stays the same, and what is not included;
- acceptance (A-IDs) as things someone can observe;
- assumptions the user can reject, and choices deferred and by whom.

File lists and test commands wait for `workflow-specify`.

## 4. Agreement

Summarize every part of the agreement in plain words, with the PLAN path. Then ask:

> "Does this describe what should be built? Agree to it, or tell me what to change. Agreeing lets me write the detailed plan; no code changes until you approve that plan."

**STOP.** Answering grilling, silence or a generic "go" is not agreement. Never invite approval of a plan the user hasn't seen, and never borrow shortcuts from other tasks or earlier revisions.

When nothing is open and the work is one ticket (`workflow/VISUAL-REVIEW.md` "No separate agreement"): record Agreement `not required — one-ticket offer` and invoke `workflow-specify` without the question above. Clarify never asks for plan approval itself and never makes an offer.

Record the answer in the checkpoint `Agreement` line and DECISIONS: agreed (agreement N, date), partially agreed (reopened items go back to step 2), rejected, or an explicit waiver with its scope.

## Next

- Agreed, waived or not required: `workflow-specify`.
- Approved offer, even later: `workflow-execute`.
- Research: stop with findings and open choices recorded. Plan-only: continue through `workflow-specify`, then stop; code needs an implementation request too.
- Blocked: record the blocking question or missing access, and what can still proceed.