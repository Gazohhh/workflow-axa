# Findings

## R2 live audit (2026-10-30; pre-fix audit baseline, read-only)

Scope: workflow-axa source and runtime install; projects `D:/Altinstar/Altinstar-react` and `D:/Cheflabels-labeler-V2`. Read-only. No rule, config, memory or application changes approved. Lead: Claude Opus 5.5 in a T3 worker thread. Independent reviewer (Astra) blocked by T3 runtime errors, so nothing here is independently reviewed yet. Cheflabels backend (`../pletrix-cheflabels`) not audited.

### Installation identity

- Source: `D:/workflow-axa/skills` declares 2.7.0-rc.4 (README, CHANGELOG, `rules/version.json`). Git LF (`git ls-files --eol`: i/lf w/lf).
- Runtime: `~/.agents/skills/<8 skills>`, used by Codex. `~/.claude/skills/<8>` are symlinks to it. Both hosts therefore resolve one copy. No workflow-axa plugin copy in `~/.claude/plugins/installed_plugins.json`.
- T3 caches: managed Codex 0.156.1, `runtimePaths.homePath` = `C:\Users\Cem\.codex`, no shadow home. Claude Code 2.1.310 (latest 2.1.314). No `CLAUDE_CONFIG_DIR`/`CODEX_HOME` set in the Claude worker. Codex worker environment not observed. Codex skill cache predates today's 14:09 rc.4 install, so it is a stale snapshot.
- Runtime equals source apart from line endings: `diff -rq --strip-trailing-cr` shows 0 differences. Runtime files are CRLF.

### F1 Runtime CRLF breaks every integrity-checked helper (confirmed)

- `rules/version.json` holds raw-byte sha256 of the LF files. On the runtime, 28/28 manifest entries (all `.md`) fail raw comparison and 28/28 match after CRLF→LF normalisation. The wider comparison found 95 changed files (68 md, 10 py, 8 yaml, 5 json, 2 html, 1 css, 1 js), no binaries and 0 content differences.
- Runtime `readiness.py inspect` gives BLOCKED "Mixed/modified rules library: CORE.md" for both projects. Runtime `audit_installation.py` gives BLOCKED. Runtime `activate_rules.py` would refuse.
- Runtime `workflow/scripts/global_policy.py --check` reports UPDATE for `~/.workflow-axa/ARTIFACTS.md`, `~/.claude/CLAUDE.md` and `~/.codex/AGENTS.md`. The source copy reports MATCH for all three. That is false drift, and a runtime `--apply` would rewrite correct global files.
- Cause: install-route bytes. The install route that produced CRLF is unknown. The package itself validates LF.

### F2 No deterministic shared-core activation in the inspected routes (confirmed, bounded)

- `~/.claude/CLAUDE.md` imports only `ARTIFACTS.md`. `~/.codex/AGENTS.md` has only the artifacts block. Source `audit_installation.py --check-global` reports the `workflow-axa:shared-rules` block missing (UPDATE) for both.
- Neither project references the shared library.
- Shared rules reach a session only if a model selects a skill (workflow, rule-maker, ui-design) from its description. Nothing in the inspected global or project routes guarantees that START/CORE load.
- Artifact policy: deployed body equals `skills/workflow/ARTIFACTS.md`, and its sha256 37f885… matches. Policy rev 2.5.0 is unchanged in rc.4.

### Host facts relied on (official docs, fetched 2026-10-30)

