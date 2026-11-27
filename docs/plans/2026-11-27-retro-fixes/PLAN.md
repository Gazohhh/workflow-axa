# Retro fixes 1, 2, 4 and 6 (Hooqd and Xerocast retro)

## Current checkpoint
- Updated / phase: 2026-11-27; closed (delivered, awaiting the owner's decision on commit, merge and install)
- Recipe: bug; plus Security (agent-sent messages must not approve or narrow an offer) — the approval hook misreads some messages and commands, and two setup checks are missing; scope: the task; classification question: not asked (the request names the outcome and that a change is wanted)
- Rules: READY / AGENTS.md, CLAUDE.md, shared START, CORE, READINESS (rule-maker 1.9.0); rules_stamp NONE; docs_check 0 blocking / this task's scope / package 2.12.0 at ee0e979 / no framework module applies (Python hooks and scripts)
- Agreement (gate one): agreed (agreement 1, 2026-11-27, DECISIONS D1)
- Offer: #1 approved (DECISIONS D6)
- Implementation: implemented
- Verification / owner acceptance: passed (FINDINGS V7: 1736 ran, OK, 14 skipped; validate PASS; review S4 passed); owner acceptance pending
- Blockers: none
- Changed files: hooks/approval.py, hooks/phase_gate.py, hooks/duplicate_skills.py, skills/workflow/scripts/offers.py, skills/workflow/scripts/open_items.py, skills/workflow-execute/SKILL.md, skills/workflow-specify/SKILL.md, tests/test_approval_hook.py, tests/test_offers.py, tests/test_open_items.py, tests/test_duplicate_skills_hook.py
- Scope paths: `hooks/approval.py`, `hooks/phase_gate.py`, `hooks/duplicate_skills.py`, `skills/workflow/scripts/offers.py`, `skills/workflow/scripts/open_items.py`, `skills/workflow-execute/SKILL.md`, `tests/`
- Next safe action: none; 2.13.0 released and installed (Outcome, V9-V11). Restart sessions to load the plugin update.

## Working context
- Owner: Cem. The request was relayed by the coordinator agent of the Hooqd and Xerocast launcher thread (T3 thread 90c9636a), at the owner's request. A relay approves nothing; the owner answers here.
- Repository: workflow-axa; worktree C:/Users/Cem/.t3/worktrees/workflow-axa/retro-fixes-945c384ad2fb6e56, branch `retro-fixes`, base ee0e979 (= origin/main), clean at start. D:/workflow-axa is the live plugin checkout and is not edited.
- Source plan: the coordinator's read-only proposal, copied to C:/Users/Cem/AppData/Local/Temp/claude/a1eeb927f0fe8874/b7506a41-b8f7-4d60-bed7-961ca1f9d0fe/scratchpad/workflow-axa-retro-proposal.md. It is a plan, not authority. FINDINGS records what was checked against the code.
- Test output: the tests write only to temporary folders. Logs go to the session scratchpad and are not kept in the repository.

## Goal and acceptance
Apply the four retro fixes the owner picked ("1. Agent messages ≠ owner", "2. Fewer false refusals", "4+6. Baseline + settings warning"). Fixes 3 and 5 of the proposal are excluded. No commit, push, release, version bump or install.

## Baseline before this change
- Commit ee0e979, empty local diff (sha256 of `git diff HEAD` is the empty hash e3b0c442…b855), Windows 11 Pro 10.0.26200, Python 3.14.2, Git Bash.
- `python -X utf8 -B tools/validate.py` in the worktree: PASS (package structure, manifest consistency, minimal metadata, 22 local skills, relative links). NOTE `skills/verify-app/SKILL.md: 2371 words, above the 2200-word default ceiling` (existing).
- `python -X utf8 -B -m unittest discover -s tests -p "test_*.py"` in the worktree: `Ran 1727 tests in 726.716s`, `OK (skipped=14)`.

## Approach and scope
File lists and checks are added by workflow-specify.

## Agreement
Agreement 1 (proposed 2026-11-27).

Requirements:
- R1 (owner pick "1. Agent messages ≠ owner"): a message that starts with T3's marker `[T3 Code: the agent in T3 thread "…" sent this message, not the user.]` is not the owner's. It cannot approve an offer, narrow it, withdraw it, pause it or resume it.
- R2 (same pick): text inside a fenced code block or on a `>` quote line is not read for narrowing words ("only", "but", "except" …). A withdrawal ("revoke", "not approved") is still read from the whole message.
- R3 (same pick): unmarked owner messages are read as today. "Can you change only the tests?" still narrows an approval.
- R4 (owner pick "2. Fewer false refusals"): in a repository with several worktrees, these commands are no longer refused as "a place known only while it runs": `sh -n <script>`, a PowerShell `2>$null`, the command text after `adb shell`, the message of `git commit -m`, and a heredoc body that goes to a program which is not a shell or interpreter (for example `record.py`). A heredoc fed to `bash`, `sh` or `python -` is still read and still refused when it writes to a run-time place. `sh <script>` without `-n` is still refused.
- R5 (same pick): an offer path `folder/` also covers the folder itself (`rm -r folder`).
- R6 (same pick): the CSS check reads `--name:` custom properties only in files that can carry CSS (css, scss, sass, less, styl, html, vue, svelte, astro, mdx, js/ts/jsx/tsx and Blade). A PHP console signature such as `{--dry-run : Only show}` is no longer styling. The same line in a `.css` file still is.
- R7 (same pick): an approved offer can list a project's own test runner as the operation `run: <exact command>`. Only that exact command text passes the run-time placement check, and only while the offer is approved. No new configuration file.
- R8 (owner pick "4+6"): workflow-execute's "Before you start" list names the review baseline step (`completion_check.py baseline`), for every route. It is removed from the lightweight-edit paragraph, where it is today the only mention.
- R9 (same pick): `open_items.py --task` lists a record problem when the checkpoint's Implementation line says in progress, implemented or partial and the task folder has no completion.json.
- R10 (same pick): at session start the hook reports missing `~/.workflow-axa/settings.json` or `~/.workflow-axa/ARTIFACTS.md` when the global CLAUDE.md names that folder. It says what is missing and how to restore it. It only reports and changes nothing.

What each actor sees:
- The owner: an agent's message in the thread can no longer approve or change an offer. Pasted output in a code block no longer pauses an approved offer. Fewer false refusals of read-only commands in repositories with linked worktrees. A warning at session start when the machine files are missing.
- An agent such as the coordinator: its messages carry no approval authority, which is what the owner asked for. A stop it relays does not pause the work; only the owner's own stop does.
- A session executing a task: a reminder in "Before you start" and an `open_items.py` warning before the review check fails with "no baseline".

Stays the same: every approval form for the owner's own messages, every existing refusal the tests cover, and the offer format apart from the new `run:` operation.

Not included: proposal fix 3 (`record.py tick` reasons) and fix 5 (status-lag hint); recreating ARTIFACTS.md on this machine; a CHANGELOG entry, version bump, commit, push, release or install.

Acceptance:
- A1: an agent-marked "yes" after a presented offer approves nothing; an agent-marked "Only the tests, but never the database." after approval does not narrow it.
- A2: a fenced paste containing "only … but" after approval does not narrow it; an unfenced "only the tests" still does.
- A3: the R4 commands pass with several worktrees; a `bash` heredoc that runs `rm "$p"` is still refused; every existing refusal test still passes.
- A4: an offer with `run: sh deploy/jenkins/tests/run.sh` allows that exact command and still refuses `sh deploy/jenkins/tests/other.sh`.
- A5: `_covers("a/b/", "a/b")` is true and `_covers("a/b/", "a/bc")` is false.
- A6: a PHP edit that adds `{--dry-run : Only show}` with CSS off is allowed; the same text in a `.css` file is refused.
- A7: `open_items.py --task` warns for "Implementation: in progress" without completion.json, and not for "not started".
- A8: the session-start note names both missing files when CLAUDE.md names the folder and it is empty; no note when both exist or when CLAUDE.md does not name it.
- A9: each fix's new test fails on the base code and passes after the change; `tools/validate.py` and the whole unittest suite pass with the exact counts reported.

Assumptions the owner can reject:
- Agent-marked messages are ignored completely, so an agent cannot pause or stop the work either. Only the owner's own stop counts.
- The R9 warning uses the current template's states (in progress, implemented, partial) so older tasks that say "Implementation: complete" do not warn.
- The two internal cache versions (`STATE_VERSION`, `ENTRIES_VERSION`) go up so old transcripts are read again with the new rule. This is not a package version bump.
- A `run:` operation lets the owner approve whatever that script does. The offer shows the exact command.

Known limits: an unfenced paste still narrows an offer; `adb shell "a; rm x"` is still split at the quoted `;`; the session-start check runs only at session start.

## Outcome

Delivered 2026-11-27 under offer #1 (agreement 1). Reconciled by the agent that built it (self-performed); every change was reviewed by an independent code-review subagent (S1-S4, last passed).

Asked and agreed: retro fixes 1, 2, 4 and 6 (requirements R1-R10). Built in this worktree only; nothing committed, pushed, released or installed. D:/workflow-axa is unchanged.

Tickets: T1, T2, T3 and T4 verified (TODO.md).

Changed files: hooks/approval.py, hooks/phase_gate.py, hooks/duplicate_skills.py, skills/workflow/scripts/offers.py, skills/workflow/scripts/open_items.py, skills/workflow-execute/SKILL.md, skills/workflow-specify/SKILL.md, tests/test_approval_hook.py, tests/test_offers.py, tests/test_open_items.py, tests/test_duplicate_skills_hook.py; plus this task folder. All 11 are in the offer; no other file changed.

Verdicts:
- R1, A1 verified (V2, V3). R2, R3, A2 verified (V2, V3).
- R4, R5, R6, R7, A3-A6 verified (V6, V7), after review repairs F1-F8 and S1.
- R8, R9, A7 verified (V4, V7). R10, A8 verified (V5, V7). A9 verified (V7: 1736 ran, OK, 14 skipped; baseline 1727, OK, 14 skipped).
- Assumptions shown in agreement 1 held as agreed (D2, D3).

Checks: full unittest suite and tools/validate.py on the final state (V7, diff sha256 67b1422b…). Reviews: Standards and Spec with blast radius, S1 failed, S2 failed, S3 failed, S4 passed; every finding closed.

Documents: workflow-execute and workflow-specify SKILL.md changed as the tickets named. docs_check on the changed files: 0 blocking; 3 warnings in UPGRADE.md:112 and SETUP.md:68 that predate this task. tests/README.md has no section for the new tests (not in the offer).

Limits: no live T3, PowerShell or adb session was run (V7 UNTESTED line). Unfenced pastes still narrow an offer. `adb shell "echo $(rm $p)"` passes as before (E12). The session-start note runs only at session start. A `run:` operation approves whatever that script does.

Machine note: C:/Users/Cem/.workflow-axa/ has settings.json but no ARTIFACTS.md, which the global CLAUDE.md imports. Not recreated (excluded by the offer).

Kept evidence: this task folder and completion.json. Scratch logs in the session scratchpad are disposable.

Next safe action: the owner decides whether to commit this branch, merge it and install it as the live plugin; each needs its own approval.


Published 2026-11-27 under offer #2 (D7): commits 1e7e07a (the fixes and records) and 8e2744b (the hook's offer #2 approval record) on retro-fixes, pushed as a fast-forward to origin/main (ee0e979..8e2744b). global_policy.py --apply wrote C:/Users/Cem/.workflow-axa/ARTIFACTS.md; --check now reports MATCH for all four files (V8). D:/workflow-axa is not updated yet, so live sessions still run the 2.12.0 hooks. This note is written after the push and is not committed.

## Revision 2: release 2.13.0 and install (2026-11-27)

Request (owner, after the publish): "make a new release if you did not already and install the new plugin." No release was made yet: origin/main 8e2744b still says 2.12.0. Recipe: Other (release and install) — build steps from the phases; one ticket (T5); Agreement: not required — one-ticket offer.

Findings for this revision:
- E14: version strings live in .claude-plugin/plugin.json, README.md title, UPGRADE.md, VALIDATION.md, skills/rule-maker/rules/version.json (package_version), skills/codebase-map/scripts/render_report.py (RENDERER_VERSION) and the candidate_version of four tests/behavioral/*.json files; release 2.12.0 (323c7f9) also added CHANGELOG, README, UPGRADE and docs/DESIGN.md text, then a separate "release records" commit.
- E15: installed now: Claude plugin cache 2.12.0 from ee0e979 (installed_plugins.json); the gazohhh marketplace is the directory D:/workflow-axa, whose main checkout is clean at ee0e979, so live hooks run from it. Codex copies in ~/.agents/skills: all 22 skills equal the ee0e979 tree byte for byte (232 files, none differ, missing or extra); one extra folder `retro` (archived, not in the package) stays.
- E16: tools/build_release.py writes dist/ when Git ignores it, else .artifacts/release/; verification_summary.py --run --write runs the suite and rewrites VALIDATION.md's current section.

Version choice (by: agent, D8): 2.13.0, a minor version, because the release adds the `run:` offer operation and a new session-start warning, as 2.12.0 was minor for new review rules; 2.11.1 was a patch for fixes only.


Released and installed 2026-11-27 under offer #3 (D9), ticket T5 verified. Release 2.13.0 is commit 312a56c on origin/main (V9); the ZIP is .artifacts/release/workflow-axa-2.13.0.zip. Codex copies in ~/.agents/skills equal the release (V10). The owner pulled D:/workflow-axa to 312a56c; the Claude plugin is 2.13.0 and the live hook passed both checks (V11). A release-records commit follows with these lines. Not done: tags or a GitHub release; removing the archived ~/.agents/skills/retro. Running sessions keep the old hooks loaded only until their next call reads the files; Claude asks for a restart to apply the plugin update.
