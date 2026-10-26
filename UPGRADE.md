# Upgrade to 2.5.0

This update adds global rules for test/build output. It does not clean existing artifacts, install another specialist or change application/build scripts. Matt's skills, grilling, approval, task records and local flowchart stay in place.

## 1. Update the skills

Replace the six complete package-owned skill folders with this version, preserving unrelated custom files and project rules. For plugin installation, update the root containing `.claude-plugin/plugin.json`; for standalone installations, update the complete folders under your active skill directory. Avoid duplicate active copies. Do not reinstall Matt's reviewed collection.

## 2. Activate the policy globally — once per user/profile environment

From the extracted `workflow-axa` folder, run these in Git Bash or your terminal (Python 3.10+):

```bash
# Preview only: prints destinations/managed blocks; writes nothing.
python -X utf8 skills/workflow/scripts/global_policy.py

# After reviewing the preview and skills/workflow/ARTIFACTS.md:
python -X utf8 skills/workflow/scripts/global_policy.py --apply

# Confirm files match this package; read-only.
python -X utf8 skills/workflow/scripts/global_policy.py --check
```

No global setup command has been run on your machine by preparing this ZIP. The helper deploys one shared policy to `~/.workflow-axa/ARTIFACTS.md` and merges only a marked section into your existing global Claude/Codex instructions. It keeps all unrelated content, BOM and line endings. Run setup while no other agent is editing these instruction files. It creates no log/backup folders, does not scan `.artifacts` and does not modify any repository. Repeated application is idempotent: it does not append another block.

Defaults are `~/.claude/CLAUDE.md` and `~/.codex/AGENTS.md`; CLAUDE_CONFIG_DIR/CODEX_HOME or explicit `--claude-dir`/`--codex-home` select other profiles. Use absolute paths. A nonempty Codex `AGENTS.override.md` gets the same small block too, because it hides AGENTS.md; no override is created. The preview shows all paths. A manually edited/unowned deployed policy, duplicate markers, linked config or downgrade stops setup for review. No script can prove which instructions a running model actually read.

Do not paste project-specific AGENTS.md/CLAUDE.md into these global locations. This global setup is for all projects in that local user environment, not automatically all teammates, remote/cloud machines or unrelated ChatGPT sessions. Run it in each actual environment. Use `--host claude` or `--host codex` when only one host should change. Skill updates do not silently upgrade global configuration: run the reviewed setup again when ARTIFACTS.md changes.

## 3. Apply the separately supplied project instruction edits

For the project whose AGENTS.md/CLAUDE.md were supplied, merge the delivered replacements into that repository's root, after checking for edits made since upload. They are **project** files, not global files. The updated AGENTS.md defines its protected paths and shared-policy reference. CLAUDE.md still imports `@AGENTS.md` and passes the output boundaries to specialist/subagent work. Their CRLF endings are preserved. CONTEXT.md has no required changes.

No other project's policy needs a copy of those domain-specific rules. Read any existing project protections; ask about conflicts instead of deleting protected files. Nothing in this update modifies the referenced ADR or claims to have read the complete user's repository.

## 4. Verify in fresh agent sessions

Start fresh Claude/Codex sessions. Run `workflow-doctor` and ask each host to identify the active global policy and its own loaded instruction paths. In Claude, inspect the loaded memory/instruction list; in Codex inspect the effective AGENTS chain, including overrides. Keep normal permissions; do not bypass them to force a test.

Use a small existing disposable project and an ordinary request without `/workflow`, such as “run the existing tests and report the result.” Confirm the policy is actually read, output uses the stable parent, no extra documentation scaffold appears, and only owned disposable scratch is eligible for cleanup. Test parallel workers and a required screenshot set separately. Setup/unit tests do not prove these model behaviors.

## Limits

Existing tool scripts may still retain a stamped directory per run. The global policy tells the agent to use supported retention or propose an approved producer fix; it does not silently rewrite scripts or make old files safe to delete. Any cleanup of the accumulated artifacts remains separate work requiring its own reviewed scope.

The helper uses atomic replacements per file and rejects changed inputs, but setup is not one transaction across all target files. After interruption, run `--check` and complete the reviewed merge. It does not create backup trees; the preview is the opportunity to review changes before applying them. See [SETUP.md](skills/workflow/SETUP.md) and [VALIDATION.md](VALIDATION.md).
