# Decisions

- D1 Agreement 3 agreed (by: user, 2026-11-18): "Alright i am approving the plan." It covers the two-layer design, phase 1 with the bug job only, the guide, the first test 502db1f, the eval, and the stated assumptions S1–S8. It is not implementation approval; that is the offer.
- D2 Revision log: agreement 1 (workflow-paperclip, everything there) replaced by Q7 before agreement; agreement 2 (workflow-axa, bugs only) replaced by Q8; agreement 3 agreed.

- D3 Offer #1 (6a88b84efa431900) answered "Approve from this summary" by the owner on 2026-11-18 (by: user). It covers T1–T7 as listed in TODO.md; T4–T7 wait for P1–P4. Implementation has not started.

- D4 Offer #2 (12f89e4187bc7ad0), revising #1 with tests/test_owned_skills.py and one run of tools/verification_summary.py --run --write, answered "Approve from this summary" by the owner on 2026-11-18 (by: user).

- D5 Offer #3 (8ddcbd507e312583), revising #2 with the pinned counts in tests/test_package.py, tests/test_ui_design.py and tests/test_docs_consistency.py and one more summary run, answered "Approve from this summary" by the owner on 2026-11-18 (by: user).

- D6 Offer #4 (e10c51d6b8436c82) with agreement 4 (backend pin for <local backend name>, Playwright install in the labeler, staging copy with test data only, Dashboard for T7) answered "Approve from this summary" by the owner on 2026-11-18 (by: user). Agreement 4 agreed with it.

- D7 Offer #5 (13d12201816e53da) with agreement 5 (step-by-step driving through the guard, ticket T8) answered "Approve from this summary" by the owner on 2026-11-18 (by: user). Agreement 5 agreed with it. Q12: the owner chose to follow Lauren Tan's method (b).

- D8 Agreement 6 recorded from the owner's answers Q13–Q15 (by: user, 2026-11-18). D9 Q16: the owner accepts the documented residual that Playwright's in-memory step data holds the typed test login, which only the HTML/blob reporters or a trace would write (by: user, 2026-11-18).

- D10 Q18 (2026-11-19, by: user): the local backend's host name is replaced everywhere in this task's records, offers included, and in the paused workflow-paperclip records (27 places, now "<local backend name>"), so no committed file names it. Consequence the owner accepted: `record.py offer list` now reports offer #1 (and so every offer) as edited by hand, its canonical fields no longer matching its hash; the approvals stand as recorded in D1–D7 and the chat, not through the offer hashes.

- D11 Q19 (2026-11-19, by: user): the labeler login helper's temporary style (login field text made invisible in the test browser while the helper types, removed right after login; `journeys/support.ts`) is an accepted exception to T4's "no new CSS": it changes no app file or app style and exists only to keep the test e-mail out of videos (Q14).

- D12 (2026-11-19, by: user): "the test app was a test": the labeler's verify skill is deleted and later feature maps are the owner's own; from here the work and its reviews cover only the workflow-axa skills (verify-app, reproduce-bug and the package files). Done: the 23 files of D:\<test app>\.claude\skills\verify-labeler\ (made by this task) deleted from the working tree; the owner's staged copies of them stay in his Git index (git status shows AD) for him to unstage; the labeler's ignored `.artifacts/2026-11-18-bug-reproducer/` (21 MB of run evidence for T4–T8) is kept until the owner says otherwise. T4–T8's labeler evidence stays as history in FINDINGS.

- D13 Q20 (2026-11-19, by: user): the review loop continues until a GPT review passes, however many rounds; only then delivery and the 2.9.1 release.

- D14 Q21 (2026-11-19, by: user): "Fictional test login". The test account must use an e-mail and a password that are no real person's and no real secret (a throwaway alias used for nothing else, a password used nowhere else); set-up stops until the owner confirms both. Masking stays as a documented safety net: a form of the login it does not cover is a note, not a leak, and reviews judge masking against its documented forms. The review loop (D13) continues on everything else until a review passes.

- D15 (2026-11-19, by: user, after a spar in which Claude and GPT-6.2 Sol agreed): the test accounts are restricted throwaway agent accounts, so hiding their login is not worth its weight. Removed: the login masking (encodings, letter case, entities), the login-file stamp, the end-of-run clean of every file, the 4-character minimum and their tests. Kept: the production guard, Doctor, no proxy, the Git ignore checks, the driver's allowed commands, run.mjs's restrictions (no other config, reporter, trace or output folder), cutting query strings and fragments from addresses the driver shows and the CLI saves (an app's own tokens), the throwaway-account rule (D14) and reading the login only from the ignored login file. Supersedes the masking parts of D11 and D14 and the login-masking part of agreement 6 / Q14 for these accounts.

- D16 (2026-11-19, by: user): "keep looping with low not astra high but keep it simple we dont need to overly engineer its just a skill that does verification and produces bugs. Shouldn't be that complicated." The review loop continues with GPT-6.2 Sol at low reasoning effort, judging the skills as a simple verification and bug-reproduction tool: only problems a fresh agent following the documented steps would plausibly hit count; rare edge cases are notes. S40's beforeAll/afterAll redirect item is left as a note under this rule.

- D17 Q22 (2026-11-19, by: user): "Records without client names". Before the release commit, the client's repository, folder, database and host names in this task's records were replaced with neutral placeholders (<test app>, <test backend>, <production host 1–3>, <production domain>, <test database>), 72 places; the skills, tests and package files named none.
