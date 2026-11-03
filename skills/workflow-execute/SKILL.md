---
name: workflow-execute
description: "Implement an approved workflow plan ticket by ticket: pick ready tickets whose dependencies are verified, build each in a recoverable checkpointed unit with agreed test-first slices, review it on Standards and Spec, repair, run integration checks, then review the whole feature. Use only after gate-two implementation approval."
---

# Workflow execute

Build the approved tickets, in parallel when their files don't overlap, until each is verified, then review the whole feature. This adapts Implement Spec's ticket graph (see Next); it is not an `implement-spec` invocation.

Read shared policies from `../workflow/` from this SKILL.md (missing: stop and say so; never another skills root's copy). Its "Always" list applies here too.

**Before you start**, check:

- rules cover the next ticket (`workflow/RULES.md`);
- the checkpoint `Approval` is approved, legacy or an explicit waiver covering these tickets. Agreement alone never allows code: go to `workflow-specify`;
- tickets have dependencies, acceptance, seams and scope (else `workflow-specify`);
- any optional specialist a ticket names (`workflow/SPECIALISTS.md`) is installed; a missing one blocks only that ticket;
- `git status` and diff are recorded so your changes can be told apart (`workflow/TASK-FOLDER.md`);
- UI tickets have their `ui-design` authority recorded; otherwise they wait. Read `../ui-design/SKILL.md` step 4 before building one.

Approved tickets need no further confirmation; ask only for missing authority, material changes or real blockers.

## The loop

Repeat while a ticket is ready. Run every ready ticket whose files overlap nothing running, up to the host's limit, and say how many run; one at a time only without subagents or with overlapping files.

1. **Pick.** A ticket is ready when every ticket it depends on is verified with a V-ID on the current files. A checked box without a V-ID isn't verified. A blocked ticket blocks only its dependents.
2. **Checkpoint.** Save the ticket, its files and its check. Run every check the ticket names (full suites included) once before changing anything and record the counts as the baseline, so later failures can be attributed by number, not guessed by type.
3. **Hand off or build here.** With subagents, hand every ticket, even a single one, to a fresh worker briefed with the ticket, acceptance, seams, allowed files, rules, UI authority, output folder and starting `git status`; it returns evidence and you write the records. Otherwise build it here and say so. Collect the ticket's `needs human` steps into one request instead of asking one at a time.
4. **Build.** TDD tickets: read `../tdd/SKILL.md` before the first test (once per session) and follow it. Run it at the agreed seam; it owns the red/green loop. Docs or config tickets: check the named contract; never report a red/green that didn't happen. Keep behavior at its owner, apply AUDIT.md's necessity check, update the named docs and delete what the ticket replaces.
5. **Verify.** Run the ticket's checks and record a V-ID: command, result, limits. UI tickets also run `ui-design` VERIFY.md; design acceptance stays separate. Save long output once and query that file; never rerun a check just to filter it. Tell your failures from existing and environment failures. Never weaken a test to pass.
6. **Review.** Review the ticket's changes on Standards and Spec separately, with the reviewer `workflow/AUDIT.md` picks for what changed: `../code-review/SKILL.md` for code (never a host's same-named built-in); `../writing-for-agents/SKILL.md` plus the AUDIT categories for skills, instructions or docs. When the host has subagents, the reviewer must be a fresh subagent that reads that file; a self-review is allowed only without subagents, and is labelled.
7. **Repair.** Fix findings inside scope and re-review promptly with the same reviewer. A finding the reviewer calls a user decision, or a fix that changes the approved approach or anything a user would notice (a new side effect, different wording, a different endpoint with other behavior) goes to the user before you ship it; continue other tickets meanwhile. A finding that needs new authority, or repairs that stop making progress, mark the ticket blocked with the reason.
8. **Close.** Verified only with passing evidence and every finding closed or limited. Save the result and the next ready ticket.
9. **Integrate.** When a group of dependent tickets is verified, run its integration checks before anything depending on it starts.

## Whole-feature review

When every ticket is in a terminal state (`workflow/TASK-FOLDER.md`), review the whole change against the whole agreement with the same reviewer selection, plus AUDIT's checks for other callers, failure journeys, cleanup and records. Repair, rerun and re-review as in the loop. Ticket reviews don't replace this one; for a single ticket, one review briefed with these checks counts as both.

## Changes found mid-way

A material change to behavior, scope, interface, dependency, risk or a protected area pauses only the affected tickets: behavior goes back to `workflow-clarify`, tickets to `workflow-specify`. Others continue. Missing infrastructure is a blocker; never install a runner or provider yourself.

## Next

Then invoke `workflow-deliver` (it runs its reconciliation in a fresh subagent) with the ticket list, V-IDs, reviews and blocked tickets; a partial stop goes there too, labelled partial. Execution is done only when deliver has run: never end with a summary of your own instead.

Adapting Implement Spec: PLAN/TODO replace the tracker and the current worktree replaces integration branches; no branch, worktree, reset, stash, stage, commit, merge, push, PR or tracker action on your own; sequential execution is labelled as such. Don't edit installed specialist files.
