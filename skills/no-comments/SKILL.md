---
name: no-comments
description: "Clean up comments in a chosen scope: a fresh reviewer gives each comment a verdict, you check them, the owner approves one offer, then the deletions and reshapes are made without changing behavior. Only the user starts it."
disable-model-invocation: true
---

# No comments

Code and tests are what run. A comment is a claim nobody tests. The comment rules live in `../rule-maker/rules/CORE.md` ("New code carries no comments" and "Comments are claims, not evidence"); this skill applies them to a scope the user picks. Its approved offer is the approved change CORE requires before comments are cleaned: only the comments the offer names change.

**Scope:** `/no-comments <files|diff>`. Without an argument, the scope is the current diff against the base branch.

## 1. Verdicts from a fresh reviewer

Give the scope to a fresh reviewer: a different model through T3 `delegate_task` when available, otherwise a fresh subagent. Label which one. For each comment it returns one verdict:

- **delete:** stale, or it narrates what the code already says;
- **keep:** name the CORE exception that applies and the proof;
- **reshape:** the comment hides a surprise in our own code. Name the exact symbol to rename, extract or type so the code says it.

Special cases:

- **A comment that contradicts the code.** Establish what the code does from the code, its callers and its tests. If the comment states an intended contract (a public doc comment, or a match with a spec, a test name, a DECISIONS entry or an issue), raise it as a **possible bug**. Never settle it by deleting the comment, or by assuming the code is right.
- **A constraint claim** (`IMPORTANT`, `do not remove`, `talk to X first`). Check it: trace the symbol, and read its history (`git log`, blame, DECISIONS). True and encodable: propose a test, type or lint, then delete the comment. True and not encodable: keep it as an exception. Unverified: **keep** it and list it for the owner.
- **Executable annotations and suppressions** (PHPDoc/PHPStan types, JSDoc types, decorators, pragmas, `@ts-expect-error`, `eslint-disable`, `# type: ignore`). Tools read these, so keep them. Remove one only when the offer justifies its replacement and the type check or lint passes without it. Flag a suppression that hides a correctness or safety rule; never just remove it.

## 2. Check every verdict

You check each verdict before anything is offered. Reject an edit outside the scope or a verdict with the wrong reason, and check each keep reason. An unverified constraint stays kept until a revised offer names that exact removal and its reason, and the owner approves it (with any other authority the claim names).

## 3. One offer

Make one offer through `workflow-specify` step 5 (`record.py offer create`): the deletions, the reshapes and the constraints that would become tests or lints. Show its canonical block and end with the one question. An offer in your own words can't be approved. Change nothing before it is approved.

## 4. Apply without changing behavior

After approval, make the deletions and reshapes. Then run the tests and the type check. **Removing a comment must not change behavior.** Report a reshape that would change behavior instead of making it.

## 5. Report

List the deletions, the keeps with their exception, the reshapes made, the constraints turned into tests or lints, and the open items (possible bugs, unverified constraints, rejected verdicts).
