# Optional readiness checker

`readiness.py` writes only to stdout. It does not run repository tests, create task files, install tools, change permissions, or authorise application implementation.

## Inventory first

```bash
python -X utf8 skills/rule-maker/scripts/readiness.py inspect --root /absolute/project --scope src --task current-task --host claude-profile
```

Use repeatable `--scope` arguments for all affected directories. Include additional inspected project references with `--source docs/reference/VERIFICATION.md`. The helper searches familiar root/ancestor instruction and configuration names along those scopes, plus scoped .claude/rules files. Composer manifest/lock/platform markers, Cargo/toolchain files, additional JS lock names and Unity inputs are now included for freshness. It includes the shared manifest/module hashes, root and Git worktree/branch/commit identity where available. It does not enumerate every custom build system, follow imports automatically, inspect every future nested scope or prove the effective host instruction chain. Re-read newly affected areas before editing.

It returns REVIEW_REQUIRED, never READY from mere file presence. Observe actual host/profile/global sources separately; the host argument is an identity label, not live-host verification. Unsupported links/paths, corrupt inputs and incomplete shared modules fail rather than silently truncate. No Git installation is performed if Git is unavailable; report the manual identity-check requirement.

## Assess known facts

A calling tool can feed an assessment through stdin to `assess` using the same root/scope/task/host/source arguments. No persistent JSON file is necessary. The object has:

- `schema_version: 1` and `snapshot`: the exact inspected snapshot, rechecked against current inputs.
- `checks`: identity, trust, shared_rules, project_rules, scope, versions, verification, output_safety, authority, conflicts and loading. Each has a status (`verified`, `missing`, `blocked`) and a nonempty evidence explanation. Design is optional; it may be `not-applicable` with a reason.
- For setup only, `setup_consent`: an actual response reference, `authority_confirmed: true` and exact approved `paths`. It authorises only those setup artifacts, not application changes.
- For an exception, `exception`: actual response reference, authority confirmation, reason, exact `gaps`, permitted `operations`, active state, `expires: task` or `work-unit`, and the matching `snapshot_fingerprint`. Only known project-rule or verification coverage gaps are exception-eligible in this checker; other unknown prerequisites block.

Use `--mode plan|change|test|read-only|setup`. Exit 2 indicates a blocked/missing prerequisite. Exit 0 does not mean an implementation was approved. READY means the **declared** checks/fingerprints are structurally consistent. It cannot establish that the declarations are true, a person really approved them or the agent obeyed them.

This tool is not a host hook. Do not wire its exit code blindly to shell/MCP permissions or treat an agent-writable receipt as a security token. Effective action enforcement needs separately reviewed host permissions/hooks and live tests of their failure modes. The workflow's readiness procedure remains authoritative when semantic judgment is needed.

## Optional static version facts

```bash
python -X utf8 skills/rule-maker/scripts/version_facts.py --root /absolute/project --scope src --scope server/app
```

This standard-library helper reads bounded named files on each scope's ancestor path. It does not crawl the repository, execute Node/PHP/Artisan/Composer/Cargo, read .env, install anything, fetch documentation or write artifacts. No stdout redirection is needed. Readiness and human implementation approval remain separate.

It reports selected JS framework/compiler declarations; numeric npm v1/v2/v3 direct lock entries (including an explicitly represented workspace); Composer PHP/extension constraints, platform emulation, locked Laravel/Illuminate entries; and configured Unity Editor/render-pipeline packages. Repeated scopes are deduplicated; separate app manifests remain separate. Rust source identities are located but TOML/toolchain versions are not guessed.

Limits are explicit: pnpm/yarn/bun locks, npm aliases/links, custom manifest locations, unsupported lock schemas and unresolved workspace relationships require manual inspection or a compatible read-only tool. Multiple lockfiles or a conflicting declared manager are not silently resolved. A Composer lock version does not establish its alias/replacement semantics or that the current install/runtime matches. Constraint solving, actual PHP/Node/Unity/compiler execution, environment variables, containers and deployment are not verified. The lock's content-hash is not recomputed; use the project's approved tooling to validate lock/manifest consistency.

Use forward-slash relative scopes. Linked/junction, escaping, malformed or over-2-MB inputs fail with BLOCKED/exit 2, not a truncated claim. An empty project returns REVIEW_REQUIRED with no inferred stack. Exit 0 means static collection finished, never READY or compatible. Version-input hashes let readers identify what was inspected; they do not authenticate the content.

Angular/Ionic/Capacitor declarations are now selected in static JS facts, including official @capacitor plugin declarations. Relevant angular.json, ionic.config.json and capacitor.config.* bytes are fingerprinted without execution. No runtime-range solver or host compatibility certification is provided. The installation checker and limits are described in [INSTALLATION.md](INSTALLATION.md).
