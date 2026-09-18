# Changelog

Notable changes to the `workflow` skill. Versions are git tags; this file says what each one changed and why.

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
