# Validation — 2.7.0-rc.2

Date: 2026-10-30. Baseline: workflow-axa-2.7.0-rc.1.zip, SHA-256 `154e46c0f8eb1eeffde7f02bdbfd9ec3407d3503245dc52b1cc88b08e6241dda`. Work was performed on a separate package copy. No installed skills, actual global profiles, user projects or application dependencies were modified.

## Observed results

| Check | Result |
|---|---|
| Baseline | Existing package validator and all 264 tooling tests passed before edits. |
| Candidate automated tests | PASS: 321 tests (57 added). These test package structure, rule routing/content contracts, static version facts, snapshot freshness and safe configuration behaviour, not model compliance. |
| Negative controls | Modified/unlisted/duplicate shared-rule modules, mismatched package identity, corrupt manifests, linked/escaping/oversized inputs, conflicting locks, unsupported npm formats and unrepresented ancestor workspaces are rejected or explicitly unresolved. |
| Read-only collection | Controlled package/Composer script sentinels were not executed; no project file or .env content was copied to output. Version collection does not invoke PHP, Node, Artisan, Composer or Cargo. |
| Version cases | npm JSON lock v1/v2/v3; represented workspaces; separate React app versions; missing/ambiguous/alias/linked locks; Composer PHP constraints, platform emulation and Laravel/Illuminate observations; separate PHP apps; Unity configured Editor/render-pipeline; Rust source identification without fabricated TOML parsing. |
| Readiness freshness | Composer, PHP marker, Cargo/toolchain and additional JS lock changes are included in selected input fingerprints. Old assessments require rechecking, not project/task migration. |
| Shared-library integration | Manifest includes every Markdown module exactly once and hashes are checked; rules release 1.1.0 matches package metadata. Seven skills remain registered. Main workflow stays at 1,216 words; shared core is 512 words. |
| Browser | PASS: 19 Chromium 144.0.7559.96 checks, offline, no external requests or page errors; desktop/mobile geometry, navigation, disclosure, history and inert hostile labels checked. |
| Preserved components | 25 selected files are byte-identical, including the complete local codebase-map subtree, workflow entrypoint, questioning policy, specialist adapters, task-record guide, artifact policy/installer and global-reference helper. All 27 Matt catalogue entries and 26 prior task-history files are preserved. |
| Final archive | ZIP integrity, source-to-extraction equality, validator and automated tests are rerun from a fresh extraction before delivery. Browser checks also run from that extraction. |
| Live model/host evaluation | NOT RUN. Neither Claude Code nor Codex was available as a configured authenticated test agent. Existing scenarios and 30 new engineering scenarios remain explicitly NOT_RUN. |
| Enforced action blocking | NOT ADDED / NOT TESTED. No host permission changes, catch-all blocker or automatic updater is installed. |

## Browser environment limits

The first attempt through `/usr/bin/chromium` timed out without completing checks. Using the installed `/usr/lib/chromium/chromium` binary completed all 19 checks. No package UI logic or assertion was weakened to obtain that result. The container required `--no-sandbox` for this trusted local fixture; do not copy that setting into production browsing.

Direct `file://` navigation is blocked by the environment. The identical HTML was loaded using Playwright set_content while offline. The system opener, native Windows/macOS rendering, full accessibility and actual agent invocation were not verified. Desktop screenshot was inspected. The renderer/assets are unchanged; no new pixel-equality claim across environments is made.

## Static facts are not compatibility certification

The new helper is bounded, standard-library-only and read-only. It reports named static facts; it does not solve dependency ranges, verify lock content-hash consistency, resolve all manager formats, inspect the runtime/container/device, authenticate approval or enforce the agent's prose instructions. pnpm/yarn/bun, custom paths, aliases, linked packages and unfamiliar formats require explicit inspection. No API compatibility pass is derived from a manifest or lock entry. A version range, locked dependency, emulated PHP platform and actual runtime remain distinct.

Filesystem checks reject ordinary linked/escaping inputs; this is not a hardened sandbox against an adversary changing the filesystem concurrently. Hashes identify inspected bytes, not trust or future freshness. Existing host/organisation protections remain necessary.

## Engineering rules and limitations

The library adapts primary guidance recorded in rules/SOURCES.md. It does not reproduce entire upstream guides or claim vendor approval. Rules define applicability, useful examples and verification; they are not a universal lint engine. No code-quality tool, dependency upgrade, database migration, automatic legacy cleanup or per-function compliance report is introduced. Framework APIs still require version/configuration-matched sources.

Tests with PHP/Laravel/Rust manifests are synthetic static fixtures, not executed applications or proof against every framework release. New live scenarios cover stale results, partial cleanup, duplicate effects, authorisation, non-tautological tests, old Laravel structure, PHP syntax limits, multiple React versions, runtime mismatches and avoiding mechanical overengineering. Run them in the real team environments before treating this candidate as established behaviour.

Current compact logs live in tests/evidence/tooling-tests.txt, browser-smoke.json and dependency-preservation.json. Specifically versioned older logs and visual reference records remain historical evidence, not new results. No scratch browser images, caches or build environments are included in the ZIP.
