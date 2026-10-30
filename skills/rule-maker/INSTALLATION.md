# Check the actual installed copy

Run from the trusted complete package (Python 3.10+, no installation required):

```bash
python -X utf8 skills/rule-maker/scripts/audit_installation.py
python -X utf8 skills/rule-maker/scripts/audit_installation.py --candidate /path/to/other/workflow-axa
python -X utf8 skills/rule-maker/scripts/audit_installation.py --check-global
```

The script accepts a package root, its `skills` directory, or its `skills/rule-maker` directory. For split per-skill installations, supply their common skills parent. It compares the eight local skills and their supporting files to the trusted package running the command, validates the library fingerprints, and reports declared versions, missing/changed files and distinct duplicate copies. Only named candidate locations are read. No recursive search of user profiles, deletion, installation, host execution or network access occurs. Linked/junction candidate inputs require manual review; changing a manifest's version alone cannot hide changed content.

`--check-global` reuses the safe activation helper in read-only mode; `--home`, `--claude-dir`, `--codex-home` and `--host` are supported. It checks the managed blocks including a nonempty Codex override. Unrelated global instructions are preserved and not printed. Disk matches are not proof of host loading, followed rules or enforcement; these remain NOT VERIFIED. Exit 0 means named disk/reference checks match; 1 means drift/duplicate/reference warning; 2 means invalid, unsafe or unreadable input. Do not use the result to skip a fresh-session test.

Resolve the host's actual skill registration and trace its reads in a disposable project, with a normal prompt that names no skill. Check the effective root/nested instructions, rules START/CORE, appropriate framework modules and UI route. Observe missing-rule and no-styling cases as well as a permitted task. Repeat on the real Claude and Codex versions and for relevant subagents. The checker cannot list hidden plugin caches or determine precedence from disk alone. Add explicitly identified candidates instead of guessing.

Use one installation route per host. Do not delete old copies automatically; establish which is active and preserve a rollback copy outside active discovery. Global activation still uses the existing preview/apply helper; running `--check` never repairs it. Existing local references remain valid when installation paths and the managed blocks stay unchanged. The package includes no auto-updater, host hook blocker or new external dependency.

Primary host references: [Claude memory/imports](https://code.claude.com/docs/en/memory), [Codex instructions](https://developers.openai.com/codex/guides/agents-md). Inspect current installed capabilities; no universal claim that Claude never reads AGENTS.md or that Codex can never explicitly open nested rules.
