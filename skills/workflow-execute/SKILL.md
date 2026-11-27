---
name: workflow-execute
description: "Implement approved tickets, verify and review them, then deliver with evidence. Use only after implementation approval."
---

# Workflow execute

Build the approved tickets until each is verified, then review the whole feature. Write progress updates and ticket summaries for a person (`../workflow/WRITING.md`).

Read RULES.md, TASK-FOLDER.md, WRITING.md and AUDIT.md from sibling `../workflow/` before the first ticket; other files there only when a step names your case. Stop if missing; never substitute another installed copy.

**Before you start**, check:

- rules cover the next ticket (`workflow/RULES.md`);
- the checkpoint names `Offer: #<id>` covering these tickets, and approval is verified from evidence, as `resume` requires: the offer's presentation, the owner's decision and any later stop, withdrawal or narrowing. The `Offer:` line alone is not authority; on a host without hooks, check that evidence yourself. An `Approval` line counts only for a legacy task. Agreement alone never allows code: go to `workflow-specify`;
- tickets have dependencies, acceptance, seams and scope (else `workflow-specify`);
- a missing optional specialist a ticket names (`workflow/SPECIALISTS.md`) blocks only that ticket;
- `git status` and diff are recorded (`workflow/TASK-FOLDER.md`);
- the review baseline exists: before the first change, once per task, run `python -X utf8 -I ../workflow-deliver/scripts/completion_check.py baseline <project-root> <task-folder>` (it writes `completion.json`, which the review check needs; it is not the PLAN test baseline);
- UI tickets wait for their recorded `ui-design` authority; read `../ui-design/SKILL.md` step 4 before building one.

Reconfirm only missing authority, material changes or blockers.

**Todo list.** Copy the recipe's numbered steps (`workflow/flows/<recipe>.md`) and the approved tickets word for word into the host's todo list (TodoWrite or its equivalent); work from it and mark each item done as it finishes.

A lightweight edit runs one pass: build, its check, one review (step 6), then the short `workflow-deliver`.

**Briefs.** Every subagent brief starts with "The bar in this brief is the whole bar: add no check, gate or review round above it.", then gives what its step lists, pointing to files rather than copying them. A worker gets the ticket, acceptance, seams, allowed files, rules, FINDINGS documents, UI authority, output folder and starting `git status`. A builder quotes the runner's verbatim summary line for every test count (for unittest, `Ran N tests … OK`) and gives a file:line for every claim about existing behaviour. Subagents return evidence; you write the records.

## The loop

Repeat while a ticket is ready and the owner has not said stop, pause or cancel (then `workflow/TASK-FOLDER.md` "Stop, pause and cancel"). Use the approved worker/check budget; a paid evaluation needs `workflow/PAID-EVALUATION.md`. Parallel work needs independent tickets and separate files; say how many run.

1. **Pick** a ticket whose dependencies are verified with V-IDs on the current files. A blocked ticket blocks only its dependents.
2. **Checkpoint.** Save the ticket, its files and its check. Run the planned baseline checks first, or reuse a baseline whose inputs still match (TASK-FOLDER "Baseline before this change"); record each failing test's name and first error line.
3. **Pick the route.** Small route: one ticket, named files only, no interface, dependency, data or security change; build it here and say so. A ticket leaves the small route on an unlisted file, a second caller, an interface or data change, an unrelated failure, or a finding or user decision; then a fresh worker builds it (without subagents, you, saying so). With several tickets, each runs in a fresh worker, or after /clear from the task records when the host has no subagents; you keep the records and reviews. Collect `needs human` steps into one request.
4. **Build.** TDD tickets: read `../tdd/SKILL.md` before the first test and follow it at the agreed seam. Docs or config tickets: check the named contract; never report a red/green that didn't happen. Apply AUDIT.md's necessity check; delete what the change replaces. When the ticket's Documents line names a document, update it as `../rule-maker/DOCS.md` says.
5. **Verify.** Run the ticket's checks; record a V-ID: command, result, limits. UI tickets also run `../ui-design/VERIFY.md` under `../rule-maker/rules/DESIGN.md`; design acceptance stays separate. Compare failures by name with `workflow/scripts/compare_failures.py` (`id<TAB>first error line` per line): existing only when the same test fails the same way. Never weaken a test to pass.
6. **Review.** Snapshot the handed-over files with the same script (`snapshot <project-root> <task-folder> <files>`), give the reviewer its `S<n>` and record the FINDINGS line it prints. `workflow/AUDIT.md` picks the reviewer: `../code-review/SKILL.md` for code, `../writing-for-agents/SKILL.md` plus AUDIT's categories for skills, instructions or docs. Code-review step 4 sets the count: for a small diff one fresh subagent reviews both axes, reading that file. Self-review only without subagents, labeled. Code-review's step 4b runs when its trigger fires. Never review a diff again that has not changed since its last review.
7. **Repair.** Only a finding as code-review "What counts as a finding" defines it starts a repair; record notes. A code or test repair gets a new snapshot and goes to the same reviewer as the repair diff only; check and note a records or wording repair. A finding the reviewer calls a user decision, or a fix that changes the approved approach or anything a user would notice, goes to the user before you ship it. New authority needed, two rounds without progress, or a reviewer failing twice blocks the ticket, with the reason.
8. **Close.** Verify every current acceptance check after the last repair, required device/human checks included. Missing proof stays verification pending; removed work needs a decision, never a passed-test label.
9. **Integrate.** Run a verified ticket group's integration checks before its dependents start.

## Whole-feature review

When every ticket is verified or explicitly closed without a pass, review the whole change against the agreement with the same reviewer selection, plus AUDIT's checks for other callers, failure journeys, cleanup and records. If the trigger fired for any ticket, code-review's step 4b runs again on the whole diff: tickets can combine into a break none shows alone. A one-ticket task's ticket review, briefed with these checks, is its whole-feature review; so is the last ticket's review when so briefed and no other ticket changed after its own review. Never review the same diff twice. When nothing approved is runnable, deliver partial with blockers.

## Changes found mid-way

A material change to behavior, scope, interface, dependency, risk or a protected area pauses only the affected tickets: behavior goes back to `workflow-clarify`, tickets to `workflow-specify`. Missing infrastructure follows `workflow/FALLBACKS.md`; only what it lists may pause work. Never install one yourself.

## Next

Invoke `workflow-deliver` with the ticket list, V-IDs, reviews and blocked tickets. A stop, pause or cancel goes there too, labeled partial, and never comes back here unless the owner asks to continue. Execution is done only when deliver has run. No Git/tracker operations or specialist edits without separate authority.
