# Upgrade to workflow-axa 2.7.0-rc.2

Full package, based on 2.7.0-rc.1. Shared rules: 1.1.0. The same seven local skills and existing Matt collection are retained. This candidate adds engineering guidance, PHP/Laravel/actual-Rust modules and static version inspection. It does not install code-quality tools or enforce all prose through host hooks.

## 1. Install the complete release

Keep a known-good package. Replace all seven complete skill folders together (or update the whole plugin using your established installation method). Do not overlay selected rule files: START, module references and version.json hashes must agree. Preserve your project's unrelated instructions, task history, settings and policies. No new external specialist installation is needed. Keep Matt's current collection and the local flowchart skill; avoid duplicate active workflow copies.

## 2. Confirm the shared location

General rules stay inside `skills/rule-maker/rules/`, not copied into each repository. The global reference helper and global artifact policy/installer are unchanged from rc.1. With an in-place update at the same trusted path, existing references remain valid. Verify them from that final installed location:

```bash
python -X utf8 skills/rule-maker/scripts/activate_rules.py --check
```

If references are missing or the path changed, preview, review and then apply:

```bash
python -X utf8 skills/rule-maker/scripts/activate_rules.py
python -X utf8 skills/rule-maker/scripts/activate_rules.py --apply
```

Use the actual `--home`, `--claude-dir`, `--codex-home` and `--host` where necessary. Keep the separate artifact-policy activation. Receiving the archive does not modify any machine. No automatic updater or network installation is introduced. Native Windows, custom/cloud profiles and live host loading still need local checks. Shared paths with unsafe import syntax require the existing manual setup route.

## 3. Start a fresh session or refresh at a safe task boundary

Rules 1.1.0 changes the shared fingerprint. An old readiness assessment must be rechecked; do not edit its hash to force a pass. Reconcile actual rule coverage and relevant version inputs, while preserving existing task identity, approval and revision history. Reapprove only a material change to the agreement. Existing rule/setup gaps still trigger the rules-readiness question before substantive work.

No plan-folder migration, schema update, renumbering, source cleanup or dependency upgrade is required. Existing project-specific rules remain authoritative constraints; shared defaults cannot silently waive stricter verification or Git protections. A new module does not automatically refactor older code.

## 4. Version facts are optional, read-only assistance

```bash
python -X utf8 skills/rule-maker/scripts/version_facts.py --root /absolute/project --scope src --scope server/app
```

Use the real bounded scopes. Output goes to stdout; do not create another report by default. This tool reads selected static JS/npm, Composer and Unity facts; Rust inputs are identified without guessed TOML resolution. It does not run project code, resolve all dependency formats, prove runtime versions or grant readiness. pnpm/yarn/bun, aliases, custom paths and conflicting inputs require explicit inspection. See [checker limits](skills/rule-maker/CHECKER.md).

## 5. Verify before team rollout

```bash
python -X utf8 tools/validate.py
python -X utf8 -m unittest discover -s tests -p 'test_*.py'
```

Pilot both Claude and Codex using the existing rules-readiness matrix and [engineering scenarios](tests/behavioral/engineering-rules.json). Include a fresh project without rules, plain requests without slash commands, an upgraded Laravel app retaining its old structure, different React versions in a monorepo, a runtime/platform mismatch, a missing rule file and a resumed already-approved task. Inspect actual reads, decisions and final changes; a generated statement that rules loaded is not proof of compliance.

The package's successful static tests do not certify PHP/Laravel application behaviour, device performance, every future framework release or model obedience. [VALIDATION.md](VALIDATION.md) records observed results and limits. Roll back the complete package and matching references if the local pilot fails; never discard task history to roll back rules.
