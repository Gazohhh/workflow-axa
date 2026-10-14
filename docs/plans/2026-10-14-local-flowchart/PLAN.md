# Local flowchart dependency correction

## Checkpoint
- Phase: completed locally; live host pilot not run.
- Approved scope: the user clarified to keep research/debugging/testing/review and all other existing Matt integrations; make only the flowchart local.
- Baseline: supplied workflow-axa-2.2.0.zip. Candidate version: 2.2.1.
- Next safe action after delivery: run the documented pilot in the user’s actual host; do not reinstall Matt’s collection or add an external diagram skill.

## Outcome
`workflow` continues to invoke Matt specialists. `codebase-map` reads its own local flowchart design reference and renders the approved visual style without installing or invoking Cathryn Lavery's skill.

## Scope
Update only the visual route, local design reference, dependency manifest/setup, affected documentation, regression tests and release evidence. Preserve the 27 Matt catalogue entries, eleven model routes, their adapters, questioning, grounding and approval. Keep the report schema and rendered geometry/style unchanged.

## Acceptance
- No external diagram skill is required for a visual report; missing local files are a package error, not an invitation to install a third-party skill.
- Matt research, diagnosing-bugs, tdd, code-review, grilling and all other existing entries/methods remain unchanged.
- The local flowchart guide includes the approved styling, grammar, geometry and checks; provenance remains informational, not a runtime load.
- Standalone codebase-map contains everything the design/renderer needs other than the documented Python runtime and optional local browser tools.
- Package tests pass; rendered source/examples remain valid; fresh host behavior is not claimed without actual execution.

## Exclusions
No new application features, new upstream skill copies, new design, third-party install, user-environment changes, staging, commits, publishing or remote writes.
