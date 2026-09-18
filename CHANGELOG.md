# Changelog

Notable changes to the `workflow` skill. Versions are git tags; this file says what each one changed and why.

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
