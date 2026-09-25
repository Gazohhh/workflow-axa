---
name: workflow
description: Use when implementing a feature, fixing a bug, or changing behaviour in a codebase. Investigates first, asks the plan and every question in one batch, then delegates to parallel subagents with tests, a persistent TODO and handover folder, architecture and flow doc updates, and a cold audit of the staged changes.
---

Every task leaves a **relay**: a task folder the next agent picks up cold and knows what was done, what remains, what was learned, and where you stopped.

The failure this flow prevents is a green test suite beside a call site nobody looked at, or beside a doc still describing the old system. **Docs are part of the implementation**: a change to architecture, ownership, dependencies, data flow, user flow, build flow, or runtime behaviour corrects the existing docs that describe it, in the same task.

## Batches

The user is interrupted exactly twice: **batch 1** (plan + every question, before any code) and **batch 2** (report + everything parked, after the audit).

- A batch is one message: numbered, a recommendation per item, then **end your turn**. Only the user's words clear it.
- Ask nothing while a subagent is running.
- Questions found mid-work **park**. Keep moving on everything that doesn't depend on them.

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

## 3. Investigate

Read `AGENTS.md` (else `CLAUDE.md`) and every file it points to; follow it for the whole task. A pointer to a missing file is a defect — say so. No rules file: offer one in batch 1.

Fan out **recon subagents**, as many at once as the harness allows, one question each:

- Where the behaviour lives today, and what already implements it.
- Every caller, and every other path to the same thing.
- What the tests cover, and whether the runner works.
- Constraints: types, migrations, shared state, public surface.
- Reach beyond the edited files: APIs, state, data flow, build, deploy, rendering, shared modules.
- Which docs describe this area (architecture, flows, `CONTEXT.md`, ADRs), and whether they match the code.
- Whether a task folder for this work already exists.

**Done when:** you can say what exists, what must change, what else it touches, and which docs describe it, without guessing.

## 4. Plan

**Claim one task folder.** Other workflows may be running in this repo at the same time, so their folders sit beside yours:

- **Continue** a folder only on evidence: the user named it, or its `PLAN.md` goal is this exact work.
- **Draft new** at `docs/plans/YYYY-MM-DD-<slug>/` per [TASK-FOLDER.md](TASK-FOLDER.md) when no folder matches.
- **Ask** in batch 1 when more than one could fit, or you are unsure. Being the newest folder, having a similar name, or holding a `[~]` item is not evidence; a `[~]` is another session's work in progress.

Once claimed, the folder is fixed for the whole task. Every `TODO.md`, `FINDINGS.md`, and `DECISIONS.md` write goes there and nowhere else. Other task folders are read-only. Shared files outside it (a `CHANGELOG.md`, a project-wide TODO) are written only when the plan names the exact file, and which one is a batch 1 question when it isn't obvious. If you lose track of which folder is yours, ask; never pick one to keep going.

`TODO.md` is the plan: every piece of work one item, doc updates included, each tagged with its lane.

**Lanes** are groups of items whose files don't overlap. Items writing the same file share a lane; an item needing another's output waits for it. A doc several lanes touch gets its own lane, after them.

**🛑 Batch 1** — the plan, `Task folder: <path>` on its own line, and every question. Nothing outside the task folder is written until an explicit go.

## 5. Implement

You orchestrate; subagents do the work. Run every ready lane at once, up to the harness maximum; start the next as soon as one finishes. Each lane runs sequentially:

1. **Implementer** — task folder, rules file, repo path. Makes the simplest change that works and corrects the docs in its lane.
2. **Test writer** — task folder and the implementer's diff. Tests behaviour, not implementation.

After every lane is done, one **verifier** gets the task folder, rules file, and full diff, and reports every unmet requirement in `PLAN.md`, broken rule, and stale doc.

- **Let every running subagent finish.** Never stop, redirect, or message one mid-run, or touch files its lane owns. A cross-lane effect becomes a finding and a queued follow-up item.
- **The task folder is yours alone.** Subagents report back; you update it as you go, not at the end: `[~]` on start, findings the moment they appear, `[x]` only with proof you have seen.
- **Tests are never skipped or left failing.** A failing test, a broken runner, or a layer with no framework is the user's call — park it. Skipping tests writes a `⚠️ untested` line to `FINDINGS.md`.

**Done when:** the verifier reports nothing, the test command has run and its output was seen, and every item is `[x]` with proof or open with its reason in `FINDINGS.md`.

## 6. Stage and audit

`git add` this task's files only; leave anything already staged alone.

Dispatch one audit subagent with **cold eyes**: the repo path, this task's diff, `PLAN.md`, and [AUDIT.md](AUDIT.md) — nothing from this conversation. Findings go to `FINDINGS.md` and become `TODO.md` items. Fix them, audit the new diff once more, then stop.

On a trivial task, a real finding means the classification was wrong: open a task folder and restart from step 4.

**Done when:** every check has a verdict and nothing raised is unaddressed or unexplained.

## 7. Report

**🛑 Batch 2** — what changed, what the audit found, which docs were updated, `Task folder: <path>`, what is still open, and every parked question.

Do not commit or push. The commit is the user's.

Preparing a task or audit prompt in another assistant: [CHATGPT-PROMPTS.md](CHATGPT-PROMPTS.md).
