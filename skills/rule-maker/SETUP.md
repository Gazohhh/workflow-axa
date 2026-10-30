# Shared rules setup — one installation, no project rulebook copies

Keep the complete rule-maker folder in a stable trusted installation alongside the other workflow-axa skills. Both hosts reference this same library. Default discovery alone may select a different duplicate; verify the effective skill and rule paths in each fresh environment.

From the package root (Python 3.10+):

```bash
python -X utf8 skills/rule-maker/scripts/activate_rules.py
python -X utf8 skills/rule-maker/scripts/activate_rules.py --apply
python -X utf8 skills/rule-maker/scripts/activate_rules.py --check
```

Preview writes nothing. Apply only after reviewing the exact managed sections. The helper updates global Claude instructions and Codex base plus an existing nonempty global override, preserving unrelated text and CRLF/BOM. It references the installed rules; it does not copy CORE/framework modules into user homes or projects, install hooks, alter permissions, fetch updates or touch application files. Keep the existing artifact-policy activation too; that policy has a separate lifecycle.

Use `--home`, `--claude-dir`, `--codex-home` and `--host` for the real profiles; CLAUDE_CONFIG_DIR and CODEX_HOME are honoured. The source skill must be at its final stable path before activation. Moving/removing it makes references invalid. A future in-place rules update is picked up by reads at task boundaries; a moved plugin-cache installation requires rerunning this helper. A path containing unsafe import syntax or linked config is rejected for manual review rather than guessed.

Claude's managed block imports the entry point/core via its supported syntax. Codex receives explicit file-read instructions, not a pretend Markdown import. Disk `--check` is not evidence of actual loading. Inspect fresh host traces, a root and scoped task, a plain request without slash commands, a resumed task and a delegated worker. Host configurations that omit global instructions, custom/cloud profiles, unsupported imports or truncated context remain NOT VERIFIED until tested. Do not downgrade permissions to force this setup to pass.

New repositories need no setup command to trigger the readiness question: global instructions route the request to the check. If relevant project rules are absent, the agent must ask before substantive planning/edits. Existing adequate rules need no rewrite or setup marker. Only project-specific facts and approved exceptions belong in repository rules. Use the existing task record; no mandatory readiness manifest per repo.

## Update and rollback

The shared library's small `rules/version.json` identifies this release and fingerprints its modules. After an authorised library edit, the maintainer previews/applies `tools/update_rules_manifest.py` and runs package validation before distribution. This is package maintenance, not a project update command. Ordinary sessions may read but not modify it. Update through your reviewed package distribution, not an agent's implicit git pull. Test the replacement, switch at a safe task boundary and retain a known-good package. An interrupted/partial update fails validation; do not proceed under mixed modules. Another machine/container still needs its own installation and activation. Offline use reports the last verified local version; it does not claim the newest remote release.

Rollback is an explicitly reviewed operation: restore the complete previous package and its matching references. Do not remove unrelated global sections or delete project history. No user-machine changes have occurred merely by receiving this ZIP.

## Optional stronger host enforcement

Global prose and the checker are not an enforced sandbox. To enforce actions, separately review host-version-specific permissions/hooks for direct edits, shell wrappers, MCP tools, child processes and worktree changes. Test unknown tools and failing hooks. Do not ship an untested catch-all regex as "no bypass possible". This release deliberately does not auto-install an action blocker; live-host enforcement must be reported as NOT CONFIGURED rather than green.


## Optional read-only checker

Use [CHECKER.md](CHECKER.md) only when running the inventory/assessment helper. It accepts stdin so no new receipt file is required. Normal workflow uses a short existing checkpoint; never confuse a generated receipt with authenticated approval.

## UI-design boundary

The shared START/CORE/design modules now route application UI to the local ui-design skill. Install all eight local skill folders together. Existing global references at stable paths need checking, not duplicate activation or framework-rule copies. Policy content changed, so re-read it at the next task/work-unit boundary; reconcile existing specific design approvals rather than stripping prior styles. The helper remains reference setup only: it does not install a tool-call blocker or a UI framework. Test ordinary prompts and delegated work in the actual host.

For mixed/old installations, use [INSTALLATION.md](INSTALLATION.md) and the read-only audit helper before a fresh-session test. Do not assume this package is active because its ZIP was downloaded. For a full project-rules audit use [AUDIT.md](AUDIT.md); a task-readiness pass is not a full audit. Global blocks remain unchanged in rc.4, so a matching existing block needs no reinstallation.
