# workflow-axa 2.7.0-rc.2

**Full candidate update: shared engineering standards and version-aware rules.** Based on 2.7.0-rc.1. The same seven local skills; no new external specialist. Live Claude/Codex behaviour and host action enforcement have not been validated here.

## The missing prerequisite is now explicit

`/workflow` checks applicable shared/project rules before substantive planning, task scaffolding, application edits, output-producing tests/builds and delegated writes—even when nobody has run `/rule-maker`.

| Situation | Required response |
|---|---|
| Existing rules actually cover this scope | Continue; no rule-maker marker or migration needed. |
| Project rules are missing/empty/inadequate | Stop and offer minimal setup, a specific limited exception, read-only inspection or stop. |
| Unreadable indispensable rules, unknown trust/identity/authority or unsafe conflict | Block affected work; a generic "continue" does not waive unknown constraints. |
| User approves setup | Prepare/apply only the exact approved setup scope; no application implementation. |
| User grants a bounded known-gap exception | Keep remaining safeguards and normal task approval; record scope and expiry in the existing checkpoint. |
| Rules/scope/host/worktree change | Recheck affected inputs, not every file in the codebase. |

**Readiness, setup approval, implementation approval, passing tests and enforced permissions are separate claims.** A Markdown rule cannot guarantee obedience; neither can a checksum authenticate human consent. Unknown prerequisites default to a pause, not an assumed pass.

## Shared rules without project copies

General guidance lives in `skills/rule-maker/rules/`: core, React, TypeScript, Vite, Unity, Three.js, PixiJS, PHP, Laravel, actual-Rust and design-review principles. ENGINEERING.md selects data-contracts, lifetimes, reliability, testing, security, performance and compatibility modules only when relevant. VERSIONS.md separates declared, locked and runtime versions; it does not demand upgrades. The framework references apply to the actual installed versions; they never auto-upgrade dependencies. The design module does not prescribe colours/fonts or replace the approved local flowchart style.

Global Claude/Codex instructions reference this one installed library. Ordinary requests and new folders therefore receive the readiness instruction without needing a slash command. Project files contain only local agreements, commands, ownership and exceptions. A rule update applies to future reads; no automatic bulk changes to application code, old task records or project rulebooks.

See [upgrade instructions](UPGRADE.md) for the preview-first reference helper. The helper installs no hooks, permissions changes or updater. Stable paths and actual host/profile loading must be verified. Other machines and containers need their own installation; no local change silently updates them.

## What this update adds

General rules remain centrally maintained in the skill, not copied into every repository. Required safety/correctness rules are distinguished from design defaults; no rigid zero-nesting, function-length or comment-count mandate. Source/API docs explain the end-state while task records retain the history.

The optional read-only `skills/rule-maker/scripts/version_facts.py --root /absolute/project --scope src --scope server/app` reports static declarations/locks without executing project code or writing artifacts. PHP platform emulation is not a runtime version; npm/pnpm/yarn/Composer formats are not interchangeable. Unsupported resolution remains explicit. The helper is not a solver, compatibility certification or readiness approval.

This is a complete replacement package, not an rc.1 overlay. PHP/Laravel modules are now included. Rust advice runs only for actual Rust work; useful ownership/testing principles remain language-neutral in the shared topics. Existing code is not rewritten automatically.

## Commands

```text
/workflow-axa:workflow <goal>
/workflow-axa:rule-maker audit
/workflow-axa:rule-maker setup
/workflow-axa:rule-maker update
/workflow-axa:task-status <task>
/workflow-axa:resume-task <task>
/workflow-axa:workflow-doctor
/workflow-axa:plan-review <task>
/workflow-axa:codebase-map explain <feature>
/workflow-axa:codebase-map current|proposed|compare <scope>
```

Use the host's actually registered names. Standalone Claude uses `/workflow` and `/rule-maker`; Codex uses `$workflow` and `$rule-maker`. Do not keep duplicate active copies.

The workflow remains: **check rules → find/reuse task → inspect code → grill missing decisions → PLAN/TODO and local flowchart → user approval → implement → verify**. `rule-maker` is a setup/maintenance procedure, not a mandatory repeated interview on every task. Read-only explanations/status need no artificial setup project. Setup bootstrap must not recurse into itself.

## Preserved behaviour

All Matt catalogue entries and existing specialist routes remain, including grilling, research, debugging, TDD, domain modelling and code review. `codebase-design` receives actual project constraints; its suggestions cannot override approved ownership or silently create new architecture.

Local flowchart guide, renderer, CSS/JS, examples and historic reviews remain unchanged. The existing artifact policy and installer remain independent and unchanged. Revision/history support remains forward-only; no folder renaming or schema migration. Existing valid approvals are reused after reconciliation.

## Validation and limitations

Run from the package root:

```bash
python -X utf8 tools/validate.py
python -X utf8 -m unittest discover -s tests -p 'test_*.py'
```

[Validation results](VALIDATION.md) distinguish observed mechanical tests from authored live-host scenarios. [Rules scenario matrix](tests/behavioral/RULES-READINESS.md) and [engineering cases](tests/behavioral/engineering-rules.json) covers missing/partial/legacy/conflicting inputs, bootstrap, exceptions, scope changes, recovery, trust and unsupported cases. No enumeration claims every possible future behaviour is solved.

The read-only `skills/rule-maker/scripts/readiness.py` inventories selected inputs and validates declared coverage/freshness. It never claims file presence proves adequacy. It is not a sandbox, approval authenticator, automatic code-quality proof or host tool-call firewall. Unsupported/malformed states block affected changes under the protocol. Project scripts that generate artifacts or enforce tests keep their existing requirements.

Before team rollout, pilot this candidate in your actual Claude/Codex environments using ordinary requests, missing rules, unchanged resumption and delegated work. Revert to the known-good package if the pilot fails; no files in your computer were changed by generating this archive.

[Setup detail](skills/rule-maker/SETUP.md) · [Existing testing guide](tests/README.md) · [Changelog](CHANGELOG.md) · [Local flowchart example](skills/codebase-map/examples/review.html)
