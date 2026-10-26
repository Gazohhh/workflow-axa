# Test output without the clutter

Policy revision: 2.5.0. Applies to testing, builds, device/browser checks, profiling and delegated work, including ordinary prompts outside `/workflow`. An artifact is a generated file, not automatically something worth keeping. Project protections and explicit user instructions still apply; resolve conflicting instructions before a risky write or cleanup.

## Before producing files

Read the applicable project rules and relevant tool's output options. Identify the existing task, output owner, active consumers and any protected destinations. Use the tool's supported output/retention settings; do not move its files or rewrite its scripts merely to fit this policy.

For **agent-chosen** output, reuse the task's recorded parent. If absent, use the project's convention; otherwise use `.artifacts/<full-existing-task-folder-name>/` under this worktree. For a small standalone check with no task, reuse `.artifacts/checks/<stable-purpose>/` when an ignored output location is appropriate; do not create PLAN/TODO files just to name test output. Verify the chosen location is ignored/private where required. Do not change Git configuration or `.gitignore` without authority. Do not create directories until they are needed.

Keep the parent stable across sessions, days, phases and retries. No new top-level `builds2`, `final-retry`, date or phase directories, and no loose files in the artifact root. Preserve established tool-owned paths. In a shared output root, worktrees need distinct ownership. Independent runs may use isolated child directories for concurrency; isolation is correct, indefinite accumulation is not. Never overwrite an active run or the only needed before/after evidence.

Before a costly run, name the command, destination, necessary captures and removal/retention condition in the existing checkpoint or chat. Reuse an installed SDK, emulator, browser and environment after checking compatibility. Do not provision or copy one per task. Required isolation may justify a temporary environment; record why and its lifetime. New tools/installations still require their existing approval.

## Keep these categories separate

| Category | Treatment |
|---|---|
| Temporary work: task-owned intermediate builds, extracted copies, probes, scratch captures | Keep only while needed by the active check/comparison or another consumer. Clean eligible output after that unit, not only at task closure. |
| Evidence: selected proof, necessary failure logs/traces, measured results | Keep the smallest set supporting the conclusion, investigation or handoff. Record its reason and path in existing FINDINGS/checkpoint; do not duplicate full logs there. |
| Deliverables, approved visual references/reviews, rollback/recovery data, provenance, active outputs and shared tool installations/caches | Protect. Follow their owner's/project's retention rules, not scratch cleanup. Re-creatable does not mean safe to delete. |

No whole build/APK copy merely to prove a test ran: reference the existing output while needed and record its identity and result. A hash cannot restore its bytes. Do not delete a requested build before delivery/installation acceptance, or a build needed to reproduce a failure. Don't hide accumulation by moving it outside the repo, archiving it or adding ignores.

For routine retries, retain one current working set and the latest necessary successful result **per distinct check/device/configuration**, plus selected unresolved-failure or before/after evidence. This bounds the agent's choices, not an oldest-file deletion algorithm. Pin indispensable comparisons before replacing disposable results. Screenshot sets explicitly requested by the user, visual baselines, required performance samples and compliance/diagnostic evidence are not subject to a one-image limit. Never omit a required measurement or failure to save space. Configure routine screenshots/traces on failure where appropriate and supported; use readiness assertions, not guessed delays.

## Cleanup authority and stopping rules

Adopting this policy authorizes routine cleanup only of the agent's **own, explicitly disposable output from the current authorized work** when all of the following are established: exact path and ownership; saved necessary results; no running or pending consumer; no required reference, baseline, delivery, rollback or recovery purpose; and no stricter project/host restriction. Do not ask again for every file meeting these conditions. Verify candidates immediately before removal, not from an old inventory.

Interrupted or resumed ownership must be reconciled first. A timestamp, filename, Git ignore, an empty search result or absence from FINDINGS is not deletion authority. Older/unknown outputs, tool-owned state and another session's files need a separate approved cleanup or the owner's established retention mechanism. Do not blanket-wipe `.artifacts`, use `git clean`, delete by wildcard, follow a symlink/junction outside the owned scope, or remove a parent containing protected children. A broad cleanup prohibition overrides this default; preserve and ask when uncertain.

A tool that retains every run is a separate producer issue. Use approved supported retention when safe, or propose a narrowly scoped script change with preview, active-run/reference protection and disposable-fixture tests. Do not silently change repository tools, infer fixed age limits or purge their history. The skill cannot enforce retention inside an unmodified tool.

## Finish and hand off

Keep required PLAN/TODO/FINDINGS/DECISIONS and the approved flowchart review. These are not scratch. Reuse an unpresented draft only when allowed by its writer; preserve presented/approved revisions and project review-page rules. No extra artifact manifest, cleanup report, duplicate log, backup tree or new task folder merely to comply with this policy.

Before handing over or finishing, record retained evidence, remaining scratch/consumers and the next cleanup condition in existing records or a short chat line. Update references before approved retirement of evidence. Subagents receive the exact output parent, ownership and retention/protected-path constraints; their outputs return to the same task. Status, doctor and plan-review return findings in chat unless a saved artifact is explicitly requested.
