---
name: workflow-specify
description: "Turn agreed behavior into scoped tickets, dependencies, checks and the offer for implementation approval; the plan report only when asked. Use after agreement or for a scoped revision."
---

# Workflow specify

Turn the agreement into tickets another agent could build, and get the offer approved. The plan report is built only on *Show review.html first* or when the owner asks. No application code or tests.

Read shared policies from sibling `../workflow/`, including its "Always" list. Stop if missing; never substitute another installed copy.

**Before you start**, check: rules cover this scope (`workflow/RULES.md`); the checkpoint `Agreement` is agreed, legacy or waived for this revision, or `not required` for a lightweight edit or settled one-ticket work, which gets the one-ticket offer (`workflow/VISUAL-REVIEW.md` "No separate agreement"); otherwise go to `workflow-clarify`; no open choice blocks the plan; application UI has its `ui-design` mode and sources recorded (an unrecorded mode blocks only UI tickets); read `../ui-design/SKILL.md` if this session has not. When existing styles cannot produce the agreed layout, ask DESIGN.md rule 4's question; include new CSS only when the machine CSS switch is on (`rule-maker/rules/DESIGN.md` rule 1). Refresh evidence for files changed since the agreement.

## 1. Place the behavior

Put each behavior in the code that already owns it. Read `../codebase-design/SKILL.md` when an interface or seam is in question, `../domain-modeling/SKILL.md` when a term or owner is unclear. Every new helper, wrapper, fallback or setting must pass the necessity check in `workflow/AUDIT.md`. Pick risk guidance from rule-maker's ENGINEERING.md.

## 2. Cut vertical tickets

A **ticket** delivers one visible slice of a journey through every layer it needs, so it can be tested and reviewed alone. A ticket with no behavior of its own is a labeled prerequisite that names what it enables.

Cut to the work's size. A lightweight edit gets no ticket: step 5's **minimal offer** names its files, its check and a one-line why. One-ticket work, a small visible change included, gets one ticket and the **one-ticket offer**. A ticket list is for multi-ticket work only.

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

List checks for each group of dependent tickets and whole-feature checks against the agreement: other callers, compatibility, failure journeys, and each safety assumption from clarify as the check that could falsify it. Say what can't be checked and why. Without a test runner, a headless Edge or Chrome probe page can click (`--dump-dom`). Name what each check needs (server, port, device, account) and ask for it in step 5, so a needed check is never dropped silently at delivery.

## 4. Challenge it (when large or risky)

Run `plan-review` in a fresh context and resolve its findings. A behavior question goes back to `workflow-clarify`. Any answer that changes what users see or an agreed requirement (placement, wording, which rows) changes the agreement: write a new agreement revision for those items and ask for it in step 5's message; never record it only as a decision.

## 5. Implementation approval

First compare every ticket with the agreement line by line (behavior, timing, data, failures, assumptions); any difference is an agreement change (step 4). Then write the **offer** (the minimal offer for a lightweight edit, one ticket's paths for one-ticket work): a JSON file with the behaviour summary, the paths the tickets may change, the operations (only protected actions, each by its exact name: `git commit` when asked, `git push`, an MCP tool's name; never a check), exclusions, conditions and required checks. Run the Unslop check of `../workflow/WRITING.md` on its prose, then create it with `python -X utf8 -I <workflow>/scripts/record.py offer create <task-folder> <file.json>`. The owner doesn't see tool output: only the offer as `record.py offer present` prints it, in your reply or as a question's own text, counts as presented. Copy that output unchanged; never rewrite, shorten, translate or escape it.

Present it with **the one question**, which has three answers: *Show review.html first*, *Approve from this summary*, *Change something*. When the change touches saved data, auth, a public interface, a migration, deletion, money, more than one owner or visible UI, recommend the report and say why in plain words. Present it one way:

- **With the question tool** whenever the host offers one (Claude Code and T3 Code do): the question's text is the output of `record.py offer present <task-folder> <id> --question`, unchanged (the CSS line first, as printed). Give exactly those three answers. A recommended answer comes first, ends in "(Recommended)" and carries the reason as its description; you may also put "**I recommend the report first**, because [reason]." and a blank line before the CSS line.
- **Only without a question tool**, as text: the output of `record.py offer present <task-folder> <id>` is **the end of your reply**, as ordinary text: no code block or quote around it, nothing after it. Text before it, the recommendation sentence included, ends with a blank line and has no `<`, no `$$` and no fenced block; put examples or HTML in an earlier message.

**STOP.** Say "implements the behavior we agreed" only when the comparison found no difference.

Done when the offer was presented and the one question asked (one-line changes included). Record the owner's choice with `record.py offer presentation <task-folder> <id> html-first|chat`. The report is built only on *Show review.html first* or when the owner asks: build it as `workflow/VISUAL-REVIEW.md` "Prepare the report" says (read `../codebase-map/TASK-REPORT.md`, `../codebase-map/FLOWCHART-DESIGN.md` and `../workflow/SIMPLE-ENGLISH.md` whole first), name its `docs/plans/<task>/reviews/<file>.html` path, and ask again with *Approve from this summary* and *Change something*. Set `task_report.screen_change`; a change a user can see on screen (`visible`) also needs the report's screen diagram, kit screens with a design kit: VISUAL-REVIEW.md "UI work" owns its rules (read `../codebase-map/UI-FLOW.md` whole first); then preview is `not-needed`.

The hook reads the answer from the conversation; never write an approval yourself. Record `- Offer: #<id>` in the checkpoint and the answer in DECISIONS. This step owns qualified answers and corrections. A qualified answer ("yes, but not the database") approves nothing: write the narrowed offer with `record.py offer revise`, present it, and ask once more. A correction of behavior or scope goes to `workflow-clarify` for those items; tickets, seams or presentation stay here. `offer revise` marks the old offer superseded; present the new one. `/wait-what` is no answer: explain, then present the unchanged offer and the same question again.

## Revisions

For a later change, rewrite only affected tickets and checks and show the difference from the last approved revision. Other approved tickets keep running. Reordering tickets inside an approved offer needs no revision. Any change to the offer's allowed paths, operations or checks needs a revised offer (`record.py offer revise`) and a new answer.

## Next

- Offer approved, or for a legacy task its recorded approval, with implementation requested: `workflow-execute`.
- Plan-only request: stop with the plan, approved or not.
- Blocked: record what blocks which tickets and what can still be approved.

Never open tracker issues.
