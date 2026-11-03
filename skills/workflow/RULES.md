# Rules readiness

Shared engineering rules live in this package's `rule-maker` skill, under `rules/`. This file says how the workflow loads them; rule-maker's `rules/READINESS.md` owns the readiness procedure.

## Before planning or writing

1. Resolve this package's `rule-maker` skill (not an upstream specialist). Read its `rules/START.md`, `rules/CORE.md` and `rules/READINESS.md`. Missing library: say so and pause affected work; never invent a substitute or fetch one.
2. Bounded read-only discovery is allowed first, to find the facts.
3. When readiness stops the work, ask only the readiness choice and stop; behavior and design questions come afterwards from the phase skill, which saves them with the task.
4. Set the readiness state exactly as READINESS.md defines it (READY, NEEDS_SETUP, BLOCKED, LIMITED_EXCEPTION, READ_ONLY, SETUP_ONLY), including its missing-rules message. Existing adequate project rules need no rule-maker run or marker; empty, stale or conflicting guidance is not adequate just because AGENTS.md exists.
5. Record the state, its sources and scope in one checkpoint line of the existing task, not a new report; name only rule files you actually opened. Reuse a valid scoped decision after rechecking what it depends on.

Readiness is not permission to implement: the two gates still apply. Conflicting memory or instructions follow rule-maker's POLICY.md; a full rules audit is rule-maker's AUDIT.md, not this check.

## Pick the guidance that applies

After readiness, use rule-maker's VERSIONS.md to tell declared, locked and actual versions apart, and ENGINEERING.md to select modules for the change's real risks (data, lifetime, reliability, testing, security, performance, compatibility). Read operations.md before side-effecting checks. Selecting a module never authorizes installs, upgrades or unrelated cleanup. Application UI follows the shared design.md, which routes to `ui-design`.

## Pass it on

Give reviewers and workers the effective rules, version evidence and any approved exception. Specialists such as `codebase-design` work within them and cannot redesign around them. Recheck affected inputs after a dependency or shared-rule update.
