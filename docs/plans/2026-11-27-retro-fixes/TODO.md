# TODO

## Overview

| Ticket | What needs to happen | Status | Dependencies |
|---|---|---|---|
| T1 | Agent-sent messages and quoted pastes never approve or narrow an offer | Verified | none |
| T2 | Fewer false refusals: placement, folder paths, PHP signatures, `run:` operations | Verified | T1 |
| T3 | Name the completion baseline in "Before you start" and warn when it is missing | Verified | none |
| T4 | Session start reports missing ~/.workflow-axa files | Verified | none |
| T5 | Release 2.13.0 and install it | Not started | T1-T4 |

## Tickets

### T1 — Agent-sent messages and quoted pastes never approve or narrow an offer
Status: Verified

What needs to happen: the approval hook treats a message that starts with T3's agent marker as not the owner's, and reads narrowing words only outside fenced blocks and `>` quote lines.

What should work:
- An agent-marked "yes" after a presented offer approves nothing (A1).
- An agent-marked "Only the tests, but never the database." after approval does not narrow it (A1).
- A fenced paste with "only … but" after approval does not narrow it; an unfenced "only the tests" still does (A2).

Technical details:
- May change `hooks/phase_gate.py` (`AGENT_SENT` beside `HOST_NOTICE`, `human_words`, `STATE_VERSION` 28→29), `hooks/approval.py` (`ENTRIES_VERSION` 3→4, `QUOTED`, the restrict branch of `decide`), `tests/test_approval_hook.py`.
- Must not change how unmarked owner messages are judged, apart from fenced and quoted text.
- Test seam: the hook's PreToolUse entry with a synthetic transcript, as the existing `owner()`/`presented()` helpers do. Misses: real T3 transcripts; covered by the marker's exact shape from this thread.
- TDD: yes.

Documents: none

How to verify:
- `python -X utf8 -B -m unittest discover -s tests -p "test_approval_hook.py"`: the new tests fail on ee0e979 and pass after the change.

Verification: passed (V2 red, V3 green, V7 whole suite; review S1-S4)

References:
- Supports: R1, R2, R3, A1, A2
- Depends on: none
- Evidence: FINDINGS E1, E2, E11, V2, V3, V7; FINDINGS V3, V7
- Rules: AGENTS.md (hooks/ owns enforcement; never weaken checks)

### T2 — Fewer false refusals: placement, folder paths, PHP signatures, `run:` operations
Status: Verified

What needs to happen: the run-time placement check reads the command without commit messages, the text after `adb shell`, and heredoc bodies that no shell or interpreter reads; it accepts `sh -n` and `2>$null`; it lets through the exact command of an approved `run: <command>` operation. An offer's `folder/` covers the folder itself. `--name:` counts as a CSS custom property only in files that can carry CSS.

What should work:
- With several worktrees: `sh -n deploy/x.sh`, `grep -n 'x$' f 2>$null`, `adb shell sh /data/local/tmp/x.sh`, `git commit -m "see D:/main for sh x.sh"` (with `git commit` approved) and a record.py heredoc whose body says `sh -n x.sh -> $5` are allowed (A3).
- `bash <<'EOF'\nrm "$p"\nEOF` and every existing refusal stay refused (A3).
- An approved offer with `run: sh deploy/jenkins/tests/run.sh` allows that exact command and refuses `sh deploy/jenkins/tests/other.sh` (A4).
- `_covers("a/b/", "a/b")` is true, `_covers("a/b/", "a/bc")` is false (A5).
- A PHP edit adding `{--dry-run : Only show}` with CSS off is allowed; the same in a `.css` file is refused (A6).

Technical details:
- May change `hooks/approval.py` (`RUN_TIME_REDIRECT`, `INDIRECT_WRITE`, new `placed_text` and `run_approved`, `another_worktree`, `styled_lines`/`changes_style_lines`/`touches_styling`), `skills/workflow/scripts/offers.py` (`_covers`), `skills/workflow-specify/SKILL.md` (step 5 names the `run:` operation), `tests/test_approval_hook.py`, `tests/test_offers.py`.
- Must not change any other refusal.
- Test seam: the hook entry in the existing linked-worktree setup, `offers._covers`, and an Edit event with CSS off. Misses: a live PowerShell or adb session.
- TDD: yes.

Documents: `skills/workflow-specify/SKILL.md` step 5

How to verify:
- `python -X utf8 -B -m unittest discover -s tests -p "test_approval_hook.py"` and `-p "test_offers.py"`: new tests fail on ee0e979 and pass after.

Verification: passed (V6 red then green after review repairs F1-F8 and S1, V7 whole suite; review S4 passed)

References:
- Supports: R4, R5, R6, R7, A3, A4, A5, A6
- Depends on: T1 (same file)
- Evidence: FINDINGS E3, E4, E5, E6, E10, E12, E13, V6, V7; FINDINGS V6, V7
- Rules: AGENTS.md

### T3 — Name the completion baseline in "Before you start" and warn when it is missing
Status: Verified

