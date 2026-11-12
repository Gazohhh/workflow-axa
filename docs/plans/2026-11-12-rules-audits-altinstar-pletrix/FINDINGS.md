# Findings: rules audits for Altinstar-react and D:\PletrixV2

Owner request (2026-11-12): "Alright do all the follow-ups as well" (follow-up 2 of the closed task 2026-11-12-owned-skills-and-repo-test-run: rules reviews for Altinstar-react and D:\PletrixV2). Read-only audits with rule-maker; proposals are written here (rule-maker AUDIT.md: never inside the audited repository without approval). No application repo writes.

## Facts (2026-11-12, after git fetch)
- Altinstar-react: on development/unity-native-mobile (equal to origin), 3 modified plan files; newest branch origin/fb-instant-loading-sequencing (2026-11-11). Rules stamp NONE; CLAUDE.md and config/CLAUDE.md are not the one line @AGENTS.md; AGENTS.md 2714 words.
- D:\PletrixV2: one repository holding modules/ and clients/ (core/ is its own repository with AGENTS.md); master 5 commits behind origin/master; 10 local changes (.bmad/ and untracked files); no AGENTS.md or CLAUDE.md at the root; has .claude/, .github/, .gemini/, .opencode/ folders.

## Open questions (sent 2026-11-12, round 1)
Q1 Which Altinstar branch does the audit read?
  a) The current development/unity-native-mobile, as it is. Recommended: a
  b) origin/fb-instant-loading-sequencing (switching needs the 3 changed plan files stashed).
Q2 Which PletrixV2 state does the audit read?
  a) The current local master as it is (5 commits behind origin, nothing pulled). Recommended: a
  b) Fast-forward master to origin/master first (local edits kept).
Q3 What should the PletrixV2 proposal cover?
  a) One root AGENTS.md (and a one-line CLAUDE.md) for D:\PletrixV2 that covers modules/ and clients/ and points to core/'s own rules. Recommended: a
  b) Separate rules for modules/ and clients/.


## Answers (round 1, 2026-11-12, owner via question tool)
- Q1: a (audit Altinstar-react on development/unity-native-mobile as it is)
- Q2: b (fast-forward D:\PletrixV2 master to origin/master first; local edits kept)
- Q3: b (separate rules for modules/ and clients/)


## Correction (2026-11-12, read-only checks)
- D:\PletrixV2's .gitignore ignores modules/, clients/ and core/. Each folder under modules/ (10) and clients/ (5) is its own Git repository with its own AGENTS.md and CLAUDE.md; rules_stamp: BEHIND project 1.8.7 < installed 1.8.8 for all 15 (1.8.8 needs no project action). clients/core and clients/modules are empty folders. So modules/ and clients/ have no rules gap; Q2 and Q3 were asked on a wrong premise and are superseded. The umbrella repository D:\PletrixV2 (docs, .bmad, docker files) has no AGENTS.md.
- Q2 b could not be done as asked anyway: 5 locally changed .bmad/ files are also changed by the 5 incoming commits, so a fast-forward would need your edits stashed. Nothing in D:\PletrixV2 was changed. The approval gate also refused the merge (no approved task).
- Q5 (sent 2026-11-12): what should happen for PletrixV2?
  a) Nothing more: the 15 module and client repos already have rules. Recommended: a
  b) Also audit the umbrella repository D:\PletrixV2 and propose a small AGENTS.md for it (docs, .bmad, docker files).

- Q5 answered 2026-11-12 (owner via question tool): a (nothing more for PletrixV2; the 15 module and client repos already have rules).


## Altinstar-react audit proposal (2026-11-12, read-only rule-maker audit by a subagent; branch development/unity-native-mobile @ ace3b60d3)
Runs: rules_stamp NONE; docs_check 0 blocking, 3 warnings, 12 notes (231 documents reached); --changed on rule files 0 blocking, 15 warnings; readiness inspect REVIEW_REQUIRED. Nothing in Altinstar was written. Full proposed AGENTS.md (3161 words): altinstar-proposed-AGENTS.md in this folder (copy of .artifacts/2026-11-12-rules-audits-altinstar-pletrix/altinstar-proposed-AGENTS.md).

