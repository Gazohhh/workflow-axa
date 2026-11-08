# Kit screens in UI plan reports

## Current checkpoint
- Status: delivered (rc.31 kit screens, rc.32 approval rule, rc.33 review fixes)
- Owner: this Claude Code session; ownership: active
- Updated: 2026-11-08
- Repository / branch / worktree: D:\workflow-axa, main, main worktree
- Task identity: new task from the owner's request of 2026-11-08 ("how can we make it in a way that we can re-use our kit design to make the design sample instead of a fake mockup").
- Rules readiness: READY (repository CLAUDE.md/AGENTS.md, package tests).
- Agreement: agreed by the owner 2026-11-08 through the grilling answers in DECISIONS.md (K1-K11), then "this is general inside our skill as we will be using it not jsut for pletrix also the ionic and react".
- Approval: local build and testing only ("do not commit or push just local testing than we push changes where needed"); publishing approved by the owner 2026-11-08: "alright push the workflow changes if tests are done".
- Current understanding / evidence: FINDINGS.md.
- Next safe action: none; the owner judges whether kit screens are easy enough to build.

## Goal in plain words
A UI plan report shows the current and the proposed screen built from the project's own design kit, live with the kit's real styles, instead of a drawn sketch. It works the same for Blade, Angular/Ionic and React kits, so problems are visible before any code is written.

## Requirements
- R1: Build each screen from markup copied out of a saved copy of the developer's local kit page; no invented classes or CSS.
- R2: Show the screens live in the report (sandboxed, no scripts), small in the flow and full size on Inspect.
- R3: Work for every stack that renders in a browser (tested: Intervat Blade, Cheflabels Ionic, Hooqd React/Tamagui).
- R4: Never write the developer's local address down; ask for it.
- R5: Sketches only where there is no kit or the kit lacks the part, with the reason shown.

## Outcome
- Delivered: `kit_snapshot.py`, `kit_screens.py`, renderer and report integration, docs (UI-FLOW, ui-design, workflow-specify, codebase-map), tests (`tests/test_kit_screens.py`, `ControlIntentTests`).
- Fresh-run evidence and reviews: FINDINGS.md.
- Not done: the real Help/About test pages were not opened in a browser (they need a login and a backend); the test builds were never copied to the real repositories, by the owner's instruction.