What needs to happen: workflow-execute lists the `completion_check.py baseline` step under "Before you start" for every route, and the lightweight paragraph no longer carries it alone. `open_items.py --task` lists a record problem when Implementation says in progress, implemented or partial and completion.json is missing.

What should work:
- `--task` on a task with `- Implementation: in progress` and no completion.json shows the warning; `not started` and an existing completion.json show none (A7).

Technical details:
- May change `skills/workflow-execute/SKILL.md`, `skills/workflow/scripts/open_items.py`, `tests/test_open_items.py`.
- Test seam: `open_items.py --task` output. TDD: yes.

Documents: `skills/workflow-execute/SKILL.md`

How to verify:
- `python -X utf8 -B -m unittest discover -s tests -p "test_open_items.py"`; `tools/validate.py` for links and word counts.

Verification: passed (V4, V7 whole suite and validate.py)

References:
- Supports: R8, R9, A7
- Depends on: none
- Evidence: FINDINGS E7, E8, V4, V7; FINDINGS V4, V7
- Rules: AGENTS.md (skills/ owns workflow instructions)

### T4 — Session start reports missing ~/.workflow-axa files
Status: Verified

What needs to happen: the SessionStart note names a missing `~/.workflow-axa/ARTIFACTS.md` or settings.json when the global CLAUDE.md names that folder, with the restore command. It writes nothing.

What should work:
- CLAUDE.md naming `~/.workflow-axa/ARTIFACTS.md` and an empty folder: a note naming both files; both present: no note; CLAUDE.md not naming it: no note (A8).

Technical details:
- May change `hooks/duplicate_skills.py`, `tests/test_duplicate_skills_hook.py`.
- Test seam: the hook run with isolated HOME/USERPROFILE/CLAUDE_CONFIG_DIR, as the test file already does. TDD: yes.

Documents: none

How to verify:
- `python -X utf8 -B -m unittest discover -s tests -p "test_duplicate_skills_hook.py"`.

Verification: passed (V5, V7 whole suite)

References:
- Supports: R10, A8
- Depends on: none
- Evidence: FINDINGS E9, V5, V7; FINDINGS V5, V7
- Rules: AGENTS.md

## Whole-task checks
- `python -X utf8 -B tools/validate.py` and `python -X utf8 -B -m unittest discover -s tests -p "test_*.py"` in the worktree, counts compared with the baseline (A9).


### T5 — Release 2.13.0 and install it (revision 2)
Status: Not started

What needs to happen: publish the retro fixes as release 2.13.0 and install it on this machine for Claude and Codex, so new sessions run the new hooks and skills.

What should work:
- origin/main carries a "Release 2.13.0" commit whose version strings all say 2.13.0, and validate.py passes on it.
- D:/workflow-axa (the live plugin checkout) is at that commit; the Claude plugin registration says 2.13.0.
- ~/.agents/skills holds the 22 skills of the 2.13.0 ZIP; `retro` is left alone.
- The live hook allows a read-only PowerShell command with `2>$null` in this multi-worktree repository.

Technical details:
- Release files: .claude-plugin/plugin.json, skills/rule-maker/rules/version.json, skills/codebase-map/scripts/render_report.py (RENDERER_VERSION only), README.md, UPGRADE.md, CHANGELOG.md, docs/DESIGN.md, tests/README.md (a section for the new tests), tests/behavioral/{engineering-rules,rules-audit-kit,rules-readiness,ui-design}.json (candidate_version), VALIDATION.md (by verification_summary.py), this task folder. Rules version stays 1.9.0.
- ZIP: tools/build_release.py writes .artifacts/release/workflow-axa-2.13.0.zip (ignored by Git).
- Install order: push; update D:/workflow-axa with `git pull --ff-only origin main` (the hook refuses this from a session in another worktree, so the owner may need to run it); `claude plugin marketplace update gazohhh` and `claude plugin update workflow-axa@gazohhh`; replace the 22 folders in ~/.agents/skills from the ZIP.
- TDD: no, a release and install has no behaviour of its own; the checks below prove it.

Documents: README.md, UPGRADE.md, CHANGELOG.md, docs/DESIGN.md, tests/README.md, VALIDATION.md

How to verify:
- `python -X utf8 -I tools/validate.py` before and after VALIDATION.md is written.
- `python -X utf8 -I tools/verification_summary.py --run --write VALIDATION.md` (runs the whole suite).
- `git log origin/main -1`; `git -C D:/workflow-axa log -1`; installed_plugins.json version; ~/.agents/skills/rule-maker/rules/version.json; compare_installed against the release commit; `python -X utf8 skills/rule-maker/scripts/audit_installation.py --check-global` from the installed copy; global_policy.py --check; one live PowerShell call with `2>$null`.

Verification: not run

References:
- Supports: revision 2 request
- Depends on: T1, T2, T3, T4
- Evidence: FINDINGS E14, E15, E16 (PLAN "Revision 2")
- Rules: AGENTS.md (releases read versions from plugin.json and version.json; installation and global settings need explicit approval; verification_summary.py --run --write needs the owner's OK)
