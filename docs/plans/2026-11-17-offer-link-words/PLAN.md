# Offer text with an address in it stays readable

## Current checkpoint
- Updated / phase: 2026-11-17; done, shipped in rc.3
- Rules: READY (AGENTS.md project rules; shared START, CORE, READINESS)
- Recipe: bug; modifiers Compatibility (offers already presented must render word for word); scope: the task; classification question: not asked
- Agreement (gate one): not required — one-ticket bug fix (D1)
- Offer: #1 approved (owner, question tool, 2026-11-17)
- Implementation: done (FINDINGS V1, S1)
- Verification / owner acceptance: not run
- Blockers: none
- Changed files: none

## Goal

The owner saw the rc.3 release offer and asked: "It will not be in a code block, right? If so we need to fix that still." The offer page shows a value that looks like a link or an address (it contains "://", "www." or "@") as code, so it can never become a clickable link. offers.py applies that to the whole text, so one name such as "workflow-axa@gazohhh" turns the whole "What will change" paragraph into one code block.

## Fix

- New offers use presentation format 4: only the words that look like a link or an address are shown as code; the rest of the text stays normal, escaped prose.
- Offers of formats 1 to 3 render word for word as before, so no presented or approved offer changes (the rc.3 release offer is format 3).
- Test first: a format-4 offer with "workflow-axa@gazohhh" and "https://example.com" in its text shows those two words as code and the rest as prose; a format-3 offer renders as before; a link-like word cannot become a clickable link.
