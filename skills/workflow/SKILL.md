---
name: workflow
description: "Use for repository features, fixes, refactors, research, plans, audits and task resumption, including ordinary prompts. Find the task, check rules, route to the phase skill its records require: clarify, specify, execute or deliver. Explain-only stays read-only."
---

# Workflow

Route the task. **Invoke the phase skill §3 selects; ask only a blocking readiness question here; behavior questions and approvals belong to the phase.** Write for someone new to the project ([WRITING.md](WRITING.md)).

## 1. Check rules readiness

Read [RULES.md](RULES.md) before planning or writing, even if rule-maker never ran. Missing coverage: STOP and offer setup, a bounded exception, read-only inspection or stop. Application UI: read `../ui-design/SKILL.md` before planning. Never write or offer new CSS, even as an exception; record mode, mirrored elements, preview/release limits.

## 2. Find the task

1. State the repository, branch and local changes; never touch the user's edits.
2. Pick the mode. **Explain** is read-only; a later "fix it" or "push when done" makes it Implement: invoke `workflow-clarify`. **Research, plan or audit** never authorizes code. **Implement** passes the gates below.
3. Before creating any task folder, follow [TASK-FOLDER.md](TASK-FOLDER.md) to find and reuse the task. A new chat is not a new task. When a related task might match, create nothing: invoke `workflow-clarify`, which asks "separate task or revision?" with its first questions.
4. Checkpoint before long discovery (no files allowed: keep it in chat and say what can't be recovered).
5. A message that does not clearly belong to the active task: answer a question without touching records. Before any change, ask "part of <task>, or separate?", checkpoint and offer a fresh session.

Also: `codebase-map`, `task-status`, `resume-task`.

## 3. Route

Read the checkpoint's `Agreement` and `Approval` lines. Legacy single-gate approval covers only its recorded scope, not a new request. Take the first matching row:

| Task state | Next skill | Permission |
|---|---|---|
| Owner stops, pauses or cancels | `workflow-deliver` partial route | Handoff only; no new implementation or review loop |
| New goal, changed scope, no agreement, or new request on existing work | `workflow-clarify` | Investigate and agree behavior; no application edits |
| Agreed; tickets or HTML plan unapproved | `workflow-specify` | Prepare records/report; stop for approval |
| Stopped work handed off, or all tickets terminal; no delivery yet | `workflow-deliver` | Reconcile and report; no fixes |
| Approved ready ticket, or explicit continuation after Resume recheck | `workflow-execute` | Only the approved scope; publication is separate |
| Delivery recorded | Report it | No new work |


Invoke that skill now with the skill tool (plugin installs name it `workflow-axa:<name>`), or read its SKILL.md in full. The table routes; it does not replace a phase. A missing phase skill blocks that phase; say so.

**Lightweight edit**: an exact, low-risk change that alters no behavior a user or caller can notice, and no architecture, interface, dependency or security. A visible behavior change, however small and fully specified, is not lightweight: it takes the two gates, or both at once when nothing is open. Edit at the owner, verify, review as [AUDIT.md](AUDIT.md) selects (the bundled code-review for code), then run `workflow-deliver` in its short form. 

## 4. The two gates

Defined in [VISUAL-REVIEW.md](VISUAL-REVIEW.md):

1. **Agreement** on behavior and scope. Permits the detailed plan, not code.
2. **Implementation approval** of tickets, tests and the HTML plan. STOP for user approval before application code.

Answering grilling questions is not agreement, and a generic "go" is not approval of an unseen plan.

## Always

- Questions: `grilling`. Evidence: [GROUNDING.md](GROUNDING.md). Specialists: [SPECIALISTS.md](SPECIALISTS.md), never installed automatically ([SETUP.md](SETUP.md)). Reviews: [AUDIT.md](AUDIT.md). Output: [ARTIFACTS.md](ARTIFACTS.md).
- Use AUDIT.md for the necessity check, `domain-modeling` for unclear terms, and WRITING.md for the cold-reader check.
- Never stage, commit, push, branch, reset, deploy or publish unasked.
- Pass workers the output folder, write scope, rules and UI authority. Read applicable instructions whole; do not load unrelated references.
- Approval waits: present once, end the turn; no polling. Host goals: TASK-FOLDER.md "Approval waits and host goals". End with **Running**, **Waiting on you** or **Done**; do not end running work unless the host will wake you.
- Write requested handoffs from the checkpoint ([CHATGPT-PROMPTS.md](CHATGPT-PROMPTS.md)).
- When needed: PDF-DELIVERABLE.md, OPTIONAL-HELPERS.md.
