---
name: reproduce-bug
description: "Reproduce a bug report in the running app through its verify skill: the exact symptom twice, with video, screenshots and a read-only state check; or check that a known fix commit removes it. Use when someone gives a bug report, asks whether a bug still happens, or asks whether a fix works in the real app."
---

# Reproduce bug

Prove a reported bug in the real app before anyone reads code, or prove that a fix removes it. This is a job on top of the app's verify skill (`.claude/skills/verify-<app>/`, written by `verify-app`): every action goes through that skill, its feature map and its guard. This skill never changes the app's code, its settings or its data outside what the verify skill allows, and it proposes no change; it reports what the running app does.

## 1. Read the report

Collect from the report and its attachments:

- the steps a user took, from a screen the feature map knows;
- the expected result and the actual result;
- the commit, version or build it was seen on, and the platform (browser, phone, window size);
- for a fix check, the commit that fixed it.

When an essential part is missing (no steps, no expected or actual result, or nothing that tells which screen), ask one question that names exactly what is missing, and run nothing until it is answered. A missing commit means the developer's current checkout, and a missing platform means the verify skill's default window; write down that you used them. Write down the two end states before driving: the **correct end state** (what should be on screen) and the **broken end state** (what the report says is there instead), and where they part.

## 2. Check what the run needs

Stop with **Blocked** and say what is missing when any of these fails; never a guess, never another way round:

- the app has a verify skill whose SKILL.md says `Status: ready` (its setup check has passed);
- the verify skill has its driver (`drive.mjs`) and explore session; with no driver the outcome is Blocked, never a run through Playwright's CLI directly;
- the screen in the report has a section in its feature map (otherwise the outcome is Blocked, "not mapped", and the owner adds it with `verify-app`);
- the test account has what the section's preconditions name.

Then pick the route before driving anything. When the report names a fix commit, or asks whether a fix works, go to [FIX-CHECK.md](FIX-CHECK.md) now: it reproduces on the commit before the fix first, never on the fixed code. Otherwise, when the report names a commit that is not the developer's current checkout, or names the current commit while `git status --short --untracked-files=all` shows any change, untracked files included, follow FIX-CHECK.md "Run an older commit": a separate worktree with that commit's committed files, so the developer's working copy is never touched and never stands in for the commit. A report that names a version or build but no commit gets its commit first, from the repository's tags or release records, and then runs as a named commit; when none can be found, ask one question for the commit and run nothing until it is answered, never the current checkout in its place. A report with no commit, version or build runs on the developer's checkout as it is; write down its commit and whether it had local changes.

Then, once per checkout: run the first part of the verify skill's Doctor on the chosen checkout, start the app there with its Launch, and run Doctor's second part against the allowed backend. A worktree from "Run an older commit" gets this in its step 4, never a second time here. When Doctor fails, the outcome is **Blocked** with what failed. From Launch on, every way out goes through step 5, whatever the outcome.

## 3. Reproduce

Through the verify skill's Launch, Drive and Evidence, on the reported commit. Give the run its own name and write this report's journey in `<artifacts>/journeys/<run>/` before the run, never in the run folder or the verify skill's tracked folder (guard/README.md of `verify-app`, step 4 of its set-up):

1. **Explore.** Start the verify skill's explore session and attach through its verify driver (`drive.mjs`), never Playwright's CLI directly. Confirm it is the right app, account, data and screen state, then follow the reported steps one action at a time: read the snapshot, act on one element with a real click or typing, look at the result, and write down the action and what changed. Never set internal state, call hidden methods, write to storage or change the page to make the symptom appear; preconditions may be arranged only the way the feature map says. Stop when you reach the point where the correct end state and the broken end state part, and look. Stop the session; its video is the first evidence.
2. **Prove.** Save the path you found as a journey with the verify skill's helpers and one read-only state check that tells the two end states apart (a measured position, a stored value read back, a response). When the report's platform differs from the verify skill's default (a desktop browser against a phone default, another window size), set `VERIFY_DEVICE=desktop` or `mobile` and `VERIFY_VIEWPORT=<width>x<height>` on the explore command and on every proof run, so each runs on the kind of device the symptom needs. Reset as the feature map says first, so the proof does not depend on what Explore did, then run it with Playwright: it captures a video of the whole path and a screenshot of the end state with something that shows it is this app (one the journey takes itself goes to `testInfo.outputPath('<name>.png')`, inside the run folder).
3. Reset as the feature map says again, so the second attempt does not depend on the first, and run the journey again under a new `VERIFY_RUN`: the result must show twice. Every proof run of this journey, the first included (and the other commit's runs in [FIX-CHECK.md](FIX-CHECK.md)), sets `VERIFY_JOURNEYS=<artifacts>/journeys/<first run>` explicitly in its own command, because a value left from an earlier command or a new run name would look in another folder.

The broken end state must show twice. A proof run whose `network.log` has a `blocked`, `failed` or `escaped` line during the path for an origin the path needs (the app's API, a backend, a `rewrite` source, a sign-in provider, a page the path redirects to) does not count (a third-party origin such as analytics, ads or fonts does not matter), because the guard's refusal can look like the reported error: the outcome is **Blocked**, naming the origin to add to the verify skill's `rewrite` (or to fix in the app's settings). Then take a second look at the captures alone: do they visibly show the broken end state? If not, or not clearly, it is not reproduced; capture better evidence once or report **Could not reproduce**.

A loading screen, an expected dialog or a setup step is not the symptom. When the report names a platform the run cannot have (a real phone, a printer, an operating-system dialog), say so; a translated attempt (for example a phone-sized browser for a phone) is labelled translated, and a symptom that depends on the missing platform is **Blocked**.

## 4. Check a fix

Reached from step 2 when the report names a fix: [FIX-CHECK.md](FIX-CHECK.md) runs step 3 on the commit before the fix first (the symptom must show twice), then on the fix commit (it must be gone twice), with the same backend and data.

## 5. Clean up and report

Run the verify skill's Cleanup: stop what this run started, remove each worktree exactly as [FIX-CHECK.md](FIX-CHECK.md) "Run an older commit" step 5 says (the dependency link removed as a link first, then its ownership check, which keeps a worktree holding anyone else's file, then `git worktree remove`), and keep the evidence in the app's ignored artifacts folder. Then confirm the evidence is still there and `git worktree list` shows no worktree this run made.

## Outcomes

Report exactly one, with the steps taken, the commit or commits, and the evidence folder:

- **Reproduced**: the broken end state showed twice and the second look confirms it; with the state check's values.
- **Could not reproduce**: the steps ran but the broken end state did not show twice; with what was tried and what was seen instead.
- **Blocked**: the run could not happen; with exactly what was missing (verify skill, setup check, map section, backend, account, platform, a commit that does not build).
- **Fix confirmed**: the commit before the fix showed the symptom twice and the fix commit showed the correct end state twice.
- **Fix not confirmed**: the fix commit still showed the symptom, or showed neither end state (another wrong state, described with its captures), or its two runs differed, or the commit before it did not show the symptom, so there is no baseline; with which.

Never call a run reproduced or a fix confirmed from a compile, a unit test, reading the code or a plausible change: only the running app counts.