Problems:
- P1 confirmed defect: AGENTS.md:11-14 and DESIGN_KIT.md:9 name the shared modules in lower case (typescript.md, design.md...); rules 1.8.8 files are upper case.
- P2 confirmed defect: AGENTS.md routes "verification commands" to the architecture audit README, whose command block includes owner-only builds (build:unity:local) and test:unity without --sync.
- P3 coverage gap (safety): which backend a run reaches (staging/dev vs live, ?environment=, VITE_DIAGNOSTICS_SERVER_ENV, RECONNECT_LIVE_URL) is not in auto-loaded text.
- P4 coverage gap (safety): secrets (.npmrc token per ADR 0032, NODE_AUTH_TOKEN, android/keystore.properties) have no auto-loaded rule.
- P5 conflict: third-party .claude/skills/scenario-unity-performance (MIT in frontmatter, no LICENSE) tells the agent to build players and install tools, against "agents never start the Unity player build".
- P6 policy: root CLAUDE.md holds Claude-only bullets (subagent rule, skill routes) that Codex never sees.
- P7 advisory: config/CLAUDE.md imports ../scripts/AGENTS.md; config/AGENTS.md unreachable from the index.
- P8 policy: current references live under docs/plans/ (which the shared rules call history).
- P9 coverage: PRODUCT.md, 7 ADRs, addon/HOW-TO.md, config/AGENTS.md unreachable from the index.
- P10 policy: duplicated framework versions and test layout across root and nested files (no drift yet).
- P11 policy: AGENTS.md 2714 words (advisory 1200); D2 of 2026-10-28 keeps every fact.
- P12 unknown (policy conflict): project style={{}} exception vs shared DESIGN.md rule 1.
- P13 policy: `npx playwright install chromium` does not say the owner runs it.
- P14 minor defect: injectLangs.js also runs git pull.
- P15 minor, report only: README names a public/js folder that does not exist.
Files the proposal changes: AGENTS.md (full replacement), CLAUDE.md (one line @AGENTS.md), test/AGENTS.md line 3, UnityClient/AGENTS.md line 66, docs/adr/README.md (new ADR index), DESIGN_KIT.md line 9, Unity index row, architecture audit README line 36. All CRLF. No moves. Auto-loaded words: Claude 2934 -> 3162; Codex root 2714 -> 3161.
Claim review: about 35 sampled claims verified; contradicted: module names (P1), audit command block (P2), injectLangs (P14), public/js (P15); about 220 indexed documents not verified.
docs_check false positives noted for workflow-axa: placeholder paths (src/a/b/X.ts), "React 19" read as a version claim, a ./-relative path.

## Open questions (sent 2026-11-12, round 2)
Q11 The audit's ten choices, each with a recommendation: Q1 keep every fact (~3160 words); Q2 CLAUDE.md becomes the one line @AGENTS.md (bullets move into AGENTS.md); Q3 keep config/CLAUDE.md as a recorded exception, link config/AGENTS.md; Q4 keep references under docs/plans and name them current; Q5 mark the audit command block as history (2 small edits); Q6 add the backend rule as drafted; Q7 keep scenario-unity-performance as advice only and add its LICENSE and credit; Q8 keep the style={{}} exception and record it in an ADR; Q9 new docs/adr/README.md; Q10 add the rules-checked 1.8.8 line after apply.
  a) Accept all ten recommendations, then apply the proposal to Altinstar's files (left unstaged, no commit, per the standing rule). Recommended: a
  b) Accept the recommendations, but only as a proposal for now; nothing applied.
  c) Go through the ten one by one.
Q12 (fact, asked plainly): is OkeyPlaza's dev server real money?

- Q11 answered 2026-11-12 (owner via question tool): a (accept all ten recommendations and apply the proposal to the Altinstar rule files; unstaged, no commit).
- Q12 answered: "No, test money" (OkeyPlaza dev server uses test money; the live server is real money).


## Apply (2026-11-12, owner-approved proposal, Q11 a, Q12)
- V1 Altinstar-react apply (worker + owner session): changed AGENTS.md (proposed text + "workflow-axa rules checked: 1.8.8 (2026-11-12)" + skill credit "(from scenario-labs/skills, MIT)" + "OkeyPlaza's dev server uses test money; its live server is real money"), CLAUDE.md (= @AGENTS.md), UnityClient/AGENTS.md (HOW-TO.md link), test/AGENTS.md line 3 (wording from the audit output, which this record had left out), docs/plans/2026-09-24-reference/DESIGN_KIT.md (design.md -> DESIGN.md, line 10, not 9), the Unity index row and the architecture audit README intro line; new docs/adr/README.md (0001-0042), docs/adr/0042-keep-the-runtime-style-exception.md (Q8 A), .claude/skills/scenario-unity-performance/LICENSE (exact upstream MIT text, "Copyright (c) 2026 Scenario Inc.", fetched from raw.githubusercontent.com). All CRLF. Not staged, not committed: Altinstar's AGENTS.md forbids index-changing Git (an external process stages files). The owner's 3 plan files under docs/plans/2026-10-02-graphics-settings-audit/ untouched.
- Checks: docs_check before 0 blocking, 3 warnings, 12 notes (231 reached) -> after 0 blocking, 2 warnings (AGENTS.md size, kept by Q1; config/CLAUDE.md recorded exception, Q3), 4 notes (243 reached); rules_stamp NONE -> CURRENT 1.8.8; auto-loaded words Claude 2934 -> 3182. Not verified: loading and compliance in a live Claude or Codex session in Altinstar.
- Not in scope, reported only: Unity index line 5 still says the audit README records "how to verify the current state"; P15 README public/js.
