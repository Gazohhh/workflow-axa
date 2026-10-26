# Validation — 2.5.0

Validated 26 October 2026 against the supplied 2.4.0 archive. This release changes instructions, global activation tooling and tests. It does not delete existing user artifacts or modify a real project/agent installation.

## Observed checks

| Check | Result |
|---|---|
| Package structure, metadata, links and budgets | PASS; six skills; main workflow 1,139 words. |
| Complete automated tooling suite | PASS; 178 tests (143 existing and 35 new); no skips in this Linux environment. |
| New global-setup checks | Preview/check do not write; managed apply is idempotent; existing instructions/CRLF/BOM and file modes survive; nonempty Codex override is handled; custom profiles work; unsafe/modified inputs are rejected. |
| Global-setup boundaries | Synthetic unknown project artifacts remain untouched. There is no project cleanup function. All setup writes in testing target disposable user profiles. |
| Offline Chromium | PASS; 15 existing browser checks, no external requests or page errors. |
| Matt integrations | Catalogue records/source metadata unchanged from 2.4.0 except workflow_version. Existing questioning instructions are byte-identical; output boundaries were added to specialist handoffs. |
| Local flowchart | FLOWCHART-DESIGN.md, CSS, JS and example JSON byte-identical. Renderer code changes only the emitted version. Example HTML regenerated for current metadata. |
| Project instruction edits | Supplied AGENTS.md changes confined to evidence/output rules and the disposable-output qualification. CLAUDE.md keeps @AGENTS.md and its specialist routes, adding delegated-output boundaries. Both retain CRLF. CONTEXT.md is untouched. |
| Live agent cases | 24 cases authored, including 10 artifact-specific cases; all NOT_RUN. Definitions and unit tests are not model behavior observations. |

Evidence: `tests/evidence/tooling-tests.txt`, `browser-smoke.json`, `dependency-preservation.json` and `behavioral-results.json`. Existing dated evidence and visual-reference comparisons are historical, not rerun claims for this version. This release does not claim a new exact-pixel comparison; unchanged visual assets and the browser suite were checked.

Environment: Python 3.13.5, Linux x86_64, Playwright 1.57.0, Chromium 144.0.7559.96. Existing tools only, no downloads. Browser sandbox bypass was explicitly limited to this trusted disposable container; default commands keep sandboxing elsewhere. The feature-flow screenshot was visually inspected.

## Setup guarantees and limits

The global helper replaces only its own marked block, preserves surrounding bytes and writes one shared deployed policy. It refuses malformed/duplicate markers, unowned or modified policy, a newer installed policy, unsafe path indirection and inputs changed before replacement. It has no recursive artifact scan, deletion preview or cleanup engine: its preview concerns global instructions only. Its only temporary-file removal is its own in-progress configuration-write file.

File replacements are atomic individually, not transactional across all targets. Run setup without concurrent instruction edits. A failed/interrupted apply reports partial completion; rerun the read-only check and complete the reviewed merge. Native Windows ACLs/junction behavior and actual installed-host discovery were not executed here. Conservative path checks and Linux filesystem tests are not a substitute for that target-machine verification.

Claude/Codex executables and the user's actual homes are unavailable. Global policy loading, delegation, compliant cleanup, question quality and preservation of real active consumers are NOT VERIFIED on a live model. Fresh sessions and the B15–B24 pilot are required. Instructions are not a hard filesystem permission mechanism.

Direct file navigation was blocked by this environment's browser policy. The identical HTML was tested offline through browser content loading. Opening in the user's desktop browser still requires a local check. No complete accessibility audit or human comprehension study is claimed.

The user supplied project instructions, not the whole repository or their actual global files. Referenced ADRs, test producers, build-store internals and existing 35 GB artifact tree were not inspected or changed here. The provided project edits preserve known protections and do not certify that every possible consumer has been identified. Producer retention and historical cleanup remain separately approved repository work.

## Distribution

The archive excludes caches, temporary profiles, browser-run directories, credentials, fonts and the user's project-specific files. Those AGENTS.md/CLAUDE.md copies are delivered separately; do not publish them as part of the reusable plugin. ZIP integrity and member hashes are verified against the final package. Structural, unit and browser checks are rerun from a fresh extraction before delivery; packaging does not install, tag, push or publish anything.
