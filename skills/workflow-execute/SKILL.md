---
name: workflow-execute
description: "Implement approved tickets, verify and review them, then deliver with evidence. Use only after implementation approval."
---

# Workflow execute

Write progress updates and ticket summaries for a person, as `../workflow/WRITING.md` says.

Build the approved tickets until each is verified, then review the whole feature.

Read shared policies from sibling `../workflow/`, including its "Always" list. Stop if missing; never substitute another installed copy.

**Before you start**, check:

- rules cover the next ticket (`workflow/RULES.md`);
- the checkpoint names `Offer: #<id>` covering these tickets, and approval is verified from evidence, as `resume` requires: the offer's presentation, the owner's decision and any later stop, withdrawal or narrowing. The `Offer:` line alone is not authority; on a host without hooks, check that evidence yourself. An `Approval` line counts only for a legacy task. Agreement alone never allows code: go to `workflow-specify`;
- tickets have dependencies, acceptance, seams and scope (else `workflow-specify`);
- any optional specialist a ticket names (`workflow/SPECIALISTS.md`) is installed; a missing one blocks only that ticket;
- `git status` and diff are recorded (`workflow/TASK-FOLDER.md`);
- UI tickets have their `ui-design` authority recorded; otherwise they wait. Read `../ui-design/SKILL.md` step 4 before building one.

Reconfirm only missing authority, material changes or blockers.

The chosen recipe in `workflow/flows/` may add steps to this loop; follow them where it says.

A lightweight edit runs one pass: build, its check, one review (step 6), then the short `workflow-deliver`. No ticket loop or whole-feature review.

Before the first change, record the baseline once: `python -X utf8 -I ../workflow-deliver/scripts/completion_check.py baseline <project-root> <task-folder>`. It leaves out the edits that were already there.

## The loop

Repeat while a ticket is ready and the owner has not said stop, pause or cancel (then `workflow/TASK-FOLDER.md` "Stop, pause and cancel"). Use the approved worker/check budget; paid evaluations also follow VISUAL-REVIEW.md's explicit-budget rule. Parallel work needs independent tickets and separate files; say how many run. Do not fill unused slots.

1. **Pick.** A ticket is ready when its dependencies are verified with V-IDs on the current files. A blocked ticket blocks only its dependents.
2. **Checkpoint.** Save the ticket, its files and its check. Run the planned baseline checks before changing anything, or reuse a baseline whose inputs still match (TASK-FOLDER "Baseline before this change"). Record each failing test's name and first error line, not only counts.
3. **Pick the route.** Small route: one ticket, named files only, no interface, dependency, data or security change. Build it here and say so; without subagents, build every ticket here. Otherwise hand each ticket to a fresh worker briefed with the ticket, acceptance, seams, allowed files, rules, related documents from FINDINGS, UI authority and purpose statement, output folder and starting `git status`; it returns evidence and you write the records. A ticket leaves the small route for reassessment on an unlisted file, a second caller, an interface or data change, an unrelated failure, or a hard finding or user decision. Collect `needs human` steps into one request.
4. **Build.** TDD tickets: read `../tdd/SKILL.md` before the first test and follow it at the agreed seam; it owns the red/green loop. Docs or config tickets: check the named contract; never report a red/green that didn't happen. Keep behavior at its owner, apply AUDIT.md's necessity check, update the ticket's Documents with its code (`../rule-maker/DOCS.md`) and delete what the ticket replaces.
5. **Verify.** Run the ticket's checks and record a V-ID: command, result, limits. UI tickets also run `ui-design` VERIFY.md (`../ui-design/VERIFY.md`) under `../rule-maker/rules/DESIGN.md`; design acceptance stays separate. Save long output once, query it, and retain necessary failure evidence under ARTIFACTS.md, not every retry. Compare failures by name with `workflow/scripts/compare_failures.py` (one `id<TAB>first error line` per line): one is existing only when the same test fails the same way; name environment failures as such. Never weaken a test to pass.
6. **Review.** First snapshot the files you hand over: `python -X utf8 -I ../workflow-deliver/scripts/completion_check.py snapshot <project-root> <task-folder> <files>` prints `S<n>`; give the reviewer that id. Record the result as one FINDINGS line: `- Review S<n>: <reviewer> (independent|self) <passed|failed|pending>: <scope>`. Review Standards and Spec separately with the reviewer `workflow/AUDIT.md` picks: `../code-review/SKILL.md` for code (never a host's same-named built-in); `../writing-for-agents/SKILL.md` plus the AUDIT categories for skills, instructions or docs. When the host has subagents, one fresh subagent reviews both axes, reading that file; a self-review only without subagents, labeled. Code-review's step 4b runs when its trigger fires. Never review a diff again that has not changed since its last review.
7. **Repair.** Fix findings inside scope. A repair to code or tests gets a new snapshot and goes back to the same reviewer as the repair diff only; a repair to records or wording you check and note. A finding the reviewer calls a user decision, or a fix that changes the approved approach or anything a user would notice, goes to the user before you ship it; other tickets continue. A finding that needs new authority, two repair rounds without progress, or a reviewer that fails twice marks the ticket blocked with the reason.
8. **Close.** Verify every current acceptance check after the last repair, including required device/human checks. Missing proof stays verification pending. Keep status concise and link evidence; removed work needs a decision, never a passed-test label.
9. **Integrate.** Run a verified ticket group's integration checks before its dependents start.

## Whole-feature review

When every ticket is verified or explicitly closed without a pass, review the whole change against the agreement with the same reviewer selection, plus AUDIT's checks for other callers, failure journeys, cleanup and records. When the trigger fired for any ticket, code-review's step 4b runs again on the whole diff: tickets can combine into a break that none shows alone. Repair and recheck as in the loop. Ticket reviews don't replace this one; the last ticket's review, briefed with these checks, counts as both when no other ticket changed after its own review.

When nothing approved is runnable, deliver partial with blockers. Waiting is not verified; do not restart a review/repair loop.

## Changes found mid-way

A material change to behavior, scope, interface, dependency, risk or a protected area pauses only the affected tickets: behavior goes back to `workflow-clarify`, tickets to `workflow-specify`. Others continue. Missing infrastructure follows `workflow/FALLBACKS.md`: use its named fallback and record it. It is not a blanket blocker; only what that file lists may pause work, and a missing check usually blocks only the "done" claim. Never install one yourself.

## Next

Invoke `workflow-deliver` with the ticket list, V-IDs, reviews and blocked tickets. A stop, pause or cancel goes there too, labeled partial, and never comes back here unless the owner asks to continue. Execution is done only when deliver has run.

No Git/tracker operations or specialist edits without separate authority.
