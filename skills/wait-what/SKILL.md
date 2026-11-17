---
name: wait-what
description: "Re-explain your last message in plain words when the user types /wait-what because it didn't land. No new work, no change to any offer or decision."
disable-model-invocation: true
---

# Wait, what?

The user didn't follow your last message. Say the same thing again, more clearly. Add nothing new.

1. **Context first**, in two or three sentences: what we're doing, where we are, why this point matters.
2. **Then the point**, in plain words:
   - one idea per sentence, about 20 words at most;
   - the actor first, in the active voice ("the hook refuses the write");
   - a common word over a rare one, and the same word for the same thing each time;
   - a term from the project's `CONTEXT.md` keeps its name and gets a short definition the first time;
   - concrete names, numbers and file paths instead of "it" or "this".
3. **End with the question that was pending, unchanged.** For an offer that waits for an answer, present the same offer again exactly as `workflow-specify` step 5 says: run `record.py offer present` (with `--question` for the question tool) and use its output unchanged. It prints the same offer every time, so this is not rebuilding it. If that offer was superseded or revoked, say so instead. Never rebuild, shorten or change an offer. Repeat any other pending question word for word.

Limits:

- Tool calls: only reading `CONTEXT.md` and `../workflow/WRITING.md`, when they aren't loaded yet, and `record.py offer present` for a pending offer, which only prints it. If either is missing, the bullets above are enough.
- No new work, no edits, no records. No offer or decision changes.
- `/wait-what` is not an answer. A pending offer stays pending, and only the answer after its re-presentation counts.
