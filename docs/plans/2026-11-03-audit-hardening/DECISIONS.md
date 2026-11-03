# Decisions

Open questions for the owner (asked 2026-11-03 with the r1 plan).

## Q1 — What counts as approval for code edits
- (a) The current task's Approval line, and the user's words it quotes must appear in a real user message in this session or the recorded one. Recommended: the agent can write the line, but it cannot fake a user message.
- (b) The Approval line alone. Simpler, but the agent can write it itself.
- (c) Keep today's rule (any phase name in the session). Not recommended: E1-E3 show it lets edits through.

## Q2 — Small-change route
- (a) One builder (the main session) and one independent reviewer, with the escalation rule in T6. Recommended.
- (b) Keep a fresh worker for every ticket.
Asking both gates in one message for small changes stays as today ("both at once when nothing is open"). Changing that is a separate policy choice, and this plan does not change it.

## Q3 — A licence for workflow-axa's own code
The vendored skills carry their own MIT licences, but the project has none at its root. Options: (a) MIT, (b) another licence you name, (c) none for now, private use.

## Q4 — Release package
- (a) Add `tools/build_release.py` now, with the include list in T8. Recommended.
- (b) Later.

## Q5 — Paid live acceptance runs (T9)
Measured live runs cost between about $1 and $17 each in this session's headless summaries. Options:
- (a) Up to 8 headless Claude runs on fixtures, plus Codex runs.
- (b) Claude only.
- (c) None: report only the static and helper tests.
