---
name: workflow
description: Use when implementing a feature, fixing a bug, or changing behaviour in a codebase. Runs the work through subagents, tests, a handover document, and an audit of the staged changes before you commit.
---

Every task leaves a **relay**: a document the next agent, the next chat, or the next person can pick up cold and know what was done, what remains, and where you stopped.

The failure this flow exists to prevent is not a broken test. It is a green test suite beside a call site nobody looked at.

## 1. Classify what arrived

Read the request and pick one door. Do not proceed until you have picked.

**Trivial** — all four hold: one file, no logic or control-flow change, no new or changed behaviour, no new dependency. Typos, copy and translation strings, version bumps, comments, formatting. Make the change, then go straight to step 6. Skip the document and the subagents; the audit still runs.

**A prepared prompt** — the request already states the goal, the constraints, and what done looks like. Go to step 2.

**A bare goal** — a wish, a symptom, a feature name. It is not ready to implement. Run the `grilling` skill on it now and return here with what it settles.

> If `grilling` is not installed, stop and tell the user:
> `/plugin install mattpocock-skills`
> Wait. Do not improvise an interview in its place.

## 2. Ground yourself in the project's rules

Read the project's `AGENTS.md`, or its `CLAUDE.md` when there is no `AGENTS.md`. Follow what it says for the rest of this task.

When neither exists, write a short `AGENTS.md` first: the stack as it actually is, the commands that build and test, and the conventions a newcomer would otherwise guess wrong. Keep it under 200 lines — past that, adherence drops.

When the rules file names another file, open it. A rules file pointing at something that does not exist is a defect: say so, and fix it before you rely on it.

**Done when:** you can name the project's test command and its conventions without guessing.

## 3. Open the document

Ask the user whether this task continues an existing document or starts a new one, and have them give you the path. Do not guess.

New documents go in `docs/superpowers/plans/YYYY-MM-DD-<slug>.md` and hold two sections:

```markdown
## Open
- [ ] the work still to do, one bullet each

## Changelog
- YYYY-MM-DD — what changed, and why
```

Continuing an existing document means appending to its changelog, not starting a parallel record.

Update this document **as you work**, not at the end. A document written only at the end is a summary; the point is that a chat dying mid-task leaves something useful behind.

**Done when:** every piece of the task is a bullet under Open, and the path is known.

## 4. Implement through subagents

Three, every time:

1. **Implementer** — makes the change. Give it the task, the rules file, and the constraint that the result stays as simple as the problem allows.
2. **Test writer** — writes tests against the behaviour, not the implementation.
3. **Verifier** — checks the result against the project's rules and the original requirements, and reports what does not match.

Dispatch in the order that respects their dependencies; run independent ones together.

**Done when:** the verifier reports no unmet requirement, and every bullet under Open is either ticked or still listed with a reason.

## 5. Tests

Tests are never skipped and never left failing. When you hit one of these, ask the user and follow their answer:

- **A test fails** — fix it, change it, or remove it.
- **The runner is broken** — repair it as part of this task.
- **No framework exists for this layer** — ask what they want to do.

When the user chooses to proceed without tests, write this into the changelog before moving on:

```markdown
- ⚠️ untested — <what was not covered, and why>
```

That line is not optional. Without it, "we decided to skip tests here" and "tests passed" read identically three weeks later.

**Done when:** the test command has been run and its output seen, or a `⚠️ untested` line is in the changelog.

## 6. Stage and audit

Stage the changes: `git add` the files this task touched.

Then dispatch **one subagent** for the audit, and give it only the staged diff and the repository. It must not see this conversation — an audit that inherits your reasoning inherits the blind spot that caused the miss, and will confirm its own work. Cold eyes, or none.

Have it check all six:

1. Other places in the codebase that use the changed functionality and were not updated.
2. The same functionality reached a different way elsewhere — a second call path, an alternative helper, a duplicated implementation.
3. Edge cases and dependencies the implementation did not account for.
4. Best practice for the frameworks actually in use here.
5. Whether the code is clear, efficient, and maintainable.
6. Unnecessary complexity or duplication introduced.

Findings go back into the document's Open section. Act on them, or record why not.

**Done when:** every one of the six has a verdict, and nothing raised is left unaddressed and unexplained.

## 7. Stop

Report what changed, what the audit found, and where the document is.

**Do not commit. Do not push.** Staging is where this flow ends — the commit is the user's, on their branch, in their words.

## Writing the prompt elsewhere

Any assistant can write the prompt that starts this flow. See [`CHATGPT-PROMPTS.md`](./CHATGPT-PROMPTS.md) for what to ask for when you prepare a task prompt or an audit prompt outside this agent.
