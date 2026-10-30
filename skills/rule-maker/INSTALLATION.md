# Check the actual installed copy

Run from the trusted complete package (Python 3.10+, no installation required):

```bash
python -X utf8 skills/rule-maker/scripts/audit_installation.py
python -X utf8 skills/rule-maker/scripts/audit_installation.py --candidate /path/to/other/workflow-axa
python -X utf8 skills/rule-maker/scripts/audit_installation.py --check-global
```

`--check-global` checks the global blocks against the library of the copy that runs it: run it from the installed copy to verify the installed route (see "Install byte for byte").

The script accepts a package root, its `skills` directory, or its `skills/rule-maker` directory. For split per-skill installations, supply their common skills parent. It compares the eight local skills and their supporting files to the trusted package running the command, validates the library fingerprints, and reports declared versions, missing/changed files and distinct duplicate copies. Only named candidate locations are read. No recursive search of user profiles, deletion, installation, host execution or network access occurs. Linked/junction candidate inputs require manual review; changing a manifest's version alone cannot hide changed content.

`--check-global` reuses the safe activation helper in read-only mode; `--home`, `--claude-dir`, `--codex-home` and `--host` are supported. It checks the managed blocks including a nonempty Codex override. Unrelated global instructions are preserved and not printed. Disk matches are not proof of host loading, followed rules or enforcement; these remain NOT VERIFIED. Exit 0 means named disk/reference checks match; 1 means drift/duplicate/reference warning; 2 means invalid, unsafe or unreadable input. Do not use the result to skip a fresh-session test.

## Install byte for byte

Copy the eight complete skill folders without changing their bytes: extract the release ZIP, or copy from an LF checkout of this package (its `.gitattributes` keeps `skills/` LF even where `core.autocrlf` is true). Do not pass the files through an editor, archive tool or Git setting that rewrites line endings, and do not copy `__pycache__`. The library is checked against raw-byte hashes, so a copy that differs only in CRLF line endings still fails. The helpers name that case `line_ending_only` (and say "only by CRLF line endings"), meaning: reinstall, rather than hunt for edits.

Check in two steps:
1. From the package you are installing, run `audit_installation.py --candidate <installed skills folder>`. It must report MATCH. This compares bytes only.
2. Then run the **installed** copy's `audit_installation.py --check-global` or `activate_rules.py --check`. Global blocks point at the library of whichever copy runs the check, so only the installed copy verifies the installed route.

The shared baseline is the eight skill folders at the package version, `~/.workflow-axa/ARTIFACTS.md` and the two managed global blocks; nothing inside projects. MATCH proves equality with the local package you ran the check from, not where that package came from: there is no signature. Each machine is a separate installation, and updating one does not update another.

## Trace live loading

Resolve the host's actual skill registration and trace its reads in a disposable project, with a normal prompt that names no skill. Check the effective root/nested instructions, rules START/CORE, appropriate framework modules and UI route. Observe missing-rule and no-styling cases as well as a permitted task. Repeat on the real Claude and Codex versions and for relevant subagents. The checker cannot list hidden plugin caches or determine precedence from disk alone. Add explicitly identified candidates instead of guessing.

Use one installation route per host. Do not delete old copies automatically; establish which is active and preserve a rollback copy outside active discovery. Global activation still uses the existing preview/apply helper; running `--check` never repairs it. Existing local references remain valid when installation paths and the managed blocks stay unchanged. The package includes no auto-updater, host hook blocker or new external dependency.

Primary host references: [Claude memory/imports](https://code.claude.com/docs/en/memory), [Codex instructions](https://developers.openai.com/codex/guides/agents-md). Inspect current installed capabilities; no universal claim that Claude never reads AGENTS.md or that Codex can never explicitly open nested rules.
