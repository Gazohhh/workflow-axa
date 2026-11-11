---
name: workflow-specify
description: "Turn agreed behavior into scoped tickets, dependencies, checks and the plan report for implementation approval. Use after agreement or for a scoped revision."
---

# Workflow specify

Turn the agreement into tickets another agent could build, and get the plan approved. No application code or tests.

Read shared policies from sibling `../workflow/`, including its "Always" list. Stop if missing; never substitute another installed copy.

**Before you start**, check: rules cover this scope (`workflow/RULES.md`); the checkpoint `Agreement` is agreed, legacy or waived for this revision, or clarify sent a small settled change here to ask both gates at once (`workflow/VISUAL-REVIEW.md`); otherwise go to `workflow-clarify`; no open choice blocks the plan; application UI has its `ui-design` mode and sources recorded (an unrecorded mode blocks only UI tickets); read `../ui-design/SKILL.md` if this session has not. When existing styles cannot produce the agreed layout, ask DESIGN.md rule 4's question; never offer new CSS. Refresh evidence for files changed since the agreement.

## 1. Place the behavior

Put each behavior in the code that already owns it. Read `../codebase-design/SKILL.md` when an interface or seam is in question, `../domain-modeling/SKILL.md` when a term or owner is unclear. Every new helper, wrapper, fallback or setting must pass the necessity check in `workflow/AUDIT.md`. Pick risk guidance from rule-maker's ENGINEERING.md.

## 2. Cut vertical tickets

A **ticket** delivers one visible slice of a journey through every layer it needs, so it can be tested and reviewed alone. A ticket with no behavior of its own is a labeled prerequisite that names what it enables.

Write TODO in the `workflow/TASK-FOLDER.md` format via `record.py`. Supports, Depends on and Rules go under References, Documents on its own line, the rest under Technical details:

- **Supports**: R-IDs and A-IDs.
- **Scope**: files or areas it may change, and those it must not.
- **Depends on**: tickets that must be verified first.
- **What should work**: what someone can observe, failures included.
- **Test seam**: the public interface the test uses, what it catches, what it misses and how that gap is covered.
- **TDD**: yes, or no with the reason (docs, configuration, no testable seam).
- **How to verify**: the exact check and its output folder (`workflow/ARTIFACTS.md`); steps only a person can do (device, account, visual sign-off) marked `Human check: what, when` (or `needs human`), asked for together.
- **Documents**: related documents it changes, or none (`../rule-maker/DOCS.md`).
- **Cleanup**: code it replaces and removes.
- **Rules**: the project rules (each AGENTS.md or CLAUDE.md on the ticket's path) the change must follow. A neighbor's pattern a rule forbids is no precedent: ask in step 5.

Done when the graph has no cycles, every requirement and acceptance item has a ticket and each ticket traces back to one, and parallel tickets share no file.

## 3. Name the bigger checks

List checks for each group of dependent tickets and whole-feature checks against the agreement: other callers, compatibility, failure journeys. Say what can't be checked and why. Without a test runner, a headless Edge or Chrome probe page can click (`--dump-dom`). Name what each check needs (server, port, device, account) and ask for it in step 5, so a needed check is never dropped silently at delivery.

## 4. Challenge it (when large or risky)

Run `plan-review` in a fresh context and resolve its findings. A behavior question goes back to `workflow-clarify`. Any answer that changes what users see or an agreed requirement (placement, wording, which rows) changes the agreement: write a new agreement revision for those items and ask for it in step 5's message; never record it only as a decision.

## 5. Implementation approval

First compare every ticket with the agreement line by line (behavior, timing, data, failures, assumptions); any difference is an agreement change (step 4). Build the plan report as `workflow/VISUAL-REVIEW.md` "Prepare the report" says and ask for implementation approval; say "implements the behavior we agreed" only when that comparison found no difference. **STOP** (VISUAL-REVIEW "Prepare the report" step 4).

Done when the report exists for this revision and its path is in your approval question (one-line changes included), or the user's explicit "no report" is recorded, or the task is on the small change route (valid `Small change:` line, no switch to the full route; `workflow/VISUAL-REVIEW.md`). Set `task_report.screen_change`; a change a user can see on screen (`visible`) also needs the report's screen diagram (`ui-design` step 3): kit screens with a design kit (`../codebase-map/UI-FLOW.md`), else capture and sketch; then preview is `not-needed`.

Record the answer in the checkpoint `Approval` line and DECISIONS: approved (revision, report, tickets, exclusions), a correction (behavior or scope → `workflow-clarify`; tickets, seams, presentation → here), or a scoped waiver.

## Revisions

For a later change, rewrite only affected tickets and checks and show the difference from the last approved revision. Other approved tickets keep running. Fixing a path or order inside an approved ticket needs no revision.

## Next

- Approved or waived, with implementation requested: `workflow-execute`.
- Plan-only request: stop with the plan, approved or not.
- Blocked: record what blocks which tickets and what can still be approved.

Never open tracker issues.
