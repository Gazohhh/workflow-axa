---
name: workflow
description: Use when implementing a feature, fixing a bug, or changing behaviour in a codebase. Settles the goal, plans it for your approval, then runs the work through subagents, tests, a handover document, and an audit of the staged changes before you commit.
---

Every task leaves a **relay**: a document the next agent, the next chat, or the next person can pick up cold and know what was done, what remains, and where you stopped.

The failure this flow exists to prevent is not a broken test. It is a green test suite beside a call site nobody looked at.

## Checkpoints

Four moments belong to the human. At each one, ask your question and **end your turn**. Answering it yourself and continuing is the single worst thing you can do in this flow.

| # | Checkpoint | Cleared by |
|---|---|---|
| 1 | The request is underspecified | The user confirms, through `grilling`, that the goal is settled |
| 2 | The plan | The user gives an explicit go |
| 3 | Which document | The user names the path |
| 4 | Tests cannot run | The user chooses what to do |

A step's `Done when:` measures your work. A checkpoint measures the user's answer, and only their words clear it. Silence is not a go.

## 1. Pin the repo, then classify

Say where you are working before anything else:

> Working in `<repo path>` — say if that's wrong.

Everything this task touches lives inside that path. Your session may be able to reach other directories; they are out of scope. Read them only when the user asks you to.

Then pick one door and say which, in one line, with the reason.

**Trivial** — all four hold: one file, no logic or control-flow change, no new or changed behaviour, no new dependency. Typos, copy and translation strings, version bumps, comments, formatting. Announce the classification, make the change, then go to step 6. No document, no subagents, no go gate — the audit still runs.

**A prepared prompt** — the request already states the goal, the constraints, and what done looks like. Go to step 3.

**A bare goal** — a wish, a symptom, a feature name. It is not ready to implement. Go to step 2.

## 2. Settle the goal

Run the `grilling` skill on the request. Let it interview the user to the end — it finishes when its own frontier is empty and the user confirms a shared understanding.

> If `grilling` is not installed, tell the user:
> `/plugin install mattpocock-skills`
> **End your turn.** Do not improvise an interview in its place.

**🛑 Checkpoint 1.** Implementation starts after the interview is finished and confirmed, never during it. An unanswered question is an unsettled requirement, and code written against it is code written against a guess.

When it settles, carry its outcome into step 3 as your prepared prompt.

## 3. Ground yourself in the project's rules

Read the project's `AGENTS.md`, or its `CLAUDE.md` when there is no `AGENTS.md`. Follow what it says for the rest of this task.

When the rules file names another file, open it. A rules file pointing at something that does not exist is a defect: say so, and treat what remains as the rules.

When neither file exists, say so and offer to write a short `AGENTS.md` — the stack as it actually is, the build and test commands, and the conventions a newcomer would guess wrong. Keep it under 200 lines. It is an offer, not a detour you take alone, and the task continues either way.

**Done when:** you can name the project's test command and its conventions without guessing.

## 4. Plan, and wait for the go

Ask the user whether this continues an existing document or starts a new one, and have them give you the path.

**🛑 Checkpoint 3.** Do not guess the path and do not pick for them.

New documents go in `docs/superpowers/plans/YYYY-MM-DD-<slug>.md`:

```markdown
## Open
- [ ] the work still to do, one bullet each

## Changelog
- YYYY-MM-DD — what changed, and why
```

Draft the Open list. **These bullets are the plan** — every piece of the task, one per line, specific enough that someone else could pick up any single bullet. Continuing an existing document means appending to it, not starting a parallel record.

Show the list and stop.

**🛑 Checkpoint 2.** No file outside the document is written until the user says go. If they change the plan, redraft and ask again.

**Done when:** the user has given an explicit go on the Open list.

## 5. Implement through subagents

Three, in this order, each waiting for the one before it:

1. **Implementer** — receives the plan, the rules file, and the repo path. Makes the change, and keeps it as simple as the problem allows.
2. **Test writer** — receives the plan and the implementer's diff. Writes tests against the behaviour, not the implementation.
3. **Verifier** — receives the plan, the rules file, and the full diff. Reports every requirement not met and every rule not followed.

Sequential, always. The test writer cannot test code that does not exist yet, and two subagents writing the same files collide.

Keep the document current **as you go**, not at the end. A chat that dies mid-task should still leave something useful behind.

**Done when:** the verifier reports no unmet requirement, and every bullet under Open is ticked or still listed with a reason.

## 6. Tests

Tests are never skipped and never left failing.

- **A test fails** — fix it, change it, or remove it.
- **The runner is broken** — repair it as part of this task.
- **No framework exists for this layer** — ask what the user wants to do.

**🛑 Checkpoint 4.** Each of those is the user's call. Ask, end your turn, follow the answer.

When the user chooses to proceed without tests, write this into the changelog before moving on:

```markdown
- ⚠️ untested — <what was not covered, and why>
```

That line is not optional. Without it, "we decided to skip tests here" and "tests passed" read identically three weeks later. On a trivial task with no document, say it in your final report instead.

**Done when:** the test command has been run and its output seen, or the `⚠️ untested` line is written.

## 7. Stage and audit

Stage this task's files: `git add <the files you changed>`. Leave anything already staged alone.

Dispatch **one subagent** for the audit. Give it three things and nothing else: the repo path, the diff for this task's files, and the six checks. It must not see this conversation — an audit that inherits your reasoning inherits the blind spot that caused the miss, and will confirm its own work. Cold eyes, or none.

It reports on what this task changed. Pre-existing code is out of scope unless the user asks for it.

The six:

1. Other places in the codebase that use the changed functionality and were not updated.
2. The same functionality reached a different way elsewhere — a second call path, an alternative helper, a duplicated implementation.
3. Edge cases and dependencies the implementation did not account for.
4. Best practice for the frameworks actually in use here.
5. Whether the code is clear, efficient, and maintainable.
6. Unnecessary complexity or duplication introduced.

Findings go into the document's Open section. Act on them, then **run the audit once more** on the new diff — a fix made under audit pressure is the one change in this flow that nothing else checks. Stop after that second pass and report whatever still stands.

**On a trivial task, a real finding means the classification was wrong.** A second call site was never a one-file change. Open a document, put the finding in it, and run the task properly from step 4.

**Done when:** all six have a verdict, and nothing raised is left unaddressed and unexplained.

## 8. Stop

Report what changed, what the audit found, and where the document is.

**Do not commit. Do not push.** Staging is where this flow ends — the commit is the user's, on their branch, in their words.

## Writing the prompt elsewhere

Any assistant can write the prompt that starts this flow. See [`CHATGPT-PROMPTS.md`](./CHATGPT-PROMPTS.md) for what to ask for when you prepare a task prompt or an audit prompt outside this agent.
