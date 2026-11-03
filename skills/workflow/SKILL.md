---
name: workflow
description: "Use for new or existing repository features, fixes, refactors, research, plans, audits and task resumption, including ordinary prompts. Find the right task, check rules, then route to the phase skill its records require: clarify and agree behavior, specify and approve the plan, execute tickets, deliver evidence. Explain-only requests remain read-only."
---

# Workflow

Route one task to its next phase. **Once the task is found, your next action is invoking the phase skill §3 picks; never ask the user questions or approvals from this file.** Write for someone new to the project ([WRITING.md](WRITING.md)).

## 1. Check rules readiness

Read [RULES.md](RULES.md) before planning or writing, even if rule-maker never ran. Missing coverage: STOP and offer setup, a bounded exception, read-only inspection or stop. Application UI: read `../ui-design/SKILL.md` before planning. Never write or offer new CSS, even as an exception; record mode, mirrored elements, preview/release limits.

## 2. Find the task

1. State the repository, branch and local changes; never touch the user's edits.
2. Pick the mode. **Explain** is read-only; a later "fix it" or "push when done" makes it Implement: invoke `workflow-clarify`. **Research, plan or audit** never authorizes code. **Implement** passes the gates below.
3. Before creating any task folder, follow [TASK-FOLDER.md](TASK-FOLDER.md) to find and reuse the task. A new chat is not a new task. When a related task might match, create nothing: invoke `workflow-clarify`, which asks "separate task or revision?" with its first questions.
4. Checkpoint before long discovery (no files allowed: keep it in chat and say what can't be recovered).
5. A new, unrelated goal in a long session: checkpoint and offer a fresh session.

Also: `codebase-map`, `task-status`, `resume-task`.

## 3. Route

Read the checkpoint's `Agreement` and `Approval` lines (`legacy`: [RULES.md](RULES.md)). Take the first matching row:

| Task state | Next skill |
|---|---|
| New substantive goal, material scope change, no agreement for this revision, or a new request on an approved or delivered task (clarify decides: in-scope repair or new revision) | `workflow-clarify` |
| Agreement recorded; tickets or HTML plan not approved | `workflow-specify` |
| Execution handed off or stopped, or every ticket in a terminal state ([TASK-FOLDER.md](TASK-FOLDER.md)); delivery not recorded | `workflow-deliver` |
| Implementation approved and a ticket is ready | `workflow-execute` |
| Delivery recorded | Report it |

Invoke that skill now with the skill tool (plugin installs name it `workflow-axa:<name>`), or read its SKILL.md in full. The table holds no procedure: never run a phase from it. A missing phase skill blocks that phase; say so.

**Lightweight edit**: an exact, low-risk change that alters no behavior a user or caller can notice, and no architecture, interface, dependency or security. A visible behavior change, however small and fully specified, is not lightweight: it takes the two gates, or both at once when nothing is open. Edit at the owner, verify, review as [AUDIT.md](AUDIT.md) selects (the bundled code-review for code), then run `workflow-deliver` in its short form. 

## 4. The two gates

Defined in [VISUAL-REVIEW.md](VISUAL-REVIEW.md):

1. **Agreement** on behavior and scope. Permits the detailed plan, not code.
2. **Implementation approval** of tickets, tests and the HTML plan. STOP for user approval before application code.

Small changes with no open question may ask both at once, through `workflow-specify`. Answering grilling questions is not agreement, and a generic "go" is not approval of an unseen plan.

## Always

- Questions: `grilling`. Evidence: [GROUNDING.md](GROUNDING.md). Specialists: [SPECIALISTS.md](SPECIALISTS.md), never installed automatically ([SETUP.md](SETUP.md)). Reviews: [AUDIT.md](AUDIT.md). Output and artifact retention: [ARTIFACTS.md](ARTIFACTS.md).
- New helpers pass AUDIT.md's necessity check; unclear terms go to `domain-modeling`; consequential documents get WRITING.md's cold-reader check.
- Never stage, commit, push, branch, reset, deploy or publish unasked.
- Workers get the same output folder, write scope, rules and UI authority. Code changes go through `workflow-execute`. Read package files whole, never through `head` or `sed -n`.
- Don't end a turn while your own work runs unless the host will wake you. End every turn with one state line: **Running** (what, when you'll report), **Waiting on you** (the question) or **Done**.
- When the user must pass status to another session, person or tracker, write that message from the checkpoint ([CHATGPT-PROMPTS.md](CHATGPT-PROMPTS.md) "Handoff message").
- When needed: PDF-DELIVERABLE.md, CHATGPT-PROMPTS.md, OPTIONAL-HELPERS.md.
