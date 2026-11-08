# Decisions

## Owner (grilling, 2026-11-08)
- K1 What shows: the whole screen built from kit parts. Source: owner answer "Whole screen from kit parts (Recommended)".
- K2 Format: live HTML in the report. Source: "Live HTML in the report (Recommended)".
- K3 Markup source: the saved rendered kit page. Source: "Saved rendered kit page (Recommended)".
- K4 Sketches: only when there is no kit. Source: "Only when there is no kit (Recommended)".
- K5 Before view: rebuilt from kit parts with fake data. Source: "Rebuild it from kit parts too (Recommended)".
- K6 Script-driven parts: static, in the state that matters. Source: "Static, in the state that matters (Recommended)".
- K7 Flow: small live screens in the flow. Source: "Small live screens in the flow (Recommended)".
- K8 Widths: desktop 1280 only. Source: "Desktop 1280 px only (Recommended)". See A1.
- K9 Fonts: Typekit allowed. Source: "Allow Typekit only (Recommended)".
- K10 Guard: block and name an unknown class. Source: "Block and name the class (Recommended)".
- K11 Testing: fresh run from the local folder, nothing pushed until reviewed. Source: "Fresh run from the local folder (Recommended)" and "do not commit or push just local testing".
- K12 Scope: general for all frameworks; test on Pletrix, the Cheflabels labeler app (Ionic) and Hooqd. Source: "this is general inside our skill ... Take 1 pletrix as test sample, 1 ionic for cheflabels labeler app and 1 hooqd to see".

## Agent choices (by: agent)
- A1 Phone apps are captured at 390 px (`--width`); desktop stays 1280. Reason: at 1280 the Cheflabels phone screens stretched and the thumbnails were unreadable. Told to the owner 2026-11-08; the owner then approved the 390 px Cheflabels plan ("Looks good").
- A2 Classes defined by the kit's own CSS count as existing (icon glyph classes). by: agent.
- A3 `--click` captures kit examples that only show after a click. by: agent.
- A4 A sketch next to kit screens needs `sketch_reason`. by: agent.
- A5 A copied web component must keep its shadow style. by: agent.
- A6 An approval that asks for the build lifts a plan-only pause (rc.32), narrowed after review (rc.33). by: agent; publishing approved by the owner.
