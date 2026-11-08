# Findings and delivery ledger

## Fresh runs (local plugin via --plugin-dir, plan reports only)
- Round 1 (D:/wfaxa-pilot/kitpreview): Intervat, Cheflabels, Hooqd produced kit screens; gaps: phone width, icon classes, unexplained sketches.
- Round 2 (kitpreview2): Intervat all kit screens; Cheflabels 3 kit + 1 sketch (click-only header); Hooqd kit page + sidebar sketches with reasons.
- Round 3 (kitpreview3): Cheflabels used --click unaided, all kit screens; Ionic back button lost its shadow style.
- Round 4 (kitpreview4): Cheflabels all kit screens with shadow styles intact.
- Approved test builds (never copied to real repos): Hooqd Help page (typecheck, lint, i18n check, 492 + 1489 jest tests pass); Cheflabels About page (tsc, development build, 5 About specs pass). Both were first refused by the approval hook; fixed in rc.32/rc.33.

## Reviews
- Review 1 of rc.31/rc.32: blocking false resumes in control_intent; kit-check bypasses (comment, self-closing style); kit address leaks; WebSocket/service-worker requests not blocked; JSON escaping; minor items. All addressed in rc.33.
- Review 2: kit fixes closed; control_intent still resumed on questions, held approvals and prose. Rewritten.
- Review 3: tail clauses were allow-by-default; stale cache. Made deny-by-default, STATE_VERSION 18.
- Review 4: rc.33 published with the owner's "can be pushed"; it found continue/resume, answers and mixed answers bypassing the rule. Fixed in rc.34.
- Review 5: mixed answers and task scope; fixed in rc.34.
- Review 6: no blocking false resume; a question part and a later "wait" were closed before rc.34 was published.
- Cheflabels: the four files that leave the kit out of staging and ci builds were committed and pushed (c5f0451) after a clean HEAD+4-files build check (tsc, staging build, no kit code in the bundle).

## Checks
- Full suite: 951 tests, OK (13 skipped), 2026-11-08 before the rc.33 commit.
- Live capture check: Intervat kit captured with the address absent from the file; report frames render with no console errors.

## Retained / cleaned
- Test worktrees uitest and kitpreview 1-4 removed with the owner's OK; scratch captures live only in the session scratchpad.
