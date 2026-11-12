# Workflow AXA repository rules

Shared standards: the installed workflow-axa rule-maker library (START, CORE and
READINESS). Before verification, read its operations guidance and the shared
artifact policy. Project rules here win where they are stricter. Edits to this
repository's candidate rules do not change the instructions governing the
current session.

## Rules

- hooks/ owns Claude Code hook registration and enforcement.
- skills/ owns workflow instructions, helpers and report rendering.
- tests/ owns regression fixtures and tests; tools/ owns validation
  and packaging.
- Reuse the matching records under docs/plans/. Historical approvals
  authorise only their recorded scope.
- Inspect Git status and relevant diffs before edits. Preserve existing
  changes, including UI-lite work. Resolve overlapping writers before
  changing their files.
- Keep the LICENSE file in each of the nine formerly copied skill folders
  and the credits in VENDORED-SKILLS.md. These skills are our own text now.
- Read package versions from .claude-plugin/plugin.json and the rules
  version from skills/rule-maker/rules/version.json; distinguish candidate
  files, installed copies and observed session registrations.

## Boundaries

- Develop and test hook candidates in isolation. Changes here may affect
  running sessions that load scripts from this directory; establish a
  separate candidate location before modifying hook registrations/scripts.
- Installation, cache replacement, global settings and live-session
  changes require explicit approval.
- Keep approval evidence bound to the actual user decision, task,
  workspace and report. Never weaken checks to obtain a passing test.
- Other project checkouts and their existing edits remain outside this
  repository's write scope unless separately authorised.
- Commits, pushes, merges, rebases, deployment and dependency installation
  require explicit permission.
- Preserve the existing report renderer and follow the installed design
  rules for any visual changes.
- These commands write outside a task's files and need the owner's OK each
  time: `skills/rule-maker/scripts/activate_rules.py --apply` and
  `skills/workflow/scripts/global_policy.py --apply` (merge blocks into the
  user's global ~/.claude/CLAUDE.md and ~/.codex/AGENTS.md; global_policy.py
  also writes ~/.workflow-axa/ARTIFACTS.md),
  `tools/verification_summary.py --run --write` (runs the suite and rewrites
  VALIDATION.md). The first two with `--check` or no mode, and
  verification_summary.py without `--write`, only read.

## Commands and evidence

<!-- workflow-axa:required-read phases=specify,execute,deliver path="tests/README.md" -->

- Validate: `python -X utf8 -I tools/validate.py`. Tests:
  `python -X utf8 -m unittest discover -s tests -p "test_*.py"`.
  Choose targeted checks from tests/README.md first.
- For fixes, reproduce the failure, run targeted regression checks, then
  the wider applicable suite documented in tests/README.md.
- Keep synthetic test results separate from live-host observations.
  Paid host evaluations require an explicit total usage or spending cap.
- Reuse the task's output parent under the shared artifact policy.
  Preserve active, protected and tool-owned output. Keep private session
  logs outside committed fixtures; use minimal sanitised reproductions.

## Index

- [CONTEXT.md](CONTEXT.md): the package's terms and the owner file of each
  repeated rule; tools/validate.py reads it. Read when naming a concept or
  moving a rule.
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md): routing, phase ownership,
  specialists and what enforces the contract. Read when changing a skill's
  responsibility or a hook.
  Covers: skills/workflow*/, hooks/
- [tests/README.md](tests/README.md): test layout, fixtures and which check
  covers what. Read before choosing verification.
  Covers: tests/, tools/
- [docs/EVALUATION.md](docs/EVALUATION.md): what offline tests do not prove
  and how fresh host runs are prepared. Read before a live or paid run.
- [docs/RULE-CONTRACTS.md](docs/RULE-CONTRACTS.md): contracts for the hard
  rules, what checks each rule, labels per skill and hook candidates. Read
  when changing a gate, a hook or a hard rule.
- [VENDORED-SKILLS.md](VENDORED-SKILLS.md): credits and licences of the
  formerly copied skills. Read when touching one of those skills or its
  LICENSE.
  Covers: skills/grilling/, skills/tdd/, skills/code-review/, skills/writing-for-agents/, skills/codebase-design/, skills/domain-modeling/, skills/implement-spec/, skills/retro/, skills/simple-english/
- [README.md](README.md): user-facing overview, entry points, install and
  release commands. Read when a user-visible behavior, command or count changes.
- [UPGRADE.md](UPGRADE.md), [CHANGELOG.md](CHANGELOG.md),
  [VALIDATION.md](VALIDATION.md): release notes, migration and current
  verification; tools/validate.py checks their counts and versions. Read
  when releasing.
- [docs/DESIGN.md](docs/DESIGN.md): design history by release, shipped in
  the runtime ZIP. Read when a past design decision is questioned.
- docs/plans/ and docs/archive/: task records and preserved history, never
  current rules.
