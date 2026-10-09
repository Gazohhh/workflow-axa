# Validation — 2.0.0

Date: 2026-10-09. Scope: package structure, source review, deterministic local tooling
and archive checks. This is not a certification of model obedience or live host integration.
Version 2.0.0 is the version requested by the user; no Git tag or publication was created.

## Observed local checks

| Check | Result | Evidence and limit |
|---|---|---|
| Package structure | PASS | `python -X utf8 tools/validate.py`, exit 0: matching version/changelog/catalogue, one entrypoint, required files, local reference closure and core budget. |
| Full unit suite | PASS | `python -X utf8 -m unittest discover -s tests -p "test_*.py" -v`: 39 tests passed, exit 0. |
| Existing fixture/tooling coverage | PASS | 18 retained tests: disposable Git isolation, all seven fixture variants, clean baseline, unrelated baseline failure, interrupted work, mixed staging, and package validation. |
| New specialist checker coverage | PASS | 21 tests: complete synthetic collection, selected routes, missing/duplicate entries, manual/model policy mismatch, supporting files, content-baseline changes, path relocation, symlinked skill directories, malformed input, no writes/script execution, and truthful runtime status. |
| Core size | 1,127 words | Under the retained 1,200-word maintenance budget. Not a token-cost or reliability benchmark. |
| Specialist structure | PASS, inspection | One workflow entrypoint, 11 explicit model-invocable routes, a 27-name installation catalogue and separate setup/reference files. No vendored upstream skills or fictional native dependency declarations. |
| Active-instruction consistency | PASS, self-review | Removed obsolete optional-interview/no-runtime-dependency claims; aligned questions, records, audit, README and behavioral cases. No independent reviewer available. |
| Historical records | PASS | Original four 2026-10-07 task documents remain byte-for-byte unchanged. |

Environment: Python 3.13.5, Linux, Git 2.47.3. The fixture suite makes synthetic local
baseline commits only inside fresh temporary test repositories, with no remotes. No
application repository, global installation, account settings or remote was modified.

The checker uses synthetic skill files in unit tests. Its collection test does **not**
mean Matt's actual collection was installed or invoked. Its exit 0 means requested disk
checks passed, never host readiness, source authenticity or behavioral correctness.

## Source verification

Primary web-readable upstream instructions and current official host documentation were
reviewed, as linked in docs/DESIGN.md and skills/workflow/SETUP.md. The upstream plugin
manifest reported 1.3.1 and 27 entries. Eleven routed entrypoints plus relevant wrappers,
setup and selected manual workflows were inspected. This was not a new execution audit
of the complete collection. Direct clone/download was unavailable, so no immutable
upstream commit or byte hash is asserted. Team setup must inspect its actual installation
and approve a local content baseline rather than treating a version label as proof.

## Archive

Package only source files beneath one `workflow-axa/` root. Exclude `.git`, bytecode,
caches, generated fixtures, host inventories and evaluation outputs. Check CRC integrity,
source/member equality and rerun the package validator/full tests from a fresh extraction.
PASS: fresh extraction passed the package validator and all 39 tests again. The result
and its coverage limits are recorded in the specialist-integration task findings.

## Not run / not claimed

Claude Code and Codex executables are unavailable in this environment. Native plugin
validation, actual specialist discovery/invocation, live model comparisons, real
cross-account hard-stop recovery, and the team's Windows installation have not been run.
The 22 main behavioral scenarios are test protocols, not passed evaluations. A usable
team installation, compatible host permissions and a runtime pilot remain necessary.
No PDF deliverable was requested; the existing PDF procedure is retained without claiming
new rendering tests.

Start with README.md and skills/workflow/SETUP.md. Disk checks and source review are
useful gates, but they do not replace the runtime tests in tests/SCENARIOS.md.
