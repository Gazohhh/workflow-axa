---
name: code-review
description: "Review a diff on two separate axes, Standards and Spec. Use for a task's changes, a branch, a pull request or uncommitted work."
---

Two-axis review of a diff:

- **Standards**: does the code conform to this repo's documented coding standards?
- **Spec**: does the code faithfully implement the agreed spec?

The axes stay separate so one axis's findings don't mask the other's; then this skill aggregates their findings.

This package's `code-review` (plugin name `workflow-axa:code-review`) is the reviewer the workflow means. A host's built-in command or another installed skill with the same name is a different tool.

## Process

### 1. Pin the diff

In a task, review the task's own changes: staged, unstaged *and untracked*, measured against the starting `git status`/diff in the task records. `git diff <base>...HEAD` alone misses uncommitted work; when the user had edits before the task, separate theirs from yours. Never stage, commit, create a merge-base or fetch an issue just to get a diff.

For a branch or PR review outside a task, the fixed point is whatever the user said (a commit SHA, branch name, tag, `main`, `HEAD~5`, etc.); if they didn't specify one, ask. Capture the diff command once: `git diff <fixed-point>...HEAD` (three-dot, so the comparison is against the merge-base), and the commits via `git log <fixed-point>..HEAD --oneline`.

Before going further, confirm any ref resolves (`git rev-parse <ref>`) and the diff is non-empty. A bad ref or empty diff should fail here, not inside the reviewers.

### 2. Identify the spec source

In a task, the spec is the PLAN `## Agreement` and the approved tickets. A ticket review uses that ticket's acceptance and files; the whole-feature review uses the whole agreement and the whole task diff. No issue tracker is needed.

Outside a task, look in this order:

1. Issue references in the commit messages (`#123`, `Closes #45`, GitLab `!67`, etc.), when the tracker is reachable.
2. A path the user passed as an argument.
3. A spec file under `docs/`, `specs/`, or `.scratch/` matching the branch name or feature.
4. If nothing is found, ask the user where the spec is. If they say there isn't one, the **Spec** axis skips and reports "no spec available".

### 3. Identify the standards sources

Search the repo for every file that documents how code should be written, including AGENTS.md/CLAUDE.md. When `CODING_STANDARDS.md` or `CONTRIBUTING.md` exists, it must be on the list. Add the applicable workflow-axa shared rules (`../workflow/RULES.md`) and the `../workflow/AUDIT.md` categories.

On top of whatever the repo documents, the Standards axis always carries the **smell baseline** below: a fixed set of Fowler code smells (_Refactoring_, ch.3) that applies even when a repo documents nothing. Two rules bind it:

- **The repo overrides.** A documented repo standard always wins; where it endorses something the baseline would flag, suppress the smell.
- **Always a judgement call.** Each smell is a labelled heuristic ("possible Feature Envy"), never a hard violation. Like any standard here, skip anything tooling already enforces.

Each smell reads *what it is* → *how to fix*; match it against the diff:

- **Mysterious Name**: a function, variable, or type whose name doesn't reveal what it does or holds. → rename it; if no honest name comes, the design's murky.
- **Duplicated Code**: the same logic shape appears in more than one hunk or file in the change. → extract the shared shape, call it from both.
- **Feature Envy**: a method that reaches into another object's data more than its own. → move the method onto the data it envies.
- **Data Clumps**: the same few fields or params keep travelling together (a type wanting to be born). → bundle them into one type, pass that.
- **Primitive Obsession**: a primitive or string standing in for a domain concept that deserves its own type. → give the concept its own small type.
- **Repeated Switches**: the same `switch`/`if`-cascade on the same type recurs across the change. → replace with polymorphism, or one map both sites share.
- **Shotgun Surgery**: one logical change forces scattered edits across many files in the diff. → gather what changes together into one module.
- **Divergent Change**: one file or module is edited for several unrelated reasons. → split so each module changes for one reason.
- **Speculative Generality**: abstraction, parameters, or hooks added for needs the spec doesn't have. → delete it; inline back until a real need shows.
- **Message Chains**: long `a.b().c().d()` navigation the caller shouldn't depend on. → hide the walk behind one method on the first object.
- **Middle Man**: a class or function that mostly just delegates onward. → cut it, call the real target direct.
- **Refused Bequest**: a subclass or implementer that ignores or overrides most of what it inherits. → drop the inheritance, use composition.

### 4. Run both axes

Run each axis in a fresh subagent when the host has them: issue both calls together, in the foreground, and aggregate the reports they return. A fresh subagent that did not build the change is an **independent** review even when it runs both axes one after the other: label it "independent, axes sequential". When the builder reviews its own change, label it "self-review". Keep the axes separate either way.

**Standards prompt** should include:

- The diff (in a task: the changed and untracked files) and any commits.
- The list of standards-source files you found in step 3, **plus the smell baseline from step 3** pasted in full (the subagent has no other access to it).
- The brief: "Report, per file/hunk where relevant, (a) every place the diff violates a documented standard: cite the standard (file + the rule); and (b) any baseline smell you spot: name it and quote the hunk. Distinguish hard violations from judgement calls: documented-standard breaches can be hard, but baseline smells are always judgement calls, and a documented repo standard overrides the baseline. Skip anything tooling enforces. Under 400 words."

**Spec prompt** should include:

- The diff (in a task: the changed and untracked files) and any commits.
- The path or fetched contents of the spec.
- The brief: "Report: (a) requirements the spec asked for that are missing or partial; (b) behaviour in the diff that wasn't asked for (scope creep); (c) requirements that look implemented but where the implementation looks wrong. Quote the spec line for each finding. Under 400 words."

If the spec is missing, skip the Spec axis and note this in the final report.

### 5. Aggregate

Present the two reports under `## Standards` and `## Spec` headings, verbatim or lightly cleaned. Do **not** merge or rerank findings, because the two axes are deliberately separate (see _Why two axes_).

End with a one-line summary: total findings per axis, and the worst issue _within each axis_ (if any). Don't pick a single winner across axes: that's the reranking the separation exists to prevent.

### 6. After repairs

Rerun the affected checks and re-review the affected axis.

## Why two axes

A change can pass one axis and fail the other:

- Code that follows every standard but implements the wrong thing → **Standards pass, Spec fail.**
- Code that does exactly what the spec asked but breaks the project's conventions → **Spec pass, Standards fail.**

Reporting them separately stops one axis from masking the other.
