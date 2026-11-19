# Tickets

## Overview

| Ticket | What needs to happen | Status | Dependencies |
|---|---|---|---|
| T1 | Write the `verify-app` skill with its guide and browser-guard template | Verified | none |
| T2 | Write the `reproduce-bug` skill (the bug job) | Verified | none |
| T3 | Register both skills in the package and pass its checks | Verified | T1, T2 |
| T4 | Make the labeler's verify skill and pass the setup and guard checks | Verified | T3 |
| T5 | First test: check the filter-dot fix 502db1f | Verified | T4, T8 |
| T6 | Eval: three known fixed bugs | Verified | T5 |
| T7 | Prove the guide: add a second labeler screen by following it | Verified | T4 |
| T8 | Step-by-step driving through the guard (explore route) | Verified | T3 |

## Tickets

### T1 — Write the `verify-app` skill with its guide and browser-guard template
Status: Verified

What needs to happen: Layer 1's maker. `verify-app` studies an app repository, writes that app's verify skill and feature map, adds or updates map sections later, and proves the result with the 9-step setup check. Written as the package's own text from pstack's `create-verification-skill` and `maintain-verification-skill` (E4, E5).

What should work:
- SKILL.md says, for someone who has never seen the app:
  - how to study the repo (surface, run, drive, observe, isolate);
  - what the generated `.claude/skills/verify-<app>/` holds: Launch, Doctor, Drive, Evidence, Cleanup, Helpers, Settings (allowed backend, blocked production hosts, login source), and `features/`;
  - the 9-step setup check, and that the generated skill counts as a draft until the check has run once;
  - the maintain pass. It changes only the verify skill's own folder and reports product bugs instead of editing around them. It ends in one of three outcomes: clean, changed (shown to the owner, never a pull request) or blocked.
- GUIDE.md part 1: adding or updating a screen in an app's map (section contents, asking `verify-app`, the setup check for one section, keeping it current).
- GUIDE.md part 2: adding a new job (input, rules, outcome words, evidence; uses only layer 1; keeps the safety rules; registration and tests in this package). It lists the possible later jobs as examples, marked not built.
- A browser-guard template that the app's verify skill fills with its own settings:
  - it refuses to start when the backend is one of the listed production hosts or is not set;
  - it lets the browser reach only the allowed backend and the dev server, and blocks and logs every other request;
  - it reads logins only from an ignored local file.
- A feature-map section template with the four sections Sub-features, How to get to it, Driving it, Gotchas, plus the preconditions and evidence it must name.
- No word in layer 1 about bugs or any other job. No source, company or client name.

