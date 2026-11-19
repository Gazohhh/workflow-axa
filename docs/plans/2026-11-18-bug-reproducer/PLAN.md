# Bug reproducer, phase 1: agents reproduce a bug report in the real app

## Current checkpoint
- Updated / phase: 2026-11-19; delivered (S57 passed); 2.9.1 prepared, waiting for the owner to commit and push (the hook blocks git commit for the agent)
- Recipe: feature; plus Security (test accounts, which backend the browser may reach, no production writes) — adds two generic skills to the package and a first app map; scope: the task (proposed); classification question: not asked (the request states the outcome)
- Rules: READY for planning / sources: D:\workflow-axa\AGENTS.md, D:\<test app>\AGENTS.md, shared START, CORE, READINESS (installed 1.9.0; this repository has no stamp line, the labeler is stamped 1.8.7; neither blocks) / scope: planning / limits: implementation needs its own offer and approval
- Agreement (gate one): agreed — agreements 3, 4, 5 and 6 (2026-11-18; 6 from the owner's answers Q13–Q15)
- Offer: #5 (13d12201816e53da), approved from the summary in chat 2026-11-18 (D7); its JSON keeps the draft state because the approval was not recorded through the host's `offer approve`; since D10 every offer file is hand-edited (the backend name removed), so the offer hashes no longer match; revises #4–#1 (superseded)
- Implementation: T1–T8 implemented and verified (V1–V74)
- Verification / owner acceptance: all checks passed; owner accepted the T4 map (V8), the T5 videos (V13) and the T7 guide (V15); reviews S1–S32 (S9 passed; S10–S32 failed, repaired in V27–V49; the masking was then removed by D15, V50; S33–S56 failed, repaired in V51–V74 (S41–S56 at low effort with a simple bar, D16); S57 re-check pending; the loop runs until a review passes, D13)
- Blockers: none
- Changed files: skills/verify-app/, skills/reproduce-bug/, tests/test_verify_skills.py, tests/test_package_contract.py, tests/test_owned_skills.py, tests/test_package.py, tests/test_ui_design.py, tests/test_docs_consistency.py, tests/README.md, .claude-plugin/plugin.json, VENDORED-SKILLS.md, README.md, CHANGELOG.md, VALIDATION.md, docs/plans/2026-11-18-bug-reproducer/
- Scope paths: `skills/verify-app/`, `skills/reproduce-bug/`, `.claude-plugin/plugin.json`, `VENDORED-SKILLS.md`, `CHANGELOG.md`, `tests/`; in the labeler: `.claude/skills/verify-labeler/`
- Next safe action: re-check of the simplified skills (S57, low effort, D16), workflow-axa skills only (D12); then delivery and the 2.9.1 release the owner asked for (commit and push), then the delivery record; the owner re-stages the labeler files before committing

## Working context
- Owner: Cem. Repository D:\workflow-axa (package 2.9.0-rc.4). Also touched: D:\<test app> (branch development/main, its own rules). Not touched in phase 1: D:\workflow-paperclip.
- Task identity: moved here from D:\workflow-paperclip\docs\plans\2026-11-18-bug-reproducer on the owner's Q7 answer (2026-11-18). That folder keeps the evidence E1–E16, and the questions Q1–Q7 with their answers. Anything after phase 1 is open (owner, 2026-11-18).
- Source material: pstack (https://github.com/cursor/plugins/tree/main/pstack, MIT): `create-verification-skill`, `maintain-verification-skill`, benny `reproduce-and-fix-issues` with `control-adapter.md`, `feature-map.example.md`, `verify-existing-fix.md`. Not installed; copied as this package's own text, the way blast-radius and unslop were (VENDORED-SKILLS.md).
- Test output: `.artifacts/2026-11-18-bug-reproducer/` in the labeler (its AGENTS.md rule). Cleanup: worktrees and links after each run; captures after the owner accepted A5 and the evidence is recorded.

## Goal and acceptance

The owner's words: "Create me a full plan. How it would fit into our system and how we can do our first test." Then (Q7): the generic skills belong in workflow-axa, so they are maintained once for every repository.

Goal: a bug report becomes a reproduction in the real app, done by an agent, with evidence, before a developer reads code. Phase 1 proves it on <test app> with a bug that is already fixed.

## Baseline before this change
- 2026-11-18, D:\workflow-axa at 3ddfcb1 with no local diff (only this task folder untracked); Windows 11, Python 3.14 (python --version), Git for Windows.
- `python -X utf8 -I tools/validate.py`: exit 0 ("PASS: ... 20 local skills").
- `python -X utf8 -m unittest discover -s tests -p "test_*.py"`: 1544 tests, 1 failure, 14 skipped. Failing: `test_offers.RecordCommandLine.test_record_py_offer_runs_the_offer_commands` — first error: `AssertionError: False is not true` at the assertion that the presentation starts with "CSS: off (machine setting; display only)". Environment: this machine's CSS switch reads as on (the offer presentation printed "CSS: on"), so the test depends on the machine setting.
- Output kept in `.artifacts/2026-11-18-bug-reproducer/baseline-tests.txt` and `baseline-validate.txt` (ignored); removed at delivery.

## Agreement

Agreement 3, 2026-11-18. Agreed by the owner on 2026-11-18 ("Alright i am approving the plan."). It replaces proposed agreement 2 after the owner's Q8 answer: make the general design clear, build only the bug job in phase 1, and add a guide for adding features to a map and jobs later.

### What we are building, in one paragraph
A general way for an agent to check something in the running app, with evidence, built in two layers. Layer 1 knows how to start and drive one app safely and record what happens; it knows nothing about bugs. Layer 2 is a job on top: what goes in and which outcome words come out. Phase 1 builds layer 1 for the the test app labeler and one job, the bug job: reproduce a bug report, and check a known fix. It also writes a guide, so you can later add screens to the map and add new jobs (such as checking a new feature) without redesigning anything. The first test proves the bug job on a bug we already fixed. Everything after phase 1 is open.

### The two layers
| Layer | What it does | Piece | Where |
|---|---|---|---|
| 1, generic maker | Studies an app's repository and writes that app's verify skill and feature map; adds features to an existing map later | `verify-app` | workflow-axa `skills/verify-app/` |
| 1, per app | Starts the app, checks it's the right one, drives mapped screens, blocks production, takes screenshots, video and a state check, cleans up | `verify-labeler` (made by `verify-app`) | labeler `.claude/skills/verify-labeler/` |
| 2, a job | Input, rules and outcome words for one kind of check, using layer 1 | `reproduce-bug` (phase 1's only job) | workflow-axa `skills/reproduce-bug/` |
| Guide | How to add a feature to an app's map, and how to add a new job | `verify-app`'s guide | workflow-axa `skills/verify-app/` |

Possible later jobs, not built and not decided (written in the guide as examples only): check a new feature against its acceptance steps; check a change or pull request; a smoke test of key journeys before a release or live update; before/after screenshots for a UI change; a performance check of one journey. Not what this is for: unit-level logic (unit tests), backend-only API checks (plain HTTP), real hardware (Godex printer, camera), load testing, and design approval (a person).

Both workflow-axa skills are written as the package's own text from pstack (MIT): `verify-app` from `create-verification-skill` and `maintain-verification-skill`; `reproduce-bug` from benny's repro rules with `control-adapter.md`, `feature-map.example.md` and `verify-existing-fix.md`. pstack is not installed.

### Requirements
- R1 `verify-app` and `reproduce-bug` in workflow-axa, registered in `.claude-plugin/plugin.json`:
  - pstack is credited only in VENDORED-SKILLS.md, with its LICENSE file in each skill folder; no file under `skills/` names a source (`test_owned_skills.py`);
  - neither holds anything about AXA, the test app or a client;
  - `verify-app` writes to `.claude/skills/verify-<app>/` and leaves out pstack's Cursor-only steps.
- R2 Layer 1 knows nothing about bugs or any other job. An app's verify skill can do the seven driver capabilities (bring up, drive the UI, drive mapped features and states, read-only state check, screenshot, video, cleanup) and passes the 9-step setup check before any job uses it (E3 in the workflow-paperclip FINDINGS).
- R3 The bug job (`reproduce-bug`), from benny's rules:
  - input: a bug report given in the chat (steps, expected, actual, commit or version, platform); a missing essential detail gives one question and no run;
  - reproduce the exact symptom twice through real clicks and typing, confirmed by one read-only state check and a second look at the evidence;
  - with a known fix commit, check the fix: the commit before it and the fix commit, twice each;
  - fail closed when the app's verify skill, its map section, the backend or the driver is missing;
  - outcomes: Reproduced, Could not reproduce (with what was tried), Blocked (with what was missing); in fix-check mode Fix confirmed or Fix not confirmed;
  - no fix step.
- R4 The guide (Q8), part of `verify-app`, written for someone new:
  - adding a feature to an app's map: what a map section holds (how a user gets there, controls and stable selectors, states, preconditions such as account, data and permissions, evidence, gotchas), how to ask `verify-app` to add or update it, how to run the setup check for that section, and keeping the map current when a feature changes;
  - adding a new job: what a job defines (its input, its rules, its outcome words, its evidence), that it only uses layer 1 and never drives the app another way, that it keeps the safety rules, and how it is registered and tested in workflow-axa;
  - the possible later jobs listed above as examples, marked not built.
- R5 Safety rules in code, not only in skill text (the Finance lesson):
  - `verify-app` ships a browser guard template, copied into the app's verify skill and filled with the app's own settings;
  - in the labeler, the browser may reach only the local backend and the local dev server; every other API host is blocked, so a run can't reach production even when the app's environment file points there;
  - a run refuses to start when the backend is one of the labeler's production hosts (`<production host 1>`, `<local backend name>`, `<production host 2>`); that list lives in the labeler;
  - logins come only from the labeler's untracked `.env.e2e.local`; no secrets in skills, records or captures.
- R6 Old commits run in a separate git worktree under the labeler's `.artifacts/2026-11-18-bug-reproducer/`, with node_modules linked from the main checkout; the worktree is removed afterwards and the link removed as a link; the owner's working copy is never touched (Q6).
- R7 The backend is the owner's local <test backend> with MySQL (Q5). Nothing changes in the backend repository.
- R8 First test: 502db1f, the notification dot on the label filters button (Q3), in fix-check mode: the symptom twice on 502db1f^, gone twice on 502db1f, with videos, screenshots and the dot's position check.
- R9 A small eval for the bug job: 3 known fixed bugs (the first test plus two chosen at specify from the labeler's history), each right on both commits. A later change to `reproduce-bug` is accepted only when the eval still passes.
- R10 The guide is proven once: one more labeler feature, chosen by the owner at specify, is added to the map by following the guide, and the setup check passes for that section.
- R11 The package's checks pass: `tools/validate.py` and the tests in tests/README.md, plus tests for the two skills (registered, licence present, no source or company names, outcome words and rules stated, layer 1 text free of job words).
- R12 Phase 1 builds only the above (Q4, Q8). Everything after it is open.

### What each person sees
- **Developer, one-time setup for an app:** asks Claude Code in the app's repository for `verify-app`. Gets the app's verify skill and feature map to read, then the nine setup-check steps, each passed or failed; a failure stops at its step and says why.
- **Developer, a bug:** gives `reproduce-bug` a bug report. Gets one outcome, the steps taken and the evidence folder. A screen not in the map, a backend that doesn't answer or a commit that won't build gives Blocked, never a guess.
- **Developer, a new screen in the map:** follows the guide, asks `verify-app` to add the feature, reads the new section, runs the setup check for it.
- **Someone adding a job later:** follows the guide's second part; nothing in layer 1 changes.
- **Owner, first test:** sees Fix confirmed for 502db1f with before and after videos, or an honest failure with its reason.
- **Any other repository:** nothing changes until someone runs `verify-app` there.

### What stays the same
- The existing workflow skills and their behaviour; the bug recipe does not call `reproduce-bug`.
- The labeler's app code, environment files, existing e2e tests and its "local backend only" rule, which the local backend satisfies.
- The backend repository. Paperclip, Trello, Hermes and the workflow-paperclip repository.
- Nothing is installed globally, released or published without the owner's separate OK.

### Not included
Phase 1 is the only decided work. What comes after it is open and decided by the owner after phase 1's results (owner, 2026-11-18). Possible directions, none chosen: more jobs (the examples above); more coverage (more features, a bigger eval, native-only bugs with Maestro, other apps, the workflow's bug recipe using `reproduce-bug`); running without a developer at the keyboard (where, what starts it, where results go); proposing fixes. Each needs its own plan and the owner's decision.

### Acceptance
- A1 workflow-axa has `skills/verify-app/` (with the guide) and `skills/reproduce-bug/`, each registered, each with its LICENSE file; VENDORED-SKILLS.md credits pstack; no file under `skills/` names pstack, Cursor, Slack, github.com, AXA, the test app or a client.
- A2 `python -X utf8 -I tools/validate.py` and the test suite pass, including the new skill tests; existing failures are named, not hidden.
- A3 The labeler has `.claude/skills/verify-labeler/` with a feature map covering My labels with its filters; the owner has read the map.
- A4 The setup check passes all nine steps against the local backend.
- A5 The guard: with the backend set to a production host, the run refuses before starting; a request to any other API host during a run is blocked and logged.
- A6 The first test gives Fix confirmed for 502db1f: the symptom twice on 502db1f^, gone twice on 502db1f, with videos, screenshots and the position check. The owner watches the before and after videos and agrees.
- A7 The eval's 3 bugs each come out right on both commits.
- A8 Following only the guide, the second feature is added to the map and its setup check passes; the owner reads the guide and says it is clear enough to add the next one alone.
- A9 Afterwards `git worktree list` in the labeler shows only the main checkout, its node_modules is intact, and `git status` shows only the new verify skill files plus the owner's own earlier changes.

### Agreement 4 (proposed 2026-11-18; changes only R5 and the backend)
- R5 changes for the labeler: the local backend is `http://<local backend name>`, which this machine's hosts file maps to 127.0.0.1 and ::1 while public DNS points at the real server (Q9 a). The guard pins it: Chromium resolves that name to 127.0.0.1 itself (host-resolver MAP), and the run refuses to start unless Node also resolves it to this machine. `<local backend name>` leaves the labeler's blocked list; `<production host 1>`, `<production host 2>`, `<production domain>` and `<production host 3>` stay blocked. `verify-app`'s guard gains this pin as a general setting (a backend that must resolve to this machine).
- P2 settled (Q10 a): the database is a copy of staging with test data only; runs use a test account in it as it is.
- P5 settled (Q11 b): `npm install` in the labeler, then `npx playwright install chromium`; other packages may change because the lockfile is older.
- T7's screen is Dashboard.

### Agreement 5 (proposed 2026-11-18; the owner chose to follow Lauren Tan's method, Q12 b)
- R14 Step-by-step driving, as in pstack: the agent drives the app one action at a time and looks at the result after each action, before deciding the next. It uses Playwright's own bundled `playwright-cli` (in the labeler's installed 1.65.1), attached to a browser that the guard launched.
- R15 The guard stays in code for this route. `verify-app` gains an explore launcher (`guard/explore.ts`). It launches Chromium with the guard's resolver pin, applies the same request and WebSocket blocking and logging to the browser context, records video into the run folder, logs in itself with the ignored login file (the password never appears in a command, the chat or a record), and then shares the browser under the run's name (`browser.bind`). The agent attaches with `playwright-cli attach <run name>`. Playwright MCP's own origin lists are not used as the guard, because Playwright says they are not a security boundary.
- R16 `reproduce-bug` step 3 becomes two parts. Explore: follow the report step by step through the attached browser, using the accessibility snapshot after each action, and write down each action and what changed. Prove: save the path that showed the symptom as a journey, and run it twice through `playwright test` with video, screenshots and the state check (unchanged rules: twice, reset between, second look). Fix check: the proof runs on both commits; exploring once on the commit before the fix is enough to find the path.
- R17 Proof for the new route, added to T4's checks: an explore session against a production backend refuses before Chromium starts; from the attached CLI a page request to a host that is not allowed fails and shows as blocked in `network.log`; the session's video is saved.
- New ticket T8 (depends on T3, before T5): build the explore route in `verify-app` (template, tests, SKILL and GUIDE text), copy it into the labeler's verify skill with a labeler login step, and prove R17. T5 then depends on T8.
- The guide names Playwright Test Agents (planner, generator, healer) as the likely base for a later "check a new feature" job; not built.
- Unchanged: everything else in agreements 3 and 4.

### Agreement 6 (2026-11-18, the owner's own answers Q13–Q15)
- The verify driver is a guard against mistakes, not a security boundary (the agent also has a shell): it refuses dangerous commands and every option; `eval` stays for read-only measurements under the written rule that it never changes the page, storage or state (Q13 a).
- The test account's e-mail is personal data: runs never open screens that show it (in the labeler: User Settings, `/user-settings`); a check that needs one is Blocked for a person; a capture showing it by accident is deleted (Q14 b).
- Machine values are never written in skill text or committed settings (owner: "i dont want to hardcode the namings in skills or md files nowhere"): each app's committed settings name an ignored local file holding this machine's backend address, pin and other dev server; without it the guard refuses with what to fill in. On the owner's PC the pin is `::1` (Q15 a; Agreement 4's `127.0.0.1` is replaced), kept in that local file.

### Preconditions (facts the owner supplies before execution)
- P1 The local backend's address.
- P2 What the local database holds; if it is a copy of production, runs use a separate fictional test company, because captures must not show client data.
- P3 A test account there with some labels, its login put by the owner in `.env.e2e.local`.
- P4 The local backend accepts requests from the dev server's address (CORS); the setup check shows it.

### Assumptions the owner can reject
- S1 Names: `verify-app` and `reproduce-bug`. The bug job keeps a bug-specific name because each job is its own skill; a later job gets its own name.
- S2 The guide is a file inside `verify-app`, so it travels with the skill to every machine.
- S3 Both skills can be invoked by the model as well as typed by a person ("reproduce this bug", "add the stock count screen to the map").
- S4 The first test runs the candidate skills through the package's existing `tools/stage_candidate.py`, without installing over the current plugin; a release (version bump, CHANGELOG, install) is a separate step with the owner's OK.
- S5 Phone-sized browser window (Playwright mobile emulation); the worktree's dev server on port 8101.
- S6 If 502db1f^ doesn't work against today's local backend, the first test is Blocked and the next bug from the labeler's history is used.
- S7 The two pstack texts not read in full yet are read whole at specify; any Cursor-only dependency we can't replace comes back to the owner.
- S8 We copy pstack's text as of 2026-11-18 and maintain it ourselves; pstack updates don't reach us.

## Outcome

Delivered 2026-11-19 (reconciled by the builder, self-performed; the independent reviews are S1–S57 by GPT-6.2 Sol).

- **Asked and agreed:** two generic skills in workflow-axa (agreements 3–6 as amended by D12, D14–D16): `verify-app` writes an app's verify skill with a guard against production, and `reproduce-bug` reproduces a bug report twice in the running app or checks a fix commit, with five outcomes. Phase 1 only; later phases stay open.
- **Built:** `skills/verify-app/` (SKILL, GUIDE, FEATURE-MAP, guard: guard.ts, global-setup.ts, playwright.config.ts, explore.spec.ts, prepare.example.ts, run.mjs, drive.mjs, redact.mjs, settings and local examples, README), `skills/reproduce-bug/` (SKILL, FIX-CHECK), both registered (22 skills), `tests/test_verify_skills.py` (81 tests) and pinned counts. The labeler copy was deleted (D12); the test account's login is not hidden (D15).
- **Tickets:** T1–T8 verified (TODO), with the later changes in V27–V74.
- **Checks:** test_verify_skills 81 OK with SyntaxWarning as an error; validate PASS (22 skills); strict tsc of the guard against the real Playwright 1.65.1 types exits 0; the full suite last passed on the V63 state (1623 ran, OK, skipped 14), and runs that overlapped edits do not count; a final full suite runs with the release (VALIDATION).
- **Reviews:** S57 (GPT-6.2 Sol, low effort, D16) passed on the final skills: no blocker or should-fix. Earlier rounds S10–S56 failed and were repaired.
- **Completion check:** every path of this task is covered by the passed S57 snapshot; the check still exits 1 for `docs/spar/2026-11-19-simplify-workflow/SPAR.md`, another session's file the tool counts as a repository change, which this task does not own or review.
- **Limits:** no live browser run since the labeler copy was deleted (D12): the guard's newer parts (the browser and request guards, the device settings, run.mjs) are checked by tests, stubs and the type check only, and run for real at the first set-up in an app. Notes left open under D16: escaped redirect hops inside beforeAll/afterAll hooks; masking is gone by design (D15); query cutting is best effort. The flaky record.py lock test (outside this task) stays an open bug. Offer hashes no longer match after D10/D17 (owner-accepted).
- **Kept evidence:** the labeler's ignored `.artifacts/2026-11-18-bug-reproducer/` (21 MB, T4–T8 runs) stays until the owner says otherwise.
- **Next:** the 2.9.1 release the owner asked for (version, CHANGELOG, UPGRADE, VALIDATION, commit of this task's paths only, push).