---
name: workflow-execute
description: "Implement approved tickets, verify and review them, then deliver with evidence. Use only after implementation approval."
---

# Workflow execute

Build the approved tickets until each is verified, then review the whole feature.

Read shared policies from sibling `../workflow/`, including its "Always" list. Stop if missing; never substitute another installed copy.

**Before you start**, check:

- rules cover the next ticket (`workflow/RULES.md`);
- the checkpoint `Approval` is approved, legacy or an explicit waiver covering these tickets. Agreement alone never allows code: go to `workflow-specify`;
- tickets have dependencies, acceptance, seams and scope (else `workflow-specify`);
- any optional specialist a ticket names (`workflow/SPECIALISTS.md`) is installed; a missing one blocks only that ticket;
- `git status` and diff are recorded (`workflow/TASK-FOLDER.md`);
- UI tickets have their `ui-design` authority recorded; otherwise they wait. Read `../ui-design/SKILL.md` step 4 before building one.

Reconfirm only missing authority, material changes or blockers.

## The loop

Repeat while a ticket is ready and the owner has not said stop, pause or cancel (then `workflow/TASK-FOLDER.md` "Stop, pause and cancel"). Use the approved worker/check budget; paid evaluations also follow VISUAL-REVIEW.md's explicit-budget rule. Parallel work needs independent tickets and separate files; say how many run. Do not fill unused slots.

1. **Pick.** A ticket is ready when its dependencies are verified with V-IDs on the current files. A blocked ticket blocks only its dependents.
2. **Checkpoint.** Save the ticket, its files and its check. Run the planned baseline checks before changing anything, or reuse a baseline whose inputs still match (TASK-FOLDER "Baseline before this change"). Record each failing test's name and first error line, not only counts.
3. **Pick the route.** Small route: one ticket, named files only, no interface, dependency, data or security change. Build it here and say so; without subagents, build every ticket here. Otherwise hand each ticket to a fresh worker briefed with the ticket, acceptance, seams, allowed files, rules, UI authority, output folder and starting `git status`; it returns evidence and you write the records. A ticket leaves the small route for reassessment on an unlisted file, a second caller, an interface or data change, an unrelated failure, or a hard finding or user decision. Collect `needs human` steps into one request.
4. **Build.** TDD tickets: read `../tdd/SKILL.md` before the first test and follow it at the agreed seam; it owns the red/green loop. Docs or config tickets: check the named contract; never report a red/green that didn't happen. Keep behavior at its owner, apply AUDIT.md's necessity check, update the named docs and delete what the ticket replaces.
5. **Verify.** Run the ticket's checks and record a V-ID: command, result, limits. UI tickets also run `ui-design` VERIFY.md; design acceptance stays separate. Save long output once, query it, and retain necessary failure evidence under ARTIFACTS.md; do not retain every retry indefinitely. Compare failures by name with `workflow/scripts/compare_failures.py` (one `id<TAB>first error line` per line): one is existing only when the same test fails the same way; name environment failures as such. Never weaken a test to pass.
6. **Review.** Review Standards and Spec separately with the reviewer `workflow/AUDIT.md` picks: `../code-review/SKILL.md` for code (never a host's same-named built-in); `../writing-for-agents/SKILL.md` plus the AUDIT categories for skills, instructions or docs. When the host has subagents, one fresh subagent reviews both axes, reading that file; a self-review only without subagents, labelled. Never review a diff again that has not changed since its last review.
7. **Repair.** Fix findings inside scope. A repair to code or tests goes back to the same reviewer as the repair diff only; a repair to records or wording you check and note. A finding the reviewer calls a user decision, or a fix that changes the approved approach or anything a user would notice, goes to the user before you ship it; other tickets continue. A finding that needs new authority, two repair rounds without progress, or a reviewer that fails twice marks the ticket blocked with the reason.
8. **Close.** Verify every current acceptance check after the last repair, including required device/human checks. Missing proof stays verification pending. Keep status concise and link evidence; removed work needs a decision, never a passed-test label.
9. **Integrate.** Run a verified ticket group's integration checks before its dependents start.

## Whole-feature review

When every ticket is verified or explicitly closed without a pass, review the whole change against the agreement with the same reviewer selection, plus AUDIT's checks for other callers, failure journeys, cleanup and records. Repair and recheck as in the loop. Ticket reviews don't replace this one; the last ticket's review, briefed with these checks, counts as both when no other ticket changed after its own review.

When nothing approved is runnable, deliver partial with blockers. Waiting is not verified; do not restart a review/repair loop.

## Changes found mid-way

A material change to behavior, scope, interface, dependency, risk or a protected area pauses only the affected tickets: behavior goes back to `workflow-clarify`, tickets to `workflow-specify`. Others continue. Missing infrastructure is a blocker; never install one yourself.

## Next

Then invoke `workflow-deliver` with the ticket list, V-IDs, reviews and blocked tickets. A stop, pause or cancel goes there too, labelled partial, and never comes back here unless the owner asks to continue. Execution is done only when deliver has run.

Adapts Implement Spec locally, not its invocation. No Git/tracker operations or specialist edits without separate authority.
