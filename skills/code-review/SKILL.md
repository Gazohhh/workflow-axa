---
name: code-review
description: "Review a diff on two separate axes, Standards and Spec. Use for a task's changes, a branch, a pull request or uncommitted work. Also use for \"what could this change break?\" about a diff, a symbol or a planned change: the blast-radius method, report only."
---

Review a diff on two axes, kept separate so one can't mask the other:

- **Standards**: does the code conform to this repo's documented coding standards?
- **Spec**: does the code faithfully implement the agreed spec?

The workflow means this package's `code-review` (`workflow-axa:code-review`), never a host's same-named command or skill.

## Impact questions

A question such as "what could this change break?" about a diff, a symbol or a planned change, with no review requested, skips the two axes. Follow [BLAST-RADIUS.md](BLAST-RADIUS.md) alone: no two-axis review, report only, no edits and no task records.

## What counts as a finding

A finding counts only with one of these:

- a command that reproduces the failure, with its output; or
- a concrete `file:line` plus the failure it causes: wrong output, a crash, a broken contract or caller, a missing requirement, or a breach of a documented standard quoted with its file and rule.

Everything else is a **note**: speculative concerns, style-only or naming remarks, and baseline smells with no failure behind them. Notes are reported and never start a repair round.

## Process

### 1. Pin the diff

In a task, review its own changes: staged, unstaged *and untracked*, against the starting `git status`/diff in the task records, with the user's earlier edits kept apart. Never stage, commit, create a merge-base or fetch an issue just to get a diff.

Outside a task, ask for the fixed point (SHA, branch, tag) unless the user named one; capture `git diff <fixed-point>...HEAD` and `git log <fixed-point>..HEAD --oneline` once, after `git rev-parse <ref>` resolves and the diff is non-empty.

### 2. Identify the spec source

In a task, the spec is the PLAN `## Agreement` and the approved tickets: a ticket review uses that ticket's acceptance and files, the whole-feature review the whole agreement and task diff.

Outside a task, look in order: issue references in the commits (`#123`, `Closes #45`) when the tracker is reachable; a path the user passed; a matching spec under `docs/`, `specs/` or `.scratch/`. Otherwise ask; with none, the **Spec** axis reports "no spec available".

### 3. Identify the standards sources

List every file that documents how code should be written, including AGENTS.md/CLAUDE.md, and `CODING_STANDARDS.md` or `CONTRIBUTING.md` when present. Add the applicable shared rules (`../workflow/RULES.md`) and the `../workflow/AUDIT.md` categories.

Standards always carries this **smell baseline** (Fowler, _Refactoring_ ch.3). A documented repo standard wins and suppresses a smell it endorses. Each smell is a labelled judgement call ("possible Feature Envy"), never a hard violation; skip what tooling enforces. *What it is* → *fix*:

- **Mysterious Name**: a name that hides what it does or holds. → rename.
- **Duplicated Code**: one logic shape in several hunks or files. → extract it.
- **Feature Envy**: a method using another object's data more than its own. → move it there.
- **Data Clumps**: fields or params that always travel together. → one type.
- **Primitive Obsession**: a primitive standing in for a domain concept. → a small type.
- **Repeated Switches**: the same `switch`/`if`-cascade recurs. → polymorphism or one shared map.
- **Shotgun Surgery**: one change forces edits across many files. → gather it into one module.
- **Divergent Change**: one module edited for unrelated reasons. → split it.
- **Speculative Generality**: abstraction for needs the spec doesn't have. → inline it.
- **Message Chains**: long `a.b().c().d()` navigation. → one method on the first object.
- **Middle Man**: code that mostly delegates onward. → call the target directly.
- **Refused Bequest**: a subclass overriding most of what it inherits. → composition.

Standards also always checks:

- **Comments** (from `../rule-maker/rules/CORE.md`): flag a new comment unless it is one of these: a licence header; a constraint the project can't change (vendor, platform, protocol), with its link; a public API doc comment; text a tool reads (a formatter or static-analysis directive, Rust `// SAFETY:`); an issue link; an exception the project adds. Flag a comment in the diff that contradicts the code, and when it states an intended contract, report it as a possible bug.
- **Reader load** (a judgement call): too much to hold at once: many live values, a flag that changes a function's meaning, indirection that buys nothing. → split, name or inline.

### 4. Run the axes

With subagents, review in a fresh one that did not build the change, in the foreground:

- **One reviewer for both axes** when the diff is one ticket or one lightweight edit, step 4b's trigger does not fire, and it is modest (about 300 changed lines or fewer in `git diff --stat`). Label it "independent, axes sequential"; it writes the two reports separately.
- **One reviewer per axis**, both started together, for anything larger, multi-ticket or triggered.

Without subagents the builder reviews its own change, labelled "self-review", still axis by axis.

Every brief includes the diff (in a task: the changed and untracked files), any commits, and "What counts as a finding" pasted in full.

**Standards brief** also includes:

- The standards-source files from step 3, **plus the smell baseline and the comment and reader-load checks from step 3** pasted in full (the subagent has no other access to them).
- When the diff changes prose (docs, Markdown, comments), the Unslop check of `../workflow/WRITING.md` and its tells, pasted in full; each tell is a note.
- "Report each breach of a documented standard with its file and rule; name each baseline smell, quoting the hunk, as a note. Under 400 words."

**Spec brief** also includes the spec's path or contents and: "Report requirements missing or partial, behaviour nobody asked for (scope creep), and requirements implemented wrongly. Quote the spec line for each. Under 400 words." With no spec, skip this axis and say so.

### 4b. Blast radius

Run this step when anything outside the diff reads what changed: an exported symbol, a shared module, a schema or DB column, an API or JSON shape, a wire or file format, a configuration key, a feature flag, saved data, timing or lifecycle, a dependency version, or deleting or replacing a function its callers use, private ones included. Follow [BLAST-RADIUS.md](BLAST-RADIUS.md) on the diff. When the task records list safety assumptions with their checks, prove those, and reopen any assumption that the implementation or new evidence changes or contradicts. Put the result under `## Standards` as its own item, "Blast radius". When nothing outside the diff reads what changed, the item says "none" with the boundary trace that shows it. This step reports only.

### 5. Aggregate

Present the reports under `## Standards` and `## Spec`, findings then notes, verbatim or lightly cleaned. Do **not** merge or rerank findings across axes. End with one line: counts per axis and the worst finding _within each axis_, never one winner across them.

### 6. After repairs

Only findings start a repair round. Rerun the affected checks and re-review the affected axis on the repair diff.
