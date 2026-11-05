---
name: workflow-clarify
description: "Clarify a workflow task's intended behavior before any specification: trace real journeys, callers, failure and compatibility paths in current code, grill only for open user decisions, and record the gate-one behavior agreement. Use for a new substantive goal, a material scope change, or a contradictory or partial answer."
---

# Workflow clarify

Turn a request into a behavior agreement the user confirms. Read the code first, then ask only what the code can't answer. No tickets, no code.

Read shared policies from `../workflow/` from this SKILL.md; if it's missing, stop and say so. Never use a `workflow` copy from another skills root. Its SKILL.md "Always" list applies here too (end every turn with the state line).

**Before you start**, check: rules are READY, or a recorded LIMITED_EXCEPTION covers this phase within its limits (`workflow/RULES.md`); the task is found and checkpointed (`workflow/TASK-FOLDER.md`), or the router left only its identity open: then ask "separate task or revision?" as Q1 of your first round, saying a separate task is best in a fresh chat; word the other questions so they hold for either answer, save the round as TASK-FOLDER.md's "identity pending" row says, and never ask it alongside approvals; the request is real work, not explain-only or a lightweight edit. If an agreement already covers this revision, go to `workflow-specify`. Application UI, meaning anything a user sees on screen (order, text, which rows or items show, layout, not only styling): first read `../ui-design/SKILL.md` and `../rule-maker/rules/design.md`, then trace. Options you offer never include new CSS, not even as a one-off exception.

## 1. Trace the journeys

A **journey** is one actor getting one outcome: trigger → steps → what they see. For each actor the request touches, trace in the code and record in FINDINGS (J-IDs, E-IDs):

1. **Owner and callers**: the code that owns the behavior, every other caller or entry point that reaches it, and the data and settings it reads. A caller no journey explains is a question.
2. **Failures**: what the actor sees on bad input, missing permission, offline or failed dependency, timeout, cancel, retry.
3. **Compatibility**: saved data, old callers, public interfaces, versions; whether the change extends or replaces what exists.
4. **State and timing**: remembered after closing or across devices; applies now or on the next action.
5. **Limits**: allowed dependencies or cost, target environments, privacy, stated exclusions.
6. **Screen** (UI only): each new element, the existing one it mirrors (`file:line`, tag, classes) and what `python -X utf8 -I ../ui-design/scripts/class_rules.py <project-root> <classes>` prints. A `[needs context]` rule, or a layout difference shown by `--compare <from-parent> <into-parent>`, means no match: ask design.md rule 4's question.

How to read code and record evidence: `workflow/GROUNDING.md`.

Done when every journey's owner and callers are traced, or the missing access is recorded. Trace what a question depends on before asking it. Ask direction or access blockers at once and keep tracing the rest.

## 2. Grill

Read `../grilling/SKILL.md` now, before writing any question, and run it on what step 1 found; asking without it skips the decision check.

Done when its stop rules hold ("Break it before stopping").

## 3. Write the agreement

Write `## Agreement` in PLAN with `workflow/scripts/record.py replace-section` (`workflow/WRITING.md` rules):

- requirements (R-IDs), each with where it came from;
- what happens for each actor, including failures;
- what stays the same, and what is not included;
- acceptance (A-IDs) as things someone can observe;
- assumptions the user can reject, and choices deferred and by whom.

Describe behavior and acceptance; tickets, implementation file lists and test commands wait for `workflow-specify`.

## 4. Gate one

Summarize the agreement in chat in plain words: what happens for each actor, what stays the same, what is excluded, which assumptions they can reject, and the PLAN path. Then ask:

> "Does this describe what should be built? Agree to it, or tell me what to change. Agreeing lets me write the detailed plan; no code changes until you approve that plan."

**STOP.** Answering grilling, silence or a generic "go" is not agreement. Never invite approval of a plan the user hasn't seen, and never borrow shortcuts from other tasks or earlier revisions.

When nothing is open and the change is small (`workflow/VISUAL-REVIEW.md` "Both gates in one message"), don't ask anything yet: invoke `workflow-specify` now. It writes the tickets and the HTML report and asks for both gates in one message. Clarify never asks for plan approval itself. An explicit yes to both, even in a later session, records both lines; continue with `workflow-execute`.

Record the answer in the checkpoint `Agreement` line (refreshing its next action) and DECISIONS: agreed (revision, date), partially agreed (reopened items go back to step 2), rejected, or an explicit waiver with its scope. Gate rules: `workflow/VISUAL-REVIEW.md`.

## Next

- Agreed or waived: `workflow-specify`.
- Research: stop with findings and open choices written down. Plan-only: continue through `workflow-specify`, then stop; code needs an implementation request too.
- Blocked: record the blocking question or missing access, and what can still proceed.

A later change comes back here for the affected items only; the rest keeps its agreement.