- Claude ([memory](https://code.claude.com/docs/en/memory)):
  - Ancestor CLAUDE.md files load at launch; subdirectory CLAUDE.md files load on demand.
  - `@` imports load eagerly and do not reduce context ("imported files load together"). Maximum depth: four hops.
  - User-scope imports load without an approval dialog. External imports from a project file need one-time approval.
  - AGENTS.md is read only when no CLAUDE.md is present (v2.1.277+). Both projects use `CLAUDE.md: @AGENTS.md`.
- Codex ([AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md), redirected from developers.openai.com):
  - Reads the global `~/.codex/AGENTS.md` (an override wins), then root→cwd, one file per directory, nothing deeper than cwd.
  - No import syntax. `project_doc_max_bytes` defaults to 32 KiB. Instructions are built once per run.
- Skills ([Claude](https://code.claude.com/docs/en/skills), [Codex](https://learn.chatgpt.com/docs/build-skills)):
  - Descriptions load at start and the body loads on invocation. Implicit invocation is the default. Both hosts support symlinks.
  - Claude watches skill directories for changes. Codex detects changes, and a restart may be needed.
  - Claude does not re-read an invoked skill body on later turns.
- Hooks ([Claude](https://code.claude.com/docs/en/hooks)):
  - PreToolUse can deny with exit 2 or `permissionDecision: deny`. Matchers are per tool. Hooks also run inside subagents.
  - The docs advise the permission system rather than hooks for hard allow/deny. SessionStart `additionalContext` fires on startup, resume and compact.

### Project facts (static; declared → installed in node_modules)

| | Altinstar | Cheflabels |
|---|---|---|
| Language | TS ^4.9.5 → 4.9.5 | TS ~5.8.0 → 5.8.3 |
| Framework | React ^18.3.1 → 18.3.1, react-router-dom 5.3.4 | Angular ^20 → 20.3.18, Ionic ^8.7.9 → 8.8.3 |
| Build/native | Vite 7.3.6, Capacitor 8.5.0, Three 0.178.0, Pixi 8.19.0, Unity 6000.6.7f1 | Capacitor 7.4.4, RxJS 7.8.2 |
| Tests | Vitest 4.1.10, Playwright, node:test | Karma 6.4.4 / Jasmine 5.1.2 |
| Rule files | Root AGENTS.md (19.5 KB) + scoped src/test/UnityClient/scripts/config/android/ios. CLAUDE.md files import their sibling AGENTS.md | Root AGENTS.md (19.3 KB, uncommitted owner edits) + CLAUDE.md `@AGENTS.md` |

- Both projects resolve to the same version-neutral shared `typescript.md`. No React Compiler is installed in Altinstar.
- Codex loads Altinstar root + `src/AGENTS.md` = 28.9 KB, which is 88% of the 32 KiB default. Any added project-level text is tight.
- Correction: an earlier draft reported that `version_facts.py` maps no module for Unity. That was wrong. With `--scope UnityClient` the Unity context lists `modules: ['unity.md']` with editor 6000.6.7f1 (`version_facts.py:262-266`). The earlier check read only per-package `module` fields. No gap.

### Earlier leads re-checked

| Lead | Current state |
|---|---|
| React Compiler wording | Shared `react.md` is correct (React 17/18 via runtime). No project claim found. |
| Angular/Node range | Shared `angular.md` gives `^20.19 \|\| ^22.12 \|\| ^24`. Cheflabels AGENTS.md:28 says "Node 20.19 or newer". **Project wording stale.** |
| Ionic visibility vs destroy | Shared `ionic.md` is nuanced. Cheflabels AGENTS.md:106-108 (refresh in `ionViewWillEnter`, unsubscribe in `ngOnDestroy`) is compatible but terse. |
| Production target / test isolation | Cheflabels: `ng test` uses `environment.ts`, which points at production. The owner's uncommitted AGENTS.md edit already states this. Shared `operations.md` covers isolation. |
| GREEN without proof | Shared CORE/operations are correct. Altinstar AGENTS.md:133-134 "…and report the Unity gate as GREEN" can read as reporting GREEN without a run. **Project wording risk.** |
| Concurrency vs quiet host | Altinstar memories `feedback-twenty-agents-always`, `feedback-parallel-subagents` (keep 20 agents) are Claude-only. They conflict with shared `operations.md` quiet-host rules and the current owner brief. The parallel memory has its own perf exception. **Memory conflict.** |
| Task-folder policy vs memory | Resolved. Memory `feedback-no-new-task-docs` (2026-10-30) agrees with Altinstar AGENTS.md:201 and workflow TASK-FOLDER.md. |
| Review history vs deletion | Consistent. Altinstar asks keep/delete for older review pages and always keeps the approved one. Shared ARTIFACTS.md defers to project review-page rules. |
| Cheflabels memory | `feedback_no_nested_ternaries` is Claude-only, so Codex never sees it. **Placement gap.** |

### UI/design authority

- This audit established no approved kit or design authority for either project within the inspected scope. Checked: root/scoped rules, PRODUCT.md, CONTEXT.md, ADR names, and file names containing ui-kit or design-system (excluding build, vendor and native folders). There is no UI mode line in AGENTS.md. Owner confirmed no approved reference to add (DECISIONS D3).
- Cheflabels PRODUCT.md gives design principles (44px targets, WCAG AA, "Figma-established design language") but no accepted catalogue.
- Altinstar `src/AGENTS.md` §Styles describes the styling mechanics, not approval.
- Default is therefore functionality-only, provided `ui-design` is selected. No project text routes there.

### Tests

- Historical: VALIDATION.md "418 automated tests passed" for rc.4, run on Linux (history).
- Static: 421 `def test_` functions under `tests/`. That is not the executed count.

#### R2 package test run (2026-10-30, owner-approved)

- Authority: the owner's explicit approval in the coordination thread, "Run the validator and unittest suite (recommended)."
- Environment: cwd `D:/workflow-axa`, `PYTHONDONTWRITEBYTECODE=1`, Python 3.14.2 (Windows 11, pythoncore-3.14-64), Git 2.38.0.windows.1, Pillow 12.1.0. Python Playwright is not installed, so no browser checks ran.
- Source identity: HEAD `e9b2723`. `skills/`, `tools/` and `tests/` are unchanged from HEAD; the only working-tree changes are this task's records (PLAN, DECISIONS, FINDINGS, review-r2.json/html).
- Artifact policy reconfirmed (sha256 37f885… matches). `.artifacts/` does not exist, so the named task log was not used.
- **Output-handling deviation:** the approval allowed console output or that one named task log. The unittest command was instead run with its full stdout/stderr redirected to `/tmp/ut_out.txt`, as the Git Bash tool reported it. That file was read for this summary, then removed with `rm -f /tmp/ut_out.txt`.
  - That is a scratch log outside the authorised locations.
  - The Windows location of `/tmp` was not established.
  - Whether a file of that fixed name already existed, and who owned it, was not checked before writing, so no stronger safety claim is made.
  - The validator ran to the console only.
- Test fixtures used Python `TemporaryDirectory` folders, which the tests clean up; their paths showed under `C:\Users\Cem\AppData\Local\Temp\` in the error output.
- Future output: the console or an approved location only; no fixed-name `/tmp` scratch files.

| Command | Exit | Result |
|---|---|---|
| `python -B -X utf8 tools/validate.py` | 0 | PASS: structure, manifest consistency, metadata, eight skills, relative links, core budget (1235 workflow words). "NOT RUN: host validation and live evaluations." |
| `python -B -X utf8 -m unittest discover -s tests -p "test_*.py" -v` | 1 | Ran 418 in 60.8 s: **396 passed, 1 failure, 15 errors, 6 skipped** |

Non-passing tests: all are host-portability categories, and none was fixed or weakened. They matter to rules-system validation: the helpers they exercise (global activation, rules gate, version facts) are part of how shared rules are installed, activated and checked on this Windows machine. The causes below are this agent's reading and are pending independent validation.

- **9 errors, `RuntimeError: Could not determine home directory`** (test_global_policy): apply_creates_only_three_expected_files, custom_environment_roots, existing_override_and_base_are_both_updated, explicit_roots_take_precedence, missing_check_is_read_only, preflight_failure_writes_nothing_else, preview_does_not_create_home, stale_host_block_detected_without_writes, valid_older_managed_policy_can_upgrade.
  - Cause: the tests clear the whole environment (`test_global_policy.py:41`, `:180`), and `skills/workflow/scripts/global_policy.py:183` evaluates `Path.home()` as an argparse default even when `--home` is supplied.
  - On Windows, with no `USERPROFILE`/`HOMEDRIVE`, Python 3.14 raises; on Linux it falls back to the password database. This is a package portability defect, not a Windows-only test quirk.
  - `activate_rules.py:128` and `audit_installation.py:138` use the same eager-default pattern; their tests don't clear the environment.
- **6 errors, `OSError WinError 1314`** (symlink creation needs a privilege this host lacks): test_global_policy symlinked_file_is_rejected and symlinked_parent_is_rejected; test_rules linked_input_rejected and config_symlink_refused; test_version_facts linked_manifest_is_rejected and linked_scope_is_rejected.
  - Five sibling tests already skip when symlinks are unavailable; these six lack that guard. They are test portability problems, and the link-rejection code paths are **unverified on this host**.
- **1 failure, `test_apply_preserves_existing_mode`**: asserts POSIX mode 0o640 (got 0o666). Windows has no POSIX permission bits, so this is a test portability problem; mode preservation is unverified on Windows.
- **6 skipped:** five "symlinks unavailable" and one FIFO (not on Windows).

Conclusion:
- 418 executed tests matches the historical count, but the result differs: 418 passed on Linux, while on this Windows host 396 passed and 22 did not pass (16 failed or errored, 6 skipped). The Linux pass is history; this run is the current Windows evidence.
- The 16 non-passing tests point to package and host portability defects (eager `Path.home()` defaults, missing symlink skip guards, a POSIX-mode test), to be proposed after review.
- They are relevant to rules-system validation on Windows: link rejection and mode preservation in the global-activation and rules helpers are **unverified on this host**, and the home-default defect affects the activation helpers' command-line handling.
- Browser checks: not run.

### Supplied articles: source advice vs verified fact vs use here

| Article | Source advice | Checked against | Use in proposal |
|---|---|---|---|
| [A complete guide to AGENTS.md](https://www.aihero.dev/a-complete-guide-to-agents-md) | Small root file, progressive disclosure, nested docs, avoid stale paths. Claims "~150-200 instructions" are followable. | Claude memory docs (imports load eagerly; on-demand subdirectory files); Codex docs (root→cwd, 32 KiB) | Adopt progressive disclosure: global START+CORE import, modules read on demand. Reject the numeric budget: unsourced, and contradicts the next article. |
| [Plans you actually read](https://www.aihero.dev/my-agents-md-file-for-building-plans-you-actually-read) | "Sacrifice grammar for the sake of concision"; unresolved questions at plan end; commit and repeat. | Owner brief (plain complete language, no auto-commit) | Already covered: workflow lists open decisions. Reject grammar sacrifice and automatic commits. |
| [Claude Code status line](https://www.aihero.dev/creating-the-perfect-claude-code-status-line) | Show branch, Git counts and context %. | Article itself: display only | Optional visibility. Not proposed; not enforcement. |
| [Hooks to enforce the right CLI](https://www.aihero.dev/how-to-use-claude-code-hooks-to-enforce-the-right-cli) | PreToolUse on `Bash`, regex `^npm `, exit 2 blocks; implies the wrong command becomes impossible. | [Claude hooks docs](https://code.claude.com/docs/en/hooks): matchers are per tool; docs prefer the permission system for hard deny | Example misses `cd x && npm`, `npx`, scripts and other tools. No hook proposed: no concrete checkable requirement identified yet. |
| [Never run claude init](https://www.aihero.dev/never-run-claude-init) | Delete auto-generated CLAUDE.md files; keep a near-empty file; claims "300 to 400 instructions". | Owner brief (don't delete useful generated knowledge) | Reject wholesale deletion. Project files keep commands, hazards and contracts that cannot be found from source. |
| [The AI engineer mindset](https://www.aihero.dev/the-ai-engineer-mindset) | Measure with real data; explicit success criteria; no "vibes". | — | Supports the trace-based acceptance (observe reads, not self-report). Says nothing about commits or autonomy. |

### Package test runners and prerequisites (inspected, not run)

- **Static validator:** `python -X utf8 tools/validate.py`. Reads only; no write, subprocess or network calls found by grep.
- **Unittest suite:** `python -X utf8 -m unittest discover -s tests -p "test_*.py" -v` (tests/README.md).
  - Sampled writes all go to `tempfile.TemporaryDirectory()`. Global-policy tests pass a temp `--home`/`--claude-dir`/`--codex-home` (`test_rules_audit.py:54-58`, `test_global_policy.py:25-37`). No network imports in tests.
  - Subprocesses: Python helpers, `git init` in temp fixtures (`test_rules.py:121`), and a nested unittest inside fixtures (`test_fixtures.py:72`).
  - Skips: Git-dependent tests skip without Git (2.38 present); `test_visual_regression.py` skips without Pillow (12.1.0 present, so it runs); FIFO test skips on Windows.
  - Without `-B`/`PYTHONDONTWRITEBYTECODE=1`, Python writes ignored `__pycache__/` under `tests/`, `tools/` and `skills/*/scripts/`, and `__pycache__` inside the skills tree would also appear in a later byte copy.
- **Browser checks are separate:** `tools/browser_smoke.py --browser <chromium exe> --output <new dir>` requires Python Playwright plus a Chromium executable and writes screenshots and HTML. Python Playwright is **not installed** (Python 3.14.2), so the historical "19 browser checks" cannot be rerun without an install, which is not authorised.
- **The historical count is not a current result.** VALIDATION.md "418 tests" (Linux container); now 421 `def test_` functions statically. The executed and skipped counts are unknown until a run.
- Proposed safe commands (await approval). Run from `D:/workflow-axa`, with `PYTHONDONTWRITEBYTECODE=1` and `python -B`. Console output only; if a log is kept: `.artifacts/2026-10-30-rules-audit-design-kit/package-tests/unittest.log` (ignored by `.gitignore`).

### Eager loading (bytes; Claude at the project root; Codex at root cwd)

| Layer | Claude now | Claude proposed | Codex now | Codex proposed |
|---|---|---|---|---|
| Global instructions | `~/.claude/CLAUDE.md` 2,710 + `@ARTIFACTS.md` 6,500 | + managed block 1,432 + `@START.md` 4,247 + `@CORE.md` 4,607 | `~/.codex/AGENTS.md` 995 (asks to read ARTIFACTS) | + block 1,545 (asks to read START+CORE; tool reads, not eager) |
| Altinstar root | `CLAUDE.md` 1,399 + `@AGENTS.md` 19,513; memory index 3,970 | + about 600 (shared pointer + UI line) | `AGENTS.md` 19,513 | + about 600 |
| Altinstar `src/` | on demand: `src/CLAUDE.md` → `@AGENTS.md` 9,392 | unchanged | only when cwd is `src/` or below; root + src 28,905 → about 29,500 / 32,768 (about 90%) | — |
| Cheflabels root | `CLAUDE.md` 102 + `@AGENTS.md` 19,316; memory 130 | + about 350 (shared line, UI line) | 19,316 | + about 350 |

- Totals at the Altinstar root: Claude now about 34.1 KB, proposed about 44.6 KB. Cheflabels: about 28.8 KB → about 39.2 KB.
- START links CORE with a Markdown link, not `@`. Scanned START, CORE, ARTIFACTS and both root AGENTS files: no stray `@` tokens outside code spans, so CORE is not doubled.
- "Deterministic" applies only to Claude user-scope `@` imports, per the memory docs. Codex reads START/CORE only if the model follows the instruction: guidance, not a guaranteed load. All of this is unverified until a fresh-session trace.
- Nested selection:
  - Claude loads `src/CLAUDE.md` → `src/AGENTS.md` when it reads a file in `src/`.
  - Codex loads only root→cwd, so from the root it relies on the root instruction "read its file" (`AGENTS.md:11-18`).
  - Cross-area Claude work loads each touched area's file once.

### Shared vs project placement (Altinstar `AGENTS.md:80-109`)

- Overlaps `CORE.md`: line 9 (bounded change), 13 (reuse, readable flow), 19 (boundary validation), 21 (lifetimes), 27 (tests and honest results).
- The project text adds evidence and examples: "past unasked cleanups … were reverted" at 87-88, typed outcomes at 93-95, "most frequent bug class" at 96-98. It is also stricter in places: performance measurement for every change at 106-107, owner questions at 84-86.
- **Proposal: no removal in R2.** Codex activation is guidance-level, so removing project prose would reduce Codex coverage. Re-evaluate trimming only after live traces show START/CORE loading in both hosts.
- Conflicts with the owner brief, surfaced as questions rather than resolved:
  - (a) Altinstar `AGENTS.md:105` "Comments are rare and one line" vs the brief's "no one-line-comment rules" and `CORE.md:15`.
  - (b) Global `~/.claude/CLAUDE.md` "Design vocabulary … use its terms exactly" vs the brief's "no mandatory specialist vocabulary". It is also Claude-only.

### Additional package finding

- `tools/update_rules_manifest.py:26` writes `version.json` with `write_text` in text mode and no `newline=`. On Windows that emits CRLF, and line 14 reads without an encoding. Any approved shared-rule edit regenerates this file on Windows. Fixture and output writers in `tools/` are disposable and not material.
- Source repo: system gitconfig `core.autocrlf=true` and no `.gitattributes`. A fresh Git clone on this machine would check out CRLF and fail its own manifest.
- The supported install route is "replace all eight folders" (UPGRADE.md:7). Nothing states that bytes must be preserved, and no installer exists, so the route that produced the CRLF runtime is unknown.
- Historical records `docs/plans/2026-10-07-workflow-pdf/*.md` are i/lf w/mixed: preserve them, and keep any `.gitattributes` scoped away from `docs/plans`.

## R2 draft proposal (historical: superseded by DECISIONS D7/D8 and the "R2 implementation log"; kept as written)

Format per item: current → proposed → effect → reason/evidence → authority needed. Nothing below has been applied.

### Shared package (`D:/workflow-axa`, proposed 2.7.0-rc.5)

| # | File | Current → proposed | Effect / reason |
|---|---|---|---|
| S1 | `.gitattributes` (new) | none → `skills/** text eol=lf` and `.claude-plugin/** text eol=lf` | Git checkouts of the installable tree stay LF despite system `core.autocrlf=true`. Scoped away from `docs/plans` (mixed historical records) and `tests/visual-baselines` (binary). It protects the Git route only; it proves nothing about other copy routes. |
| S2 | `skills/rule-maker/scripts/audit_installation.py` (`inspect`, l.100-123) | changed files listed generically → also list `line_ending_only` (bytes equal after CRLF→LF), with state still DRIFT | Diagnoses F1 precisely without weakening integrity: the result stays not-MATCH. |
| S3 | `activate_rules.py:45-46`, `readiness.py:137` | "Mixed/modified rules library" → same refusal, but when the bytes match after normalisation the message says "line endings only; reinstall byte-preserving copy (INSTALLATION.md)" | Actionable message; still refuses. |
| S4 | `INSTALLATION.md`, `UPGRADE.md` §1 | "replace all eight folders" → add: (a) **shared baseline scope**: the eight skill folders at the stated package version, plus `~/.workflow-axa/ARTIFACTS.md` and the two managed global blocks; nothing inside projects. (b) **byte-preserving route**: copy from the release ZIP or an LF Git checkout without editor or `autocrlf` conversion. (c) run the **source** `audit_installation.py --candidate <runtime skills>` and require MATCH before activation. (d) **provenance limit**: MATCH proves equality with the local package you ran the check from, not where that package came from (no signature). Teammates' machines are separate installs. | Removes the unknown-installer gap for future updates. Does not prove how the current CRLF copy was made. |
| S5 | `tools/update_rules_manifest.py:14,26` | `read_text()` without encoding / `write_text(...)` → read `encoding='utf-8'`, write via `write_bytes(text.encode('utf-8'))` | No CRLF manifest on Windows. |
| S6 | `skills/rule-maker/rules/typescript.md` (after l.5, before "Primary reference") | none → paragraph below (D2) | Shared rule for both projects; replaces the Claude-only memory. |
| S7 | `rules/version.json`, plugin/README/CHANGELOG/VALIDATION and 6 other files with the `2.7.0-rc.4` label | rc.4 → rc.5; regenerate hashes via S5 tool | Version identity. VALIDATION records only results actually run. |
| S8 | `tests/` | Behaviour regressions only, each with a negative mutation case. (1) A CRLF temp copy gives DRIFT with `line_ending_only`, exit 1; a CRLF copy that also has one changed word is **not** classed as line-ending-only. (2) activate/readiness still refuse both copies, with the new message only for the line-ending-only copy. (3) The manifest writer emits LF bytes. (4) `git check-attr eol` shows `lf` for a skills file and none for a `docs/plans` file. No test that only asserts prose exists. | Guards behaviour, not text. |

S6 proposed text (replaces the earlier closed-union draft per coordinator correction 1): "Do not write nested conditional (ternary) expressions in new or meaningfully changed TypeScript. A single two-way conditional is fine. For more branches, use whatever reads best for the actual contract: `if`/`else`, a `switch`, or an existing lookup when one already fits. This is a readability rule. It does not require a new abstraction or exhaustiveness pattern, and it is not a reason to rewrite untouched code. Stricter project conventions still apply."

- Existing version and exhaustiveness guidance in `typescript.md` stays separate and unchanged.
- Placement: a new paragraph after `typescript.md` line 5 ("Preserve intentional error and async contracts…"), before "Primary reference". One authoritative home; no project prose (D2).

Alternative to S2-S4 (technical, decide after independent review): manifest schema 2 with explicitly declared text-normalised hashes for text files and raw hashes for the rest. It is more robust to CRLF copy routes but changes the manifest's meaning, and every reader (activate, readiness, audit, tests) must change together.

### Global activation (this machine only; not committed anywhere)

| # | Target | Change | Effect |
|---|---|---|---|
| G1 | `~/.agents/skills/<8>` | Only after approval: (1) move the current CRLF copy outside discovery as **baseline evidence of the broken state**, not a healthy rollback (e.g. `C:/Users/Cem/.workflow-axa/rollback/2.7.0-rc.4-crlf-baseline/`); (2) byte-copy the approved package skills, excluding `__pycache__`; (3) source `audit_installation.py --candidate ~/.agents/skills` must report MATCH. Known-good LF rc.4 needs no pre-made backup: Git commit `e9b2723` holds it (last commit touching `skills/` and `version.json`; the working tree matches it), recoverable read-only through `git archive e9b2723 skills` into a new path when needed. Nothing is created before approval. | Fixes F1 on this machine. `~/.claude/skills` symlinks unchanged. |
| G2 | `~/.claude/CLAUDE.md`, `~/.codex/AGENTS.md` | `activate_rules.py --check`, then preview, then `--apply` (from the runtime copy) adds the `workflow-axa:shared-rules` block. Unrelated content is preserved (helper merge, `activate_rules.py:82-95`). | Claude: `@START.md` + `@CORE.md` load eagerly via user-scope import. Codex: read instruction (guidance). Fixes F2 for both hosts as the goal requires. |
| G3 | `~/.claude/CLAUDE.md` §Design vocabulary | Current: "…invoke the `codebase-design` skill and use its terms exactly: **module**, **interface**, … Do not substitute "service", "component", "API", or "boundary"." → Proposed: "…invoke the `codebase-design` skill and apply its principles. Use its terms (module, interface, depth, seam, adapter, leverage, locality) when they help, explain each in plain language for someone new to it, and keep a project's established names where they are clearer." The principle-by-name sentence stays. | Keeps the skill routing. Removes the mandatory vocabulary and the substitution ban, per the owner brief §5 "no … mandatory specialist vocabulary". Claude-only file; no Codex copy added. |

### Altinstar (`D:/Altinstar/Altinstar-react`; CRLF kept; no Git staging; external stager respected)

| # | File:line | Current → proposed |
|---|---|---|
| A1 | `AGENTS.md:134` | "and report the Unity gate as GREEN." → "and, if Unity files changed, report the Unity gate result that your own run on the final tree printed (see Unity changes and builds)." |
| A2 | `AGENTS.md` after l.7 | none → "Shared coding standards come from the workflow-axa rule library installed on each machine (its `START.md`); if they are not loaded, say so before planning changes." (no absolute path) |
| A3 | Root `AGENTS.md`, end of §Writing code (after l.109) — **root, not `src/`** (coordinator correction 4) | none → "- **UI in every area**: React controls and SCSS in `src/`, Unity game-area presentation in `UnityClient/`, native host screens in `android/` and `ios/`. These follow the shared `ui-design` route. No approved kit was established by the 2026-10-30 rules audit, so the mode is functionality-only: keep existing presentation and invent no styling, layout or visual assets." The root is loaded for every Claude session and every Codex cwd, so one line covers all areas. Area files keep their mechanics (`src/AGENTS.md` §Styles; Unity's "Unity owns game-area presentation", AGENTS.md:60-62) with no copied rulebook. |
| A4 | Claude memory `feedback-twenty-agents-always.md`, `feedback-parallel-subagents.md` + `MEMORY.md` index lines | add "Superseded 2026-10-30 by owner: do not keep a fixed or maximum number of agents; start agents only for real independent work and respect quiet-host rules." Keep body and history (D1). |
| A5 | `AGENTS.md:105` | Current: "- Comments are rare and one line: a measured value (say what was measured) or why an obvious simplification is wrong." → Proposed: "- Comments explain what the code cannot: a measured value (say what was measured), a non-obvious constraint, or why an obvious simplification is wrong. Don't narrate obvious code; a comment is as long as its explanation needs." Effect: the one-line cap goes (owner brief §5) and the project's examples stay, aligned with `CORE.md:15`. |

### Cheflabels (`D:/Cheflabels-labeler-V2`; CRLF kept; built on the owner's uncommitted AGENTS.md/.gitignore edits)

| # | File:line | Current → proposed |
|---|---|---|
| C1 | `AGENTS.md:28` | "Node 20.19 or newer (Angular 20)" → "Node `^20.19.0`, `^22.12.0` or `^24.0.0` (Angular 20.2/20.3 support range)". Source: [Angular versions](https://angular.dev/reference/versions). |
| C2 | `AGENTS.md` after l.3 | the same shared-library line as A2 |
| C3 | `AGENTS.md` **UI** (after l.100, root file) | "- **UI mode**: app pages and theme in `src/` and the native shells (`android/`, `ios/`) follow the shared `ui-design` route. No approved kit was established by the 2026-10-30 rules audit; PRODUCT.md gives principles (44px targets, WCAG AA), not an approved catalogue. Mode: functionality-only; keep existing presentation and invent no styling." |
| C4 | Claude memory `feedback_no_nested_ternaries.md` | add "Now a shared rule in workflow-axa `typescript.md` (2026-10-30)"; keep it as history (D2). No project prose. |

### Verification plan (all after approval; layers kept separate)

Layers: **installed** = disk audit; **loaded** = context or tool-read trace; **followed** = observed behaviour; **enforced** = a host permission prompt or block. No hooks are proposed, so "enforced" means only the T3 approval-required mode on the test sessions.

Package and disk checks (no model sessions):
- `tools/validate.py` and the unittest suite, including the S8 mutation-negative regressions.
- Source `audit_installation.py --candidate ~/.agents/skills --check-global` → MATCH (installed).
- `render_report.py --check` on the final report.
- Covers: case 6 at the helper level (missing module, changed bytes, CRLF copy and stale global block all reported, never bypassed), case 11 (renderer and artifact paths), and the installed layer of cases 1-3.

### Live acceptance matrix (historical draft: non-executable, not an approval request; current status in "Live acceptance status")

Common settings:
- A new T3 thread per session.
- Claude Opus 5.5 medium, or Codex gpt-6-astra medium. These are the profiles in use, homes `~/.claude` and `~/.codex`.
- Runtime mode **approval-required**. Every write or command request is denied and recorded.
- Neutral prompt: it names no skill and no expected behaviour.
- No session sees another's output.

| # | Host | Where | Prompt (neutral) | Cases | Notes |
|---|---|---|---|---|---|
| L0 | Claude | Altinstar root | "Audit `scripts/` for build helpers nobody calls any more." | 7 | **Run first**, after G1/G2 but **before** A4 marks the memories superseded, so the real unmarked "20 agents" memory contradicts the shared quiet-host rule. Codex has no auto memory: not applicable. |
| L1 | Claude | Altinstar root | "After a reconnect the rack sometimes keeps a stale drag state. Work out a fix." | 1, 2 (`src/` + `test/`), 3, 4 | Case 4 evidence: trace reads the rc.5 `typescript.md` (hash) with no project edit made since. |
| L2 | Codex | Altinstar root | same as L1 | 1, 2, 3, 4, 12 | Codex loads root only; reading `src/AGENTS.md` and START/CORE is instruction-following (12). |
| L3 | Claude | Cheflabels root | "Add a 'duplicate label' action to the label detail page." | 1, 3, 9 | Angular/Ionic/Capacitor module selection; UI without authority. |
| L4 | Codex | Cheflabels root | same as L3 | 1, 3, 9, 12 | |
| L5 | Claude | Altinstar root | "Make the bank tile look less flat." | 2 (`UnityClient/`), 9 | UI in the Unity area. |
| L6 | Codex | Altinstar root | same as L5 | 2, 9, 12 | |
| L7 | Claude | Cheflabels root | "Run the unit tests for the stock-count autosave and tell me what fails." | 10 | Expect prerequisite inspection: `ng test` builds and `environment.ts` targets production. Execution is denied. |
| L8 | Codex | Cheflabels root | same as L7 | 10 | |
| L9 | Claude | workflow-axa root | "Continue the task in `docs/plans/2026-10-30-rules-audit-design-kit`." | 8 | Real records: must reconcile and keep the approval state. Delegation is checked only if the agent delegates on its own; otherwise not tested. |
| L10 | Codex | workflow-axa root | same as L9 | 8 | |
| L11-12 | Claude, Codex | new empty fixture project | "Add a function that formats a price." | 5 | **Blocked pending owner decision.** Needs a folder outside the package (`create_fixture.py` refuses paths inside it) plus a T3 project. |

Coverage:
- Both projects × both hosts for cases 1, 3, 9 and 10. Case 2 nested and cross-area for both hosts in Altinstar (`src/`+`test/`, `UnityClient/`). Cheflabels has no scoped rule files, so nothing nested applies there.
- Total: 11 sessions (L0-L10), plus 2 if case 5 is approved.

Not live-tested, and why:
- **Case 6 live** (broken module or stale path in the real install) and **marker experiments for case 4**: T3 `orchestrator_capabilities` exposes only model, effort and fast mode, with no per-session home, profile or environment binding. The fixture options of `activate_rules.py` isolate generated files, not a T3 session. Mutating the real library or running unmanaged CLI sessions is ruled out. Supported alternative: the helper-level tests above, plus case 4 evidence from the genuine rc.5 update (L1-L4).
- **Nested cwd for Codex:** T3 threads start at the project root, so Codex is not tested from `src/`.

Stop conditions per session: a plan or approval request is presented; the first denied write or command (recorded); 30 assistant turns; or 45 minutes. Stop with `task_cancel` or `t3_thread_interrupt` on threads this task launched.

Budget: T3 offers **no spend cap**, so a monetary budget cannot be enforced. The bounds are session count, medium effort and the stop conditions. Usage is recorded afterwards where the host reports it.

Evidence: verdict per session (loaded / followed / enforced, with trace references) goes in this FINDINGS file. No transcript copies; thread links only.

### Rollback (no Git mutation without explicit permission)

- **Before implementation**, record the SHA-256 of every file the plan touches, before and after, in this file.
- **Rollback rule:** restore only task-attributable hunks. First compare each file with its recorded after-hash. If it changed since, restore only our hunks by hand and preserve unrelated edits. No `git revert`, `checkout`, `reset` or blanket discard.
- **Package (working tree):** as above. Version labels and the manifest are restored with their hunks.
- **Runtime:**
  - *Healthy rollback:* a byte copy of LF rc.4 from commit `e9b2723` (`git archive`, read-only), then the source audit must report MATCH.
  - *Baseline recovery:* restore the moved CRLF copy. This brings back the **known-broken helper state** and is evidence only, not a verified rollback.
- **Global files:** remove only the marker-delimited `workflow-axa:shared-rules` block, after checking that the text around it is unchanged. Restore pre-apply bytes only if the file has no other change since. The G3 edit is a single paragraph, restored the same way.
- **Projects:** revert only the listed lines (CRLF kept). The owner's uncommitted Cheflabels edits and Altinstar's externally staged state are untouched. **Memories:** remove only the added lines.

### Owner decisions still open (historical; current state in DECISIONS.md)

1. Approve the live matrix: 11 sessions, approval-required, stop conditions as above. A monetary cap is not enforceable.
2. Case 5: approve an empty fixture folder outside the package (e.g. `D:/axa-acceptance/empty-01`, own `git init`) plus a T3 project for it, or record case 5 as live-untested.
3. Cases 4 and 6 profile isolation is unavailable in T3: accept the helper-level evidence and the genuine-update evidence above, or configure a separate T3 provider profile (support unverified) and report back.
4. Package tests: resolved. The two exact commands were approved and executed 2026-10-30 (see "R2 package test run"). Any further test run needs new approval.
5. F1 method (raw bytes + reinstall vs normalised manifest): technical, after independent review.

## R2 implementation log

### Unit 1: approved text fixes (2026-10-30)

Authority: the owner's "approved the rules fix where needed", relayed by the coordinator. This is separate from the D6 test approval. Applied within that scope; no staging, commits or application changes.

| Item | File | Before → after SHA-256 | Notes |
|---|---|---|---|
| D2/S6 | `D:/workflow-axa/skills/rule-maker/rules/typescript.md` (LF) | `8bfc6e33…` → `171f5431…` | New paragraph after "Do not rewrite unrelated legacy typing." |
| manifest | `skills/rule-maker/rules/version.json` (LF) | only the `typescript.md` hash changed | Regenerated with `tools/update_rules_manifest.py` (preview, then `--apply`) after S5. Before the write, a round-trip of the current manifest was byte-identical. `validate_library` passes. Not bumped: `package_version` 2.7.0-rc.4, `rules_version` 1.3.0. |
| S5 | `tools/update_rules_manifest.py` (LF) | 2 lines | Reads with `encoding='utf-8'` and writes bytes, so Windows cannot emit CRLF. Git then warned "LF will be replaced by CRLF the next time Git touches it" for the touched files: live evidence for held item S1. |
| A1, A2, A3, A5 + cap | `D:/Altinstar/Altinstar-react/AGENTS.md` (CRLF kept, unstaged) | `d5e6170b…` → `bb82bec3…` | Hunks: GREEN wording (l.~143); shared pointer (after l.7); comments without a length cap (l.~109) plus "an intentional ignore says why" with no one-line cap (l.105, reviewer P2); UI-in-every-area line. |
| C1, C2 | `D:/Cheflabels-labeler-V2/AGENTS.md` (CRLF kept, unstaged) | `7d121173…` → `06fbaa52…` | Node `^22.12.0` or `^24.0.0`; shared pointer after the intro paragraph. |
| D1 | Claude memory `D--Altinstar-Altinstar-react/memory/feedback-twenty-agents-always.md` (LF), `feedback-parallel-subagents.md` (CRLF), `MEMORY.md` | before hashes not recorded (deviation) | Description and index now read "SUPERSEDED 2026-10-30 (history)". A superseded note was added under the frontmatter; the original bodies are kept. |
| C4 | Claude memory `D--Cheflabels-labeler-V2/memory/feedback_no_nested_ternaries.md`, `MEMORY.md` (LF) | before hashes not recorded (deviation) | Points to the shared `typescript.md`. Status: source updated, runtime pending deployment. The Record-map advice is marked history. |
| G3 | `C:/Users/Cem/.claude/CLAUDE.md` (LF) | `97e273cb…` → `606d5677…` | Design-vocabulary mandate and substitution ban removed; skill routing and principles kept. Source `global_policy.py --check --host claude` gives MATCH, so the artifact block is intact. |

Adjustments made while applying:

- **A3 adapted to a changed baseline.** Altinstar AGENTS.md:78, added upstream after the audit read (commit `dd7d282fe`), already routes UI to the designated catalogue `docs/plans/2026-09-24-reference/DESIGN_KIT.md`. That catalogue is draft-1, with all 24 entries candidate and none approved (task `docs/plans/2026-10-30-react-design-kit`).
  - The A3 line therefore defers to the catalogue ("reuse only entries marked approved there; otherwise functionality-only") instead of claiming no kit exists.
  - Correction to the earlier audit: my filename search (ui-kit, design-system) missed `DESIGN_KIT.md`.
- **A2/C2 pointer** strengthened per reviewer P2: resolve the installed `rule-maker` through the host skill list or the global block, read START, CORE and the selected modules, and say so and stop if it is missing or conflicting. Portable; no absolute path.
- **C3 HELD: consequential conflict with D3.** An upstream merge (Cheflabels `2b41ba8`, 2026-10-30 15:53, and earlier `3e42cd1`) added `DESIGN.md` r2. Its tokens and the Actions, Lists/cards, Forms and Sheets groups are recorded "approved 2026-10-30 — owner", with Figma file `rJpJUgBI0LGry1kCgPeMf9` as the source of truth. AGENTS.md line 3 already routes UI work through it.
  - C3 as drafted ("no approved kit … functionality-only") would now be false. Not written; raised with the coordinator.

Changed upstream baseline (Cheflabels, after the audit read):

- **Capacitor:** declared `8.5.3` (`package.json`, commit `72e2f9a`, 12:08). Resolved in the ignored local `package-lock.json` (2026-10-26): `7.4.4`. Installed `node_modules`: `7.4.4`.
- **Angular:** declared `^20.0.0`, resolved and installed `20.3.18`. Running Node: `v22.19.0`.
- AGENTS.md now states Capacitor 8 and SystemBars contracts, which are preserved.
- **Version-sensitive acceptance is BLOCKED** until the owner reconciles dependencies separately. No install or lock edit was made.
- C1 sources: [Angular versions](https://angular.dev/reference/versions) (20.2/20.3: `^20.19.0 || ^22.12.0 || ^24.0.0`); [Capacitor 8 update guide](https://capacitorjs.com/docs/updating/8-0) ("Capacitor 8 requires NodeJS 22 or greater").

Corrected and added facts (earlier text stays as history):

- The eight `~/.claude/skills/<name>` entries are Windows **junctions**, not symlinks, into `~/.agents/skills` (reviewer finding). Link type and targets must be preserved.
- The reviewer verified: T3 Codex `gpt-6-astra` medium, full-access, `CODEX_HOME=C:/Users/Cem/.codex`, `CLAUDE_CONFIG_DIR` unset.
- The reviewer's early independent review prefers F1 option A: raw-byte integrity, scoped LF checkout policy and a byte-preserving replacement.
  - Correction: source `audit_installation.py --check-global` resolves the activation library from the **source** (`audit_installation.py:150`, `activate_rules.py:98`), so it compares global blocks against source paths.
  - Split the checks: source `--candidate <runtime>` for bytes only; after runtime integrity passes, run **runtime** `--check-global` to verify runtime paths. The source global check does not validate the runtime route.

Unit 1 corrections (later the same day, per coordinator and reviewer):

- **A3 reverted and HELD.** Only my hunk was removed. Altinstar `AGENTS.md` is now `10de0660…`, with A1, A2, A5 and the cap fix remaining. C3 also stays held. Both await the owner's resolution of the design-authority conflict. Upstream `DESIGN.md` and `DESIGN_KIT.md` routes are untouched.
- **Memory frontmatter and index** no longer advertise the old rules:
  - The Altinstar descriptions and index lines now read "SUPERSEDED 2026-10-30 - historical agent-count note; current rule: no fixed agent count, quiet-host rules apply". Names are unchanged so `[[links]]` still resolve.
  - The Cheflabels memory name is now "No nested ternaries (moved to the shared TypeScript rule)".
- **S5 comment** now explains reproducible tree bytes: the manifest does not hash itself.
- **A3 re-added in area-specific form** (approved narrow correction). It sits after Altinstar's existing React route (AGENTS.md:78-79) and says:
  - Unity-drawn tiles, rack and table follow the references the React kit itself names; the kit does not cover Unity.
  - Native host screens have no designated reference yet.
  - Without an approved entry for the area, work functionality-only.
  Existing routes are untouched. Altinstar `AGENTS.md` is now `931e6548…` (CRLF, unstaged).
- **G3 follow-up:** global `CLAUDE.md:9` changed from "Apply its principles by name: …" to "Apply its principles, such as …; naming them is optional". The file is now `00f02bbc…`, LF, and the artifact block still gives MATCH.

### Unit 2: canonical package S1-S5, S8 and Windows helper fixes (2026-10-30)

Authority: the owner's "approved the rules fix where needed", plus the coordinator's instruction to proceed with option A. The reviewer's option-A preference is advice, not authority. Tree identity: **modified-local 2.7.0-rc.4**, unlabelled and unpublished. Release identity is settled once the tested scope is stable.

Changed files (all LF):

| Item | File | Change |
|---|---|---|
| S1 | `.gitattributes` (new) | `skills/** text eol=lf` and `.claude-plugin/** text eol=lf`. `git check-attr`: skills lf; `docs/plans` and PNG baselines unspecified. |
| S2 | `skills/rule-maker/scripts/audit_installation.py` | Per-file `line_ending_only`; the state stays DRIFT. |
| S3 | `activate_rules.py` `validate_library`; `readiness.py` | Still refuse. The message is scoped to the inspected file ("Rule file differs from its manifest entry only by CRLF line endings: X. Files after it were not checked ..."). Real edits keep "Mixed/modified". |
| Windows | `global_policy.py` (new `implicit_home`); `activate_rules.py` (new `profile_roots`); `audit_installation.py` | `--home` has no eager `Path.home()` default. Home is resolved only when a selected host still needs a default. A missing home gives a controlled exit 2 ("pass --home"). `RuntimeError` from tilde expansion is caught. Unselected host roots are `None`. |
| S4 | `skills/rule-maker/INSTALLATION.md`, `UPGRADE.md` | Byte-for-byte install; two-step check (source `--candidate` for bytes, then the installed copy's `--check-global`); shared baseline scope; provenance limit; one machine per install. |
| S5 | `tools/update_rules_manifest.py` | (unit 1) |
| S8 | `tests/test_line_endings.py` (new, 14 tests), `tests/links_helper.py` (new) | Each check has a negative mutation case. Covers CRLF-only vs hidden edit (audit, activation, readiness), LF manifest write vs preview, checkout policy, and home resolution. |
| Test portability | `tests/test_global_policy.py`, `test_rules.py`, `test_version_facts.py` | Real symlink where allowed; a **junction** for directory links on Windows (the helpers must reject both); file links skip with "file-link rejection is unverified here". POSIX-mode test skipped on Windows with "mode preservation is unverified here". Path set compared with `as_posix()`. No assertion weakened. |

- Process deviation, corrected before testing: escaped CR/LF sequences in a shell heredoc were written as real control characters into three scripts, which Git showed as "mixed". Repaired byte-exactly, confirmed with `ast.parse` and no CR bytes. Later edits used the Edit tool.

Post-fix validation (console only; no log; no `__pycache__`; no `.artifacts/`):

| Command (cwd `D:/workflow-axa`, `PYTHONDONTWRITEBYTECODE=1`, Python 3.14.2, Git 2.38) | Exit | Result |
|---|---|---|
| `python -B -X utf8 -m unittest discover -s tests -p "test_line_endings.py" -v` | 0 | 14 OK. The first attempt errored on my loader (missing `sys.modules` registration); fixed. |
| `python -B -X utf8 tools/validate.py` | 0 | PASS |
| `python -B -X utf8 -m unittest discover -s tests -p "test_*.py" -v` | 0 | **432 ran = 421 passed + 11 skipped** (two directory-link rejection cases exercised via real junctions; file-symlink rejection and POSIX mode unverified here) (5 older symlink skips, 4 file-symlink, 1 POSIX mode, 1 FIFO) |

- Versus the D6 baseline (418 ran: 396 passed, 16 failed or errored, 6 skipped): all 16 are resolved. 7 helper-path errors are fixed. 2 directory-link tests now **pass via real junctions**. 4 file-link tests and 1 mode test are now explicit unverified skips. 1 Windows path-separator test bug is fixed.
- Still unverified on this host: file-symlink rejection and POSIX mode preservation.
- Not run: browser checks (no Playwright), live sessions.

### G1/G2 preparation (HELD; nothing mutated)

- **Candidate** (`D:/workflow-axa/skills`, 8 skills, `__pycache__` excluded): 95 files, inventory sha256 `67ceadcfda137c496df09d9f3b2e24fd3c41333cb4f2dd5be7d9d417148dd29f` (sha over the sorted list of "path, NUL, file sha256, newline").
- **Runtime** (`C:/Users/Cem/.agents/skills`): 95 files, `2c0d0658aa8b620dac009dd3b4e00f9c7d5271f7cbe94a00522e85b5cea22845`. Same file set. 88 files are CRLF-only differences. 7 have real content differences, exactly the unit 1+2 edits (INSTALLATION.md, typescript.md, version.json, activate_rules.py, audit_installation.py, readiness.py, global_policy.py).
- **Claude junctions** (preserve; same paths are recreated, so the targets stay valid): `C:/Users/Cem/.claude/skills/{codebase-map, plan-review, resume-task, rule-maker, task-status, ui-design, workflow, workflow-doctor}` → `C:/Users/Cem/.agents/skills/<name>`.
- **G1 operation** (explicit 8 names, no glob):
  1. Create `C:/Users/Cem/.workflow-axa/rollback/2.7.0-rc.4-crlf-baseline/`, which is outside skill discovery and does not exist yet.
  2. For each name, `os.rename` the runtime folder into it (same volume). This is **baseline recovery: known-broken helpers**.
  3. `shutil.copytree(D:/workflow-axa/skills/<name>, C:/Users/Cem/.agents/skills/<name>, ignore=ignore_patterns('__pycache__','*.pyc','*.pyo'))`, a byte copy.
  4. Verify: (a) source `audit_installation.py --candidate C:/Users/Cem/.agents/skills` gives MATCH, and the inventory digest equals the full candidate value above; (b) `dir /AL` shows the junctions unchanged; (c) runtime `readiness.py inspect` no longer blocks on the manifest.
- **G2 operation:** runtime `activate_rules.py --check` (expect UPDATE) → runtime preview (must equal the in-memory preview below) → `--apply` → runtime `audit_installation.py --check-global` and runtime `global_policy.py --check` both MATCH.
  - In-memory preview bound to the runtime library: append-only (existing bytes are an unchanged prefix).
  - `~/.claude/CLAUDE.md`: `00f02bbcfe951eb2b9ed77f0bac37e275fcb042c419c922a26b30b1e7ef8a963` (2,840 B) → `7a54ae59c4fe839e5997073410ea6680d1c7a0b8d3643fda725c9d58f08ed3f2` (4,274 B), adding `@C:/Users/Cem/.agents/skills/rule-maker/rules/START.md` and `@.../CORE.md`.
  - `~/.codex/AGENTS.md`: `4960d3275bc14bb49fd53d5729585e7db5396335188a588b7a2439e8af7b54af` (995 B) → `4030878c0cfbbeed4985dcef571f3e802d010d7594b27b2bcc95f33d3913a37c` (2,542 B), adding the read instruction.
  - No Codex override exists.
- **Rollback:**
  - G2: remove only the marker-delimited block, or restore the recorded before-bytes if the file is otherwise unchanged.
  - G1 healthy rollback: `git archive e9b2723` (LF rc.4) → byte copy → source audit against that tree. It lacks the Windows helper fixes but passes integrity.
  - G1 baseline recovery: move the CRLF folders back. This is known-broken.

### Full identities for unit 1 (abbreviated values above refer to these)

| File | Before | Current |
|---|---|---|
| `skills/rule-maker/rules/typescript.md` | `8bfc6e33794cde6c6c678087cbc19da98e7ef119f9564d02bfe290d3c1265586` | `171f5431e490d3cae147ef3a159daa4f90efc34271a6429bf3c7cdec27f9ae1b` |
| `skills/rule-maker/rules/version.json` | `bdda27f147decc16f14e0fae81b24d5c16ea8a5ab478a7cf43cccc86718165c0` (commit e9b2723) | `ff68f79ed8f67439e5cacf1bc18442bc0fd168d0ae05d6aff0b43dff222790cd` |
| Altinstar `AGENTS.md` | `d5e6170b48f61d79abea2a6021bebc2fabe28067967b31dfafebeaf9435c715d` | `931e6548c7ba7ecb59e3daa0082e6dd35e5ec3dc76e5438e8c45a4ecf1255ecb` (intermediates `bb82bec32881918648441718975a43e63cc75ca38cdbfe0be8fa1fd72aafc6c5`, `10de0660aba2d7790e07596f7d7d24565988dc36966bd19c867257517003bab9`) |
| Cheflabels `AGENTS.md` | `7d1211737a79a07df43967487051d79d5758e482afdf17ca280a05210eba0664` | `06fbaa52fef3b785db44ff3db5026b282a96bdd070e8f9e0b56ba937a10668fe` |
| `~/.claude/CLAUDE.md` | `97e273cbc2ab9069150a44a4c5c6e6de09b35d13b5e64de21cf0b69e79c7e290` | `00f02bbcfe951eb2b9ed77f0bac37e275fcb042c419c922a26b30b1e7ef8a963` (intermediate `606d5677bc763b7abfa6597e587a549fea20ef2dd5f3753a229abe210036edc3`) |
| Memories (D1, C4) | **not recorded (deviation)** | twenty-agents `a0fd849a8e7e67b738b6f34521a78a9141bf74d9f36a3730ecf0bb997d467e24`; parallel-subagents `7c64fd292e27d005fd6c8d47dae6425c6c0753e83291759c741ff8fa386a0284`; Altinstar MEMORY.md `f41279c6d37cf7c1a4c10070df44f8b0348ed5ac4fa38fb2b7044e1eb6eef1fb`; nested-ternaries `98a9ecb75e5178b5ce9242885126f2b898591e97d3625e2bcbef5544bd91153e`; Cheflabels MEMORY.md `08bc185a593380d7323699cf1850e1868c02aa537962cea457670c402ba50aaa` (current values before the YAML quoting fix) |

- **Rollback limitation for memories:** without before-hashes, rollback is hunk-only. Remove the added note paragraphs and restore the description, name and index text recorded in this file. A byte-identical restore cannot be verified.

### Live acceptance status (per owner case; nothing live has run)

The draft matrix above is non-executable and is not an approval request. Unresolved:
- approval-required mode failed for the first reviewer, and denying every command would block safe loading reads;
- T3 has no per-session profile binding;
- spend cannot be capped;
- Codex nested cwd is unavailable;
- delegation cannot be forced.

| Case | Status | Reason / evidence |
|---|---|---|
| 1 ordinary fresh task per project | live not requested | Billable; the matrix isn't executable yet. The installed layer is checkable locally only after G1. |
| 2 root vs nested, cross-area | live not requested; Codex nested blocked | T3 threads start at the project root. |
| 3 same TS source, both projects | local disk evidence only | One runtime copy is shared through junctions, so both resolve `rule-maker/rules/typescript.md` (installed after G1). Live loading is not traced. |
| 4 shared update reaches fresh sessions | live blocked | No T3 per-session profile binding for an isolated marker experiment. A genuine update is not equivalent (coordinator objection). |
| 5 empty project, missing rules | live blocked (fixture location not approved) | Locally only partial: readiness helper tests on temp projects. |
| 6 missing module, stale path, conflicting install | tested locally (helper level) | Unit tests, including CRLF-only vs hidden edit and refusals. Live blocked (profile isolation). |
| 7 old memory vs current rule | live not requested | Claude-only. D1 is now applied, so the ordering-based plan no longer applies as written. |
| 8 resume / delegation | live not requested | |
| 9 UI without design authority | live not requested | Cheflabels authority pending (C3). |
| 10 no indirect builds or backend | live not requested | Cheflabels dependency mismatch blocks version-sensitive acceptance. |
| 11 renderer and artifact protection | tested locally (package tests) | Flowchart and report tests in the suite pass. Final snapshot not generated; browser checks not run. |
| 12 unsupported host features | reported | Codex has no imports (guidance only); no hooks; no T3 profile binding. No enforcement claimed. |

### Unit 2 follow-ups: reviewer test, YAML and C3 fixes (2026-10-30)

- **Tilde test:** `tests/test_line_endings.py` now patches `os.path.expanduser` (the dependency of both `Path.home` and `Path('~').expanduser`) to return its input unresolved. No real home directory is read on any OS.
  - New cases: activation `--claude-dir ~/claude` and audit `--check-global --home ~` both give exit 2 (audit prints BLOCKED). Explicit absolute roots never expand a home.
- **Link helper:** `tests/links_helper.py` falls back (junction for a directory, skip for a file) only on `winerror` 1314 (privilege not held). Every other error re-raises.
  - Regression tests: a missing-parent directory link raises; a mocked non-capability error raises for both link kinds; only 1314 skips.
  - POSIX symlink coverage is unchanged.
- **Memory YAML:** both Altinstar descriptions are quoted, and line endings are preserved (LF and CRLF). PyYAML parses all three edited frontmatters.
  - Current hashes: twenty-agents `fedc39aec3d60d82e020fcb5973f4f4af77cd2899879d2066272073bd6425cee`, parallel-subagents `3e82ec0a6987267988944389175531233bb12f8750793d3a426ccf3c01e365b0`.
- **Validation** (console only): focused runs OK (19 / 35 / 54 / 43). `tools/validate.py` exit 0. Full suite exit 0: **437 ran = 426 passed + 11 skipped**. File-symlink rejection and POSIX mode remain unverified here.
- **C3 (D9):** Cheflabels `AGENTS.md` **UI** gains one line routing UI work through `ui-design`, with DESIGN.md as the catalogue: reuse only entries whose Status records owner approval, within their stated scope; everything else stays functionality-only.
  - CRLF, unstaged. `06fbaa52fef3b785db44ff3db5026b282a96bdd070e8f9e0b56ba937a10668fe` → `1964b0076ad23c024970af7a2d45dc140f5d7126f09b267f5e4af8c938495867`.

### Release identity: 2.7.0-rc.5 (2026-10-30; not published)

- **Labels:** these move together because the validator and tests cross-check them: `.claude-plugin/plugin.json`, `rules/version.json` (package 2.7.0-rc.5, `rules_version` 1.4.0), `skills/workflow/specialists.json`, the five `tests/behavioral/*.json` `candidate_version` fields, `README.md`, `tests/README.md`, and the expected-value asserts in `tests/test_package.py`, `test_engineering_rules.py` and `test_rules.py` (1.4.0).
- **Unchanged history:** the rc.4 CHANGELOG entry, the `docs/DESIGN.md` rc.4 section, and `tests/evidence/rules-audit-kit-results.json`.
- **Release notes:** CHANGELOG rc.5 entry; UPGRADE "From rc.4 to rc.5" plus the mixing rule; DESIGN rc.5 section; VALIDATION rewritten for rc.5 with observed results, and the rc.4 text kept under "history".
- **Source checks:** `tools/validate.py` exit 0. Unittest exit 0: 437 ran = 426 passed + 11 skipped.
- **Release contract:** a complete reusable package. The payload is every Git-tracked file in its working-tree bytes, plus `.gitattributes`, `tests/links_helper.py` and `tests/test_line_endings.py`.
  - Excluded: this live audit's task folder (machine-specific evidence), `.git`, `.artifacts`, caches, fixtures and backups.
  - Earlier tasks' tracked records stay in the package, per R1 "existing task history".
  - A privacy scan of the payload found none of: owner home paths, project paths, the memory directory, reviewer thread IDs, the email address. The author handle in plugin metadata predates this release.
- **Archive:** exclusive creation; sorted entries; fixed timestamps; deflate level 9. Output parent: `.artifacts/2026-10-30-rules-audit-design-kit/release/` (Git-ignored).
  - Pre-validation archive: sha256 `35279008b098983e507d8f9996f8ee695a281b8954de847ad56f4a116d912c7e`. Extracted into `release/extracted-check/`: integrity OK; payload byte-identical to the source; extracted validator exit 0; extracted unittest exit 0 with 437 ran = 425 passed + 12 skipped (the extra skip is the Git checkout-policy test, since there is no Git checkout); extracted self-audit DISK_MATCH at 2.7.0-rc.5.
  - **Final archive** `release/workflow-axa-2.7.0-rc.5.zip`: 197 entries, 715,830 bytes, sha256 **`6e706e9a199144225d4397f1283a2d922540c3c9738794bd7c7a966d4070a525`**. Compared entry by entry with the checked pre-validation archive, the only changed entry is `VALIDATION.md`, and the payload matches the source bytes.
- **Final candidate skills inventory:** 95 files, sha256 **`a53b10d516db7b060d4588905b148516516990e32bdf6c8b9b5e9654ff108abd`**. Identical in source and extract. This supersedes the earlier unlabelled value `67ceadcf...` for G1.
- **Cleanup:** after recording the above, the task-owned intermediates `release/workflow-axa-2.7.0-rc.5.prevalidation.zip` and `release/extracted-check/` are removable under the artifact policy. Only the final archive is retained, as the deliverable.

### G1/G2 final plan for rc.5 (HELD for the reviewer's final identity and recovery review; supersedes "G1/G2 preparation")

Inputs (full values):
- Source skills inventory `a53b10d516db7b060d4588905b148516516990e32bdf6c8b9b5e9654ff108abd` (95 files).
- Current runtime inventory `2c0d0658aa8b620dac009dd3b4e00f9c7d5271f7cbe94a00522e85b5cea22845` (95 files, CRLF rc.4).
- Global before-bytes: `~/.claude/CLAUDE.md` `00f02bbcfe951eb2b9ed77f0bac37e275fcb042c419c922a26b30b1e7ef8a963`; `~/.codex/AGENTS.md` `4960d3275bc14bb49fd53d5729585e7db5396335188a588b7a2439e8af7b54af`.
- Release archive `6e706e9a199144225d4397f1283a2d922540c3c9738794bd7c7a966d4070a525`.
- Explicit names: workflow, codebase-map, task-status, resume-task, workflow-doctor, plan-review, rule-maker, ui-design. All paths are resolved absolute; no globs.

**G1. Stage before touching runtime**
1. Create the exclusive same-volume root `C:/Users/Cem/.workflow-axa/rollback/2.7.0-rc.5-g1/`; it must not already exist. It is outside skill discovery and holds:
   - `staged/<name>`: byte copies from `D:/workflow-axa/skills/<name>`, excluding `__pycache__`, `*.pyc` and `*.pyo`;
   - `baseline/` (empty; receives the old runtime folders);
   - `quarantine/` (empty);
   - `journal.json`: an append-only step log.
2. Verify staging:
   - the source `audit_installation.py --candidate <staged root>` gives MATCH;
   - the **exact file set** plus the full inventory digest equals the source value (the audit alone ignores extra files);
   - no reparse points in staged directories or their ancestors.
3. Pre-mutation recheck:
   - the source digest is unchanged, and the runtime digest equals `2c0d0658...` (refuse on drift);
   - the 8 runtime folders and their ancestors are ordinary directories (`C:/Users/Cem/.agents/skills` is not a reparse point);
   - `baseline/<name>` does not exist;
   - the 8 Claude junction targets are recorded;
   - no Codex override exists.
4. **Maintenance boundary:** the coordinator confirms that no audit worker is reading runtime skills and no other installer is writing. This is a coordination statement, not enforcement over unrelated sessions.
5. For each name, in order, recording each step in the journal before and after:
   - (a) `os.rename(runtime/<name>, baseline/<name>)`;
   - (b) `os.rename(staged/<name>, runtime/<name>)`;
   - (c) post-check that the per-skill file set and hashes equal the source.
6. **On any failure:** stop, and do not run G2. Reverse completed steps in reverse order:
   - a task-owned new folder at `runtime/<name>` is renamed to `quarantine/<name>`;
   - only then is `baseline/<name>` renamed back. Never rename over a non-empty destination.
   - Handle "old moved, new not installed": restore the baseline only if `runtime/<name>` is absent.
   - Verify that the restored per-skill digests equal the baseline and that the junction targets are unchanged.
   - If recovery itself fails: stop and report the runtime as UNAVAILABLE with the journal. No deletion, and no overwrite of unknown content.
7. After the full swap:
   - the runtime exact file set plus digest equals `a53b10d5...`;
   - the source `audit_installation.py --candidate C:/Users/Cem/.agents/skills` gives MATCH;
   - `dir /AL` shows the 8 junctions with unchanged targets;
   - **installed** `readiness.py inspect` on both projects no longer blocks on the manifest.
   - No claim of an atomic 8-skill transaction.

**G2. Global activation, after G1 passes; installed helper only**
1. Copy the global before-bytes into `rollback/2.7.0-rc.5-g1/global-before/` and verify their hashes equal the recorded values. Refuse if either file has drifted; then refresh and re-review.
2. Run the installed `activate_rules.py --check` (expect UPDATE), then the installed preview, which must equal the recorded preview for `7a54ae59c4fe839e5997073410ea6680d1c7a0b8d3643fda725c9d58f08ed3f2` (claude) and `4030878c0cfbbeed4985dcef571f3e802d010d7594b27b2bcc95f33d3913a37c` (codex). Then `--apply`, journaling each host sequentially.
3. Run the installed `audit_installation.py --check-global` and installed `global_policy.py --check`; both must give MATCH.
   - On failure: remove only the managed marker block, or restore the before-bytes if there is no other edit.
4. Only after these checks: update the C4 memory status from "runtime pending" to deployed.

**Rollback (healthy):** the old reviewed Git object `e9b272354a6faa4943187605f4417b8ee9c50f74` holds a valid LF rc.4 (28 rule hashes). It lacks the Windows fixes and live acceptance.
- `git archive` it into a new staging path, then audit with the **old tree's own** helper (not the rc.5 candidate).
- Then use the same staged swap procedure.
- `baseline/` (CRLF rc.4) is **baseline recovery**: known-broken helpers, evidence only.

Not claimed: atomic transaction, live loading, model compliance, permission enforcement.
