# Changelog

Notable changes to the `workflow` skill. Versions are git tags; this file says what each one changed and why.

## 1.3.0 — 2026-09-24

The relay said what was done and what remained, but not what was learned, and nothing kept the project's own docs honest. Tests could pass beside an architecture doc that still described the old system.

### Added

- **Documentation is part of the implementation.** A change to architecture, ownership, dependencies, data flow, user flow, build flow, or runtime behaviour updates the project's existing docs in the same task, before its item is ticked. Stale text is corrected or deleted, not duplicated.
- **Recon finds the docs and the reach.** Two new recon questions: what the change touches beyond the edited files, and which docs describe the area today.
- **A task folder replaces the single task document**, and moves from `docs/superpowers/plans/` to `docs/plans/YYYY-MM-DD-<slug>/`. `PLAN.md`, `TODO.md`, `FINDINGS.md`, and `DECISIONS.md` (created on the first decision; ADRs in `docs/adr/` for hard-to-reverse architecture calls).
- **TODO states with proof.** `[ ]`, `[~]` (one per running lane: where the last agent stopped), and `[x]` only with its proof seen.
- **Maximum parallel delegation.** The orchestrator delegates every TODO item and fans out to the harness's concurrency limit. Items are grouped into lanes with non-overlapping files; lanes run at once, each as implementer → test writer, and the verifier runs once over the full diff when all lanes are done. Running subagents are never interrupted: cross-lane effects become findings and queued follow-ups.
- **A seventh audit check.** Docs that no longer match the code, and whether the diff delivers the goal in `PLAN.md`. The verifier checks docs too.

### Changed

- **SKILL.md is roughly half its old length.** Formats moved to `TASK-FOLDER.md`, the audit checks to `AUDIT.md` (now the single copy; `CHATGPT-PROMPTS.md` points to it). Tests folded into the implement step, so there are seven steps instead of eight.
- **An existing task folder is continued**, not duplicated. Recon looks for one before planning.

### Fixed

- **Parallel workflows no longer write to each other's task folders.** With several workflows running in one repo, the agent sometimes guessed which folder or changelog to update. It now claims one folder in batch 1 (`Task folder: <path>`) on evidence only: the user named it, or its `PLAN.md` goal is this exact work. Recency, a similar name, or an in-progress `[~]` item do not count. When unsure it asks. Other task folders are read-only, and shared files like `CHANGELOG.md` are written only when the plan names them.
- **Findings are written as they happen**, not at the end; audit findings go to `FINDINGS.md` and become `TODO.md` items.
- The `⚠️ untested` line moves from the changelog to `FINDINGS.md`.

## 1.2.0 — 2026-09-18

1.1.0 stopped the agent from implementing before its questions were answered, but let the questions leak out one at a time, mid-flight, while subagents were still reporting. And it asked them before reading any code, which made them unanswerable.

### Added

- **An investigation step.** The flow now reads the codebase before it plans: parallel recon subagents map what exists, every call site, what the tests cover, and what constrains the change. This step was in the original team flow document — *"bestaande implementaties en relevante code controleren"* — and was missing from 1.0.0 and 1.1.0. Its absence is why the plan's questions were uninformed.
- **Two batches, and nothing in between.** The user is interrupted exactly twice: once after investigation with the plan and every question, once at the end with the report and anything that came up. Each batch is one numbered message with a recommendation per item, and it ends the agent's turn.
- **A parallelism rule.** Subagents run in parallel when they only read or touch different files, sequentially when one needs another's output or they would write the same file. Recon fans out; implementer → test writer → verifier does not.

### Fixed

- **No question is asked while a subagent is running.** Every dispatched agent finishes first. A question arriving beside a half-finished recon report was the reported mess.
- **Questions found mid-work park instead of interrupting.** Work continues on everything that does not depend on the answer; the agent stops early only when nothing else can move.
- **The document choice and the go are one round.** They were two separate asks inside a single step, which cost two round-trips.
- **Test decisions park for batch 2** rather than firing their own interruption.

## 1.1.0 — 2026-09-18

The 1.0.0 skill would start implementing before its questions were answered. It no longer can.

### Added

- **Checkpoints.** Four moments now belong to the human, named in a table near the top and marked 🛑 at each site: the goal is settled, the plan is approved, the document is chosen, and a test decision is made. Each one ends the agent's turn. `Done when:` measures the agent's work; a checkpoint measures the user's answer, and only their words clear it.
- **A plan, and a go gate before any code.** The document's Open list is the plan. The agent drafts it, shows it, and stops. Nothing outside the document is written until the user says go.
- **Repo pinning.** The agent states which repository it is working in before anything else, and treats every other directory its session can reach as out of scope. Sessions configured with additional working directories were sending recon into unrelated products.

### Fixed

- **Grilling no longer runs half-way.** The interview must finish and be confirmed before implementation; its outcome then becomes the prepared prompt. The old "return here with what it settles" assumed a frame that was long gone by the time the interview ended.
- **Subagents are strictly sequential.** The previous "run independent ones together" could dispatch the implementer and test writer onto the same files at once.
- **The audit is scoped to this task.** It sees only the diff for the files this task changed, leaves anything already staged alone, and treats pre-existing code as out of scope unless asked.
- **The audit runs twice.** A fix made in response to a finding was the one change in the flow that nothing checked. Capped at a second pass.
- **A real finding promotes a trivial task out of trivial.** A second call site was never a one-file change; the task restarts properly with a document.
- **Writing a missing `AGENTS.md` is an offer, not a detour.** It was an unbounded side-quest the agent took alone.
- **Every subagent's inputs are specified.** Previously only the implementer's were.
- **The `⚠️ untested` line has somewhere to go on a trivial task** — the final report, since there is no document.

## 1.0.0 — 2026-09-18

First release.

### Added

- **`workflow` skill** — the team development flow, end to end:
  - Classifies incoming work into three doors: a prepared prompt, a bare goal (handed to `grill-me`), or a trivial change that skips the flow but still gets audited.
  - Reads the project's `AGENTS.md` / `CLAUDE.md` before touching anything, and writes one when neither exists.
  - Keeps a handover document at `docs/superpowers/plans/YYYY-MM-DD-<slug>.md` with open items and a changelog, updated during the work rather than at the end.
  - Runs every task through three subagents: implementer, test writer, verifier.
  - Never skips tests. When tests can't run, asks — and records a `⚠️ untested` line in the changelog when the answer is to proceed without them.
  - Audits the staged changes in a **fresh subagent** that sees only the diff and the repo, never the implementation conversation.
  - Stages and stops. Commits stay with the human.
- **`CHATGPT-PROMPTS.md`** — what to ask for when preparing a task prompt or an audit prompt outside the agent.
- **`agents/openai.yaml`** — display metadata for Codex.
- **Claude Code plugin manifests** — the repo installs either via `npx skills` or as a Claude Code plugin.

### Notes

The triviality bar is deliberately strict: one file, no logic or control-flow change, no new behaviour, no new dependency. Anything else takes the full flow.
