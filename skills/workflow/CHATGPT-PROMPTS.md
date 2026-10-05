# Preparing prompts outside the agent

Two moments in the flow benefit from a second assistant: writing the task prompt before you start, and writing the audit prompt after implementation. Neither is required — the skill runs without them — but on a large task a prompt sharpened somewhere else arrives better than one improvised here.

Use whichever assistant you like. The flow does not care which one wrote the prompt.

## Preparing a task prompt

Explain the problem or the feature in your own words, then ask for a prompt that carries these:

- Small and specific. Only what the agent needs to do this task well.
- Delegate the work to subagents: one to implement, one to write tests, one to verify the result against the project's rules and requirements.
- Keep the code as simple as the problem allows; no complexity the task did not ask for.
- Follow the project's `AGENTS.md` (or `CLAUDE.md`), and write one first if it is missing.
- Open the task folder before investigation per [TASK-FOLDER.md](TASK-FOLDER.md). Keep its issue, status, outcome, TODO, investigation history, and decisions current across turns. Resume an exact matching task; use related histories as evidence. Ask and wait on uncertainty; every clarification needs an answer before completion.
- Update the project's architecture and flow docs wherever the change makes them false, as part of the task, not after it.

Read what comes back before you use it. Push back on anything vague, wrong, or missing — a prompt you had to argue with is usually the one worth pasting.

**Run it to completion:** if you want the task finished without check-ins along the way, say so in the prompt. It is a sentence, not a command.

## Preparing an audit prompt

After implementation, ask for a short prompt that audits the current staged changes against every check in [`AUDIT.md`](./AUDIT.md).

The audit exists for one reason: tests can pass while a second call site, untouched and unnoticed, is now broken — or while the architecture doc still describes the old system.

The skill runs those checks by itself in a fresh subagent. Preparing the prompt elsewhere is worth it when the change is large enough that you want a second opinion on what to even look for.