Technical details:
- Files: `skills/verify-app/SKILL.md`, `GUIDE.md`, `FEATURE-MAP.md` (template), `guard/` (Playwright guard template: a fixture and a config reading a settings file), `LICENSE` (pstack's MIT text), `agents/openai.yaml` (implicit invocation allowed, S3). Must not change other skills.
- Test seam: a new `tests/test_verify_skills.py` that reads the skill files: required sections and phrases, guard template present, no job words in SKILL.md, no source or company names (the owned-skills pattern list), links stay inside the folder. It misses whether an agent follows the text; T4 and T7 cover that live.
- TDD: yes for the text-contract tests (red before the skill text). The guard template is proven live in T4, because the package has no Node test runner.

Documents: none outside the skill folder.

How to verify:
- `python -X utf8 -m unittest tests.test_verify_skills -v` in D:\workflow-axa: the T1 cases pass.

Verification: passed (V1)

References:
- Supports: R1, R2, R4, R5, A1
- Depends on: none
- Rules: D:\workflow-axa\AGENTS.md (skills/ owns skills; no source names in skills); shared CORE (new code carries no comments).
- Evidence: FINDINGS V1, Review S1–S4; FINDINGS V1/V2, Review S1-S4

### T2 — Write the `reproduce-bug` skill (the bug job)
Status: Verified

What needs to happen: Layer 2's first job, written as the package's own text from benny's repro rules, `control-adapter.md`, `feature-map.example.md` and `verify-existing-fix.md` (E2–E4 in the workflow-paperclip FINDINGS). It has no Slack, no triage marker, no github.com links and no fix step.

What should work:
- Input: a bug report in the chat with steps, expected, actual, commit or version, platform. A missing essential detail gives one question and no run.
- It refuses to run without the app's verify skill, a passed setup check or the screen's map section (Blocked, never a guess).
- Reproduce mode:
  - name the correct and the broken end state;
  - reach the symptom through real clicks and typing, twice, with an independent reset between;
  - confirm it with one read-only state check;
  - a second look at the captures must see the broken state, or it isn't confirmed.
- Fix-check mode, when a fix commit is known:
  - the commit before the fix must show the symptom twice, or there is no baseline;
  - the fix commit must show it gone twice;
  - both run with the same backend and data.
- Old commits run in a separate git worktree inside the app's ignored artifacts folder, with dependencies linked when the manifest is the same. The worktree is removed afterwards and the link removed as a link; the developer's working copy is never touched.
- Outcomes, exactly: Reproduced, Could not reproduce (with what was tried), Blocked (with what was missing), Fix confirmed, Fix not confirmed. Plus the steps taken and the evidence folder.
- No source, company or client name.

Technical details:
- Files: `skills/reproduce-bug/SKILL.md`, `FIX-CHECK.md`, `LICENSE` (pstack's MIT text), `agents/openai.yaml` (implicit invocation allowed). Must not change other skills.
- Test seam: `tests/test_verify_skills.py` cases for reproduce-bug: the outcome words, twice, read-only check, worktree and link rules, no fix step, no source or company names. It misses agent behaviour; T5 and T6 cover that live.
- TDD: yes for the text-contract tests.

Documents: none outside the skill folder.

How to verify:
- `python -X utf8 -m unittest tests.test_verify_skills -v`: the T2 cases pass.

Verification: passed (V1)

References:
- Supports: R1, R3, R6, A1
- Depends on: none
- Rules: as T1.
- Evidence: FINDINGS V1, Review S1–S4; FINDINGS V1/V2, Review S1-S4

### T3 — Register both skills in the package and pass its checks
Status: Verified

What needs to happen: make the two skills part of workflow-axa and keep the package's checks green.

What should work:
- `.claude-plugin/plugin.json` lists `./skills/verify-app` and `./skills/reproduce-bug`.
- VENDORED-SKILLS.md credits pstack with the commit copied (`35a90942a7f02e1ebbc2443643179815f2147954`) and names both LICENSE files.
- `tests/test_package_contract.py` lists both skills (EXPECTED_SKILLS, LICENSED).
- CHANGELOG.md has an entry for the two skills.
- tests/README.md gets a section for `test_verify_skills.py`.
- Documented skill counts are updated where the validator requires it.
- No version bump, release or install: that is a separate step with the owner's OK.

Technical details:
- Files: `.claude-plugin/plugin.json`, `VENDORED-SKILLS.md`, `CHANGELOG.md`, `tests/test_package_contract.py`, `tests/README.md`, plus documents whose skill counts the validator checks.
- Test seam: the package's own validator and suite.
- TDD: no, registration and documentation; the existing contract tests fail first when a skill is unregistered.

Documents: VENDORED-SKILLS.md, CHANGELOG.md, tests/README.md.

How to verify:
- Baseline before T1: `python -X utf8 -I tools/validate.py` and `python -X utf8 -m unittest discover -s tests -p "test_*.py"` in D:\workflow-axa, failing test names saved in FINDINGS.
- After: the same two commands; no new failing names; the known intermittent `test_parallel_appends_lose_nothing` is rerun once only if it is the failure (tests/README.md).

Verification: passed (V2)

References:
- Supports: R1, R11, A1, A2
- Depends on: T1, T2
- Rules: D:\workflow-axa\AGENTS.md (commands and evidence; no install).
- Evidence: FINDINGS V2, Review S1–S4; FINDINGS V1/V2, Review S1-S4

### T4 — Make the labeler's verify skill and pass the setup and guard checks
Status: Verified

What needs to happen: run `verify-app` (read by path from D:\workflow-axa, not installed) in the labeler to write `.claude/skills/verify-labeler/` with a feature map covering My labels and its filters, then prove it.

What should work:
- The verify skill's settings name:
  - the owner's local backend (P1) as the only allowed backend;
  - `<production host 1>`, `<local backend name>` and `<production host 2>` as blocked production hosts;
  - `.env.e2e.local` as the only login source;
  - port 8101 and a phone-sized window.
- The map: `features/README.md` and `features/my-labels.md` (filters and sort, how to reach it, stable selectors, states, preconditions, evidence, gotchas).
- The 9-step setup check passes against the local backend.
- Guard proof:
  - with the backend set to a production host, the run refuses before the browser starts;
  - a request to another API host during a run is blocked and appears in the log.
- No change to app code, environment files, existing e2e tests or `utils.ts`; no new CSS (exception D11: the login helper's temporary test-browser style that hides typed login text).

Technical details:
- Files: `D:\<test app>\.claude\skills\verify-labeler\` only. Captures in `D:\<test app>\.artifacts\2026-11-18-bug-reproducer\` (ignored).
- Needs: P1–P4 from the owner first (backend address, what the database holds, a test account with labels in `.env.e2e.local`, CORS). If the database is a copy of production: a fictional test company first.
- Test seam: the setup check and the guard runs themselves (live). TDD: no, live verification of a generated skill.

Documents: none in the labeler beyond the verify skill (its AGENTS.md index is not changed in phase 1).

How to verify:
- The setup check's nine results and the two guard runs, recorded in FINDINGS with the commands.
- Human check: the owner reads `features/my-labels.md` and says it describes the screen.

Verification: passed (V5, V6, V7)
Owner acceptance: Cem, 2026-11-18, passed (V8)

References:
- Supports: R2, R5, R7, A3, A4, A5
- Depends on: T3
- Rules: D:\<test app>\AGENTS.md (backend boundaries, no secrets, agent output in .artifacts, no CSS, leave the owner's uncommitted changes).
- Evidence: FINDINGS V3–V7; FINDINGS V3-V8

### T5 — First test: check the filter-dot fix 502db1f
Status: Verified

What needs to happen: run `reproduce-bug` in fix-check mode on 502db1f "fixed the notification dot for label filters button".

What should work:
- A worktree of 502db1f^ under the labeler's `.artifacts/2026-11-18-bug-reproducer/`, node_modules linked from the main checkout (package.json identical, E14), dev server on 8101 against the local backend.
- On 502db1f^: open My labels, set one filter, and the dot is wrong twice. Video, screenshots and the dot's measured position relative to the button are captured.
- On 502db1f: the same steps, and the dot is right twice, with the same captures.
- Outcome Fix confirmed, or an honest Fix not confirmed or Blocked with its reason (S6: if 502db1f^ does not run against today's backend, Blocked, and the next bug is taken).
- Afterwards: `git worktree list` shows only the main checkout, node_modules is intact, and `git status` shows only the new verify skill files plus the owner's earlier changes.

Technical details:
- Operations: `git worktree add` and `git worktree remove` in the labeler, one directory link to node_modules (removed as a link), the dev server and Playwright against the local backend only.
- TDD: no, a live run.

Documents: none.

How to verify:
- The outcome and the capture paths recorded in FINDINGS; the three cleanup commands' output.
- Human check: the owner watches the before and after videos and agrees.

Verification: passed (V11, V12): Fix confirmed
Owner acceptance: Cem, 2026-11-18, passed (V13)

References:
- Supports: R3, R6, R8, A6, A9
- Depends on: T4, T8
- Rules: as T4.
- Evidence: FINDINGS V11–V13; FINDINGS V11-V13

### T6 — Eval: three known fixed bugs
Status: Verified

What needs to happen: two more fixed bugs from the labeler's history, chosen by what the local data can show (candidates: d07872a menus "-0" percentage, a8a31c1 action-sheet button spacing, 5febbb9 ai-import price units), each checked in fix-check mode; written down as the eval for later changes to `reproduce-bug`.

What should work:
- The two choices and why are recorded before running.
- Each comes out right on both commits: the symptom twice before, gone twice after.
- The eval list (commit, bug report text, expected outcome) is saved in the labeler at `.claude/skills/verify-labeler/eval.md`, because it names labeler commits; the generic skill holds no app's eval.

Technical details:
- Files: `D:\<test app>\.claude\skills\verify-labeler\eval.md`. If a screen is not in the map yet, its section is added through `verify-app` first.
- TDD: no, a live run.

Documents: none.

How to verify:
- Three Fix confirmed results with capture paths in FINDINGS.

Verification: passed (V12, V16, V17, V18): three cases, each right on both commits

References:
- Supports: R9, A7
- Depends on: T5
- Rules: as T4.
- Evidence: FINDINGS V12, V16–V18; FINDINGS V12, V16-V18

### T7 — Prove the guide: add a second labeler screen by following it
Status: Verified

What needs to happen: the owner picks a second labeler screen; it is added to the map following only GUIDE.md part 1, and its setup check passes.

What should work:
- A new `features/<screen>.md` in the labeler's verify skill, made through `verify-app`'s update step as the guide says.
- The setup check passes for that section.
- Anything the guide left unclear is fixed in GUIDE.md and recorded.

Technical details:
- Files: the labeler's `.claude/skills/verify-labeler/features/`, and `D:\workflow-axa\skills\verify-app\GUIDE.md` if a gap shows.
- TDD: no, a live run of the guide.

Documents: GUIDE.md if a gap shows.

How to verify:
- The section's setup-check result in FINDINGS.
- Human check: the owner reads GUIDE.md and says it is clear enough to add the next screen alone.

Verification: passed (V14)
Owner acceptance: Cem, 2026-11-18, passed (V15)

References:
- Supports: R4, R10, A8
- Depends on: T4
- Rules: as T1 and T4.
- Evidence: FINDINGS V14, V15; FINDINGS V14-V15


### T8 — Step-by-step driving through the guard (explore route)
Status: Verified

What needs to happen: agreement 5. Add an explore launcher to `verify-app` that starts a guarded, video-recording, logged-in Chromium and shares it by the run's name, so the agent drives it one action at a time with the bundled `playwright-cli attach`; then use it in the labeler and prove the guard on this route.

What should work:
- (Built as `guard/explore.spec.ts`, a journey on the same guarded fixture; see the T8 implementation note in FINDINGS.) The explore launcher refuses before Chromium starts on a production backend or a failed pin (same `loadSettings` and the global-setup lookup), launches Chromium with the resolver rule, applies the guard's request and WebSocket blocking and logging to the context (the same guarded test fixture), records video into the run folder, runs the app's own login step from the verify skill, shares the browser with `browser.bind(<run name>)`, writes the attach command into the run folder, and closes cleanly on Ctrl+C or when the agent asks.
- verify-app SKILL.md: Drive has two parts, explore (step by step, snapshot after each action, write down each action and its change) and journey (scripted proof); GUIDE.md mentions both and names Playwright Test Agents as a possible base for a feature-check job.
- reproduce-bug SKILL.md step 3: explore, then prove twice with a journey (R16); FIX-CHECK.md: proof on both commits.
- Labeler: `explore.spec.ts` copied, a `prepare.ts` login step (uses `logIn` and the login file), SKILL.md Helpers name the commands.
- Proof (R17): production backend refused before Chromium; a blocked host from the attached CLI fails and is logged; the session video exists.

Technical details:
- Files: `skills/verify-app/guard/` (explore.spec.ts, which uses the guarded fixture, drive.mjs, README), `skills/verify-app/SKILL.md`, `GUIDE.md`, `skills/reproduce-bug/SKILL.md`, `FIX-CHECK.md`, `tests/test_verify_skills.py`; labeler `.claude/skills/verify-labeler/`.
- Test seam: `test_verify_skills.py` text and code checks (refusal before launch, resolver args, the guarded fixture that explore.spec.ts uses, video, bind, login from file, no password in commands), written first. Live proof in the labeler covers behaviour.
- TDD: yes for the text-contract tests; live proof for the launcher.

Documents: guard/README.md, the labeler's verify SKILL.md.

How to verify:
- `python -X utf8 -m unittest discover -s tests -p "test_verify_skills.py"` and `python -X utf8 -I tools/validate.py` in D:\workflow-axa.
- Labeler: the three R17 proofs, recorded in FINDINGS.
- Strict type check of the labeler's verify skill files.

Verification: passed (V9, V10, V20–V26); reviews S5–S9, S9 passed

References:
- Supports: R14, R15, R16, R17
- Depends on: T3
- Rules: D:\workflow-axa\AGENTS.md; D:\<test app>\AGENTS.md.
- Evidence: FINDINGS V9, V10, V20–V26; FINDINGS V9-V26, review S9 passed
