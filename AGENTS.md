# Workflow AXA repository rules

Use the installed rule-maker skill's shared START, CORE and READINESS
rules. Before verification, read its operations guidance and the shared
artifact policy. Do not treat edits to this repository's candidate rules
as changes to the instructions governing the current session.

## Scope and ownership

- hooks/ owns Claude Code hook registration and enforcement.
- skills/ owns workflow instructions, helpers and report rendering.
- tests/ owns regression fixtures and tests; tools/ owns validation
  and packaging. Read tests/README.md before choosing verification.
- Reuse the matching records under docs/plans/. Historical approvals
  authorise only their recorded scope.
- Inspect Git status and relevant diffs before edits. Preserve existing
  changes, including UI-lite work. Resolve overlapping writers before
  changing their files.
- Preserve vendored upstream content and licences according to
  VENDORED-SKILLS.md.

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

## Verification and evidence

<!-- workflow-axa:required-read phases=specify,execute,deliver path="tests/README.md" -->

- Read package versions from .claude-plugin/plugin.json; distinguish
  candidate files, installed copies and observed session registrations.
- For fixes, reproduce the failure, run targeted regression checks, then
  the wider applicable suite documented in tests/README.md.
- Keep synthetic test results separate from live-host observations.
  Paid host evaluations require an explicit total usage or spending cap.
- Reuse the task's output parent under the shared artifact policy.
  Preserve active, protected and tool-owned output. Keep private session
  logs outside committed fixtures; use minimal sanitised reproductions.
