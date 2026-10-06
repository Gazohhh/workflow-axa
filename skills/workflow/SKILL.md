---
name: workflow
description: Use when implementing a feature, fixing a bug, or changing behaviour in a codebase. Investigates first, clarifies without assumptions, batches the plan, then delegates to parallel subagents with tests, a persistent TODO and handover folder, architecture and flow doc updates, and a cold audit of the staged changes. When a PDF deliverable is requested alongside the work, adds an owner-confirmed, reader-focused PDF with source, comprehension and product-language validation.
---

Every task leaves a **relay**: a task folder the next agent picks up cold and knows what was done, what remains, what was learned, and where you stopped.

The failure this flow prevents is a green test suite beside a call site nobody looked at, or beside a doc still describing the old system. **Docs are part of the implementation**: a change to architecture, ownership, dependencies, data flow, user flow, build flow, or runtime behaviour corrects the existing docs that describe it, in the same task.

## Optional PDF mode

When the user requests a PDF deliverable alongside the workflow task, read [PDF-DELIVERABLE.md](PDF-DELIVERABLE.md) before planning or drafting and follow it alongside the seven steps below. Load that reference only for a requested PDF; ordinary tasks follow the existing flow.

PDF work requires a claimed task folder and the normal plan/approval path even when the implementation would otherwise be trivial: use step 3 for a prepared request, or step 2 if the goal is unsettled. In batch 1 present the PDF audience and terminology map for explicit owner confirmation before drafting. Add the PDF, editable source, working records, rendering and review work to the plan and TODO; keep dependent drafting paused until the language gate is satisfied. Include the PDF artifacts in verification and the staged audit, and apply the reference's final-version completion gate before batch 2. The technical relay remains separate from the reader document.

## Batches

Use **batch 1** (plan + known questions, before any code) and **batch 2** (report, after the audit). Clarifications take priority over batching, at every step, including trivial tasks.

- Group known questions: numbered, a recommendation per item, then **end your turn**. Each needs an explicit answer; silence, partial replies, and plan approval do not answer omitted questions.
- **Never assume.** Use confirmed instructions and verified facts. When anything is unclear, unknown, or unanswered, **stop, ask, and end your turn**. Resume dependent work only after an explicit answer. Independent background tasks may continue while you wait.

```
❓ **Q1** — **<title>**: <question, with options>

➡️ <your recommended answer>
```

## 1. Pin and classify

Say `Working in <repo path> — say if that's wrong.` Other directories your session can reach are out of scope.

Pick one door and say why in one line:

- **Trivial** — one file, no logic change, no behaviour change, no new dependency (typos, strings, version bumps). Make the change, go to step 6. No task folder, no batches.
- **Prepared prompt** — goal, constraints, and done are already stated. Go to step 3.
- **Bare goal** — a wish, a symptom, a feature name. Go to step 2.

## 2. Settle the goal

Run the `grilling` skill to the end, until the user confirms shared understanding. Its outcome is your prepared prompt. If `grilling` is missing, tell the user `/plugin install mattpocock-skills` and end your turn.

## 3. Open and investigate

Read `AGENTS.md` (else `CLAUDE.md`) and every file it points to; follow it for the whole task. A pointer to a missing file is a defect — say so. No rules file: offer one in batch 1.

**Claim one task folder before investigation or recon dispatch:**

- **Continue** only when the user names it or its `PLAN.md` goal is this exact work. Read it before writing; preserve its history.
- **Create** `docs/plans/YYYY-MM-DD-<slug>/` per [TASK-FOLDER.md](TASK-FOLDER.md) when no folder matches; use the session's current date.
- **Ask and wait** if the match is uncertain. Newest, similar names, and `[~]` items are not evidence; `[~]` may belong to another session.

Read related task folders for prior evidence; they remain read-only. Initialize the claimed folder with confirmed facts and explicit unknowns, then tell the user its path and your understanding of the issue. Keep status, findings, and outcome current throughout the task, including later turns.

Once claimed, the folder is fixed. All task records and supporting artifacts go there. Shared files outside it are written only when the approved plan names the exact file; ask if unclear. If you lose track of your folder, ask rather than choose another.

Fan out **recon subagents**, as many at once as the harness allows, one question each:

- Where the behaviour lives today, and what already implements it.
- Every caller, and every other path to the same thing.
- What the tests cover, and whether the runner works.
- Constraints: types, migrations, shared state, public surface.
- Reach beyond the edited files: APIs, state, data flow, build, deploy, rendering, shared modules.
- Which docs describe this area (architecture, flows, `CONTEXT.md`, ADRs), and whether they match the code.

**Done when:** you can say what exists, what must change, what else it touches, and which docs describe it, without guessing.

## 4. Plan

`TODO.md` is the plan: every piece of work one item, doc updates included, each tagged with its lane.

**Lanes** are groups of items whose files don't overlap. Items writing the same file share a lane; an item needing another's output waits for it. A doc several lanes touch gets its own lane, after them.

**🛑 Batch 1** — the plan, `Task folder: <path>` on its own line, and every question. Nothing outside the task folder is written until an explicit go.

## 5. Implement

You orchestrate; subagents do the work. Run every ready lane at once, up to the harness maximum; start the next as soon as one finishes. Each lane runs sequentially:

1. **Implementer** — task folder, rules file, repo path. Makes the simplest change that works and corrects the docs in its lane. Subagents report uncertainties and pause dependent work for your clarification with the user.
2. **Test writer** — task folder and the implementer's diff. Tests behaviour, not implementation.

After every lane is done, one **verifier** gets the task folder, rules file, and full diff, and reports every unmet requirement in `PLAN.md`, broken rule, and stale doc.

- **Let every running subagent finish.** No stopping, redirecting, messaging mid-run, or touching its files, except to pause dependent work or relay the user's clarification. Queue cross-lane findings as follow-up items.
- **The task folder is yours alone.** Subagents report back; you update it as you go, not at the end: `[~]` on start, findings the moment they appear, `[x]` only with proof you have seen.
- **Tests are never skipped or left failing without the user's decision.** A failing test, a broken runner, or a layer with no framework needs clarification immediately. An approved skip writes a `⚠️ untested` line to `FINDINGS.md`.

**Done when:** the verifier reports nothing, the test command has run and its output was seen, and every item is `[x]` with proof or open with its reason in `FINDINGS.md`.

## 6. Stage and audit

`git add` this task's files only; leave anything already staged alone.

Dispatch one audit subagent with **cold eyes**: the repo path, this task's diff, `PLAN.md`, and [AUDIT.md](AUDIT.md) — nothing from this conversation. Findings go to `FINDINGS.md` and become `TODO.md` items. Fix them, audit the new diff once more, then stop.

On a trivial task, a real finding means the classification was wrong: restart from step 3.

**Done when:** every check has a verdict and nothing raised is unaddressed or unexplained.

## 7. Report

**Completion gate:** every clarification has an explicit answer and its dependent work is resolved. Unanswered questions block the final report; ask and wait instead.

For tasks with a folder, record the verified outcome and mark `done` only when all approved work is complete; otherwise retain the open status and remaining work.

**🛑 Batch 2** — what changed, what the audit found, which docs were updated, `Task folder: <path>`, and what is still open.

Do not commit or push. The commit is the user's.

Preparing a task or audit prompt in another assistant: [CHATGPT-PROMPTS.md](CHATGPT-PROMPTS.md).
