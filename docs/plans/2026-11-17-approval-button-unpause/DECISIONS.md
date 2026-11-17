# Decisions

- D1 (by: user, 2026-11-17) "That bug needs fixing" and "first fix this bug button should work fine, test it than continue here with the spar skill … ask gpt to review the code and docs for it". Fix first, test, GPT review, then continue the /spar build.
- D2 (by: agent, 2026-11-17) One-ticket work with nothing open: agreement not required (VISUAL-REVIEW "No separate agreement"); the fix also covers a typed /approve <N>, which has the same gap (control_intent returns nothing for it). Even creating the offer is blocked while the session pause holds (offers/ isn't a plain task record), so the owner types "continue" first.

- D3 (by: user, 2026-11-17) Offer #1 (ae6a296b304207b5) approved by the typed answer "/approve 1" after its text presentation.
