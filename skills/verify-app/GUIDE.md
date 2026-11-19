# Guide: adding screens and jobs

Checking something in the running app has two layers. **Layer 1** is an app's verify skill (written by `verify-app`): it starts the app, drives its screens through the feature map, keeps the browser away from production with the guard, and captures evidence. **Layer 2** is a job: one kind of check with its own input, rules and outcome words, which uses layer 1 and nothing else. Part 1 adds screens to layer 1; part 2 adds a job.

## Part 1: add a screen to an app's map

Do this when a screen or feature is new, has changed, or a job reports a screen as not mapped.

1. **Ask for it.** In the app's repository, ask `verify-app` to add the screen, naming it the way a user would ("the stock count screen", "label filters"). It reads the code for that screen and writes one section file in `.claude/skills/verify-<app>/features/`, in the shape of [FEATURE-MAP.md](FEATURE-MAP.md), and adds it to `features/README.md`.
2. **Read the section.** Check it against what you know of the screen:
   - **How to get to it** lists every way a user reaches it.
   - **Driving it** uses selectors a user would recognise (button names, labels), not class names.
   - **Preconditions** say which account, data and settings the screen needs. If the test account lacks something, say how to create it through the app.
   - **States** lists the screen's own states (empty list, filter on, error).
   - **Evidence** names a screenshot, a video and one read-only **State check**.
   - **Gotchas** holds what you know trips people up.
3. **Look before scripting.** When the section's selectors come from code reading alone, have `verify-app` walk the screen once in an explore session (guard/README.md, "Explore step by step"): the guarded, logged-in browser driven through `drive.mjs` one action at a time, reading each snapshot, so **Driving it** names the buttons and labels the screen really shows. Correct the section from what the walk saw; the session's video and notes stay in its run folder.
4. **Run the setup check for that section.** Ask `verify-app` to run the setup check for the new section only. It runs through a small journey for that section (`journeys/<screen>-check.spec.ts`: reach the screen, use one state, read the state check, screenshot, reset; a screenshot the journey takes itself goes to `testInfo.outputPath('<name>.png')`, inside the run folder, never to a plain path, which would land beside the repository's tracked files), which `verify-app` writes with the section. All nine steps must pass; a failure names its step. Fix the section, or tell `verify-app` what is wrong, and run it again.
5. **Keep it current.** When the screen changes, ask `verify-app` to update its section in the same piece of work as the change, and run its setup check again. To check the whole map, ask `verify-app` to check the map against the app; it ends clean, changed or blocked.

A section never describes behaviour the app does not have. If the screen is broken, that is a product bug for the owner, not a map change.

## Part 2: add a new job

A job answers one kind of question about the running app. Write it as its own skill in this package, next to the existing jobs, so every repository gets it.

A job defines four things:

- **Its input:** what a person gives it (for example a report with steps, expected and actual result, version and platform; or acceptance steps; or a list of journeys). When an essential part is missing, it asks one question and runs nothing.
- **Its rules:** how it drives and when a result counts, for example how many times a result must show, what must be measured, how old commits are checked out. It uses the app's verify skill for every action: it never drives the app another way, never sets internal state, and never changes the app's code.
- **Its outcome words:** a short fixed list, each with what it means and what comes with it, always including one for "could not run" with what was missing.
- **Its evidence:** what is captured (video, screenshots, the state check) and where it is kept.

Every job keeps the safety rules: the run goes through the guard, the backend comes only from the verify skill's settings, the login only from its ignored file, and nothing is written outside the app's ignored artifacts folder except what the job's owner approved.

To add it:

1. Write `skills/<job-name>/SKILL.md` (frontmatter `name` and a `description` that says when to use it), its LICENSE when the text was copied from elsewhere, and `agents/openai.yaml`.
2. Register it in `.claude-plugin/plugin.json` and in the package's contract test.
3. Add tests in `tests/` that check the skill states its input, rules, outcome words and evidence, and names no app or company.
4. Prove it live on one app with a case whose answer is known before the run.

Jobs that exist today: `reproduce-bug`. Playwright Test Agents (planner, generator, healer; `playwright init-agents`) are a likely base for a job that checks a new feature against a written plan. Possible jobs, not built and not decided, as examples only:

- check a new feature against its acceptance steps (outcomes such as Works as described, Does not work at step N, Blocked);
- check a change or pull request: the changed screens before and after;
- a smoke test of key journeys before a release or live update;
- before and after screenshots for a change on screen;
- a timing check of one journey.

Not what layer 1 is for: logic a unit test covers, backend-only checks plain HTTP covers, real hardware, load testing, and design approval, which stays with a person.
