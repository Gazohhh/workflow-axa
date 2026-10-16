# Optional maintenance and browser helpers

These are evaluated candidates, not required dependencies. Keep Matt's research, diagnosing-bugs, tdd, code-review, grilling and other routes. Keep the flowchart procedure local. Missing optional helpers never block normal work; use the established checks and report coverage honestly. Do not install, enable or download anything from this document automatically.

## skill-creator — maintaining this workflow

Source: [Anthropic skill-creator](https://github.com/anthropics/skills/tree/main/skills/skill-creator). Use only when the user authorizes skill development/evaluation and the reviewed skill is already available, with actual source/revision and invocation policy verified.

Compare the current released workflow with the candidate on identical fixtures, host/model, permissions and specialist versions. Keep evaluator-only expected answers out of the agent workspace. Inspect actual tool traces, unanswered decisions, writes and artifacts; do not score the assistant's claim of compliance as execution. Preserve evidence locally and sanitize it. Do not auto-install a runner, spend an unapproved paid budget, change baseline answers, publish results or automatically rewrite the skill outside the approved scope.

The package's behavioral case format is its own manual evaluation input, not asserted to be compatible with this helper's native eval format. Adapt only after inspecting the installed version. No ordinary feature task needs this helper.

## webapp-testing — browser verification

Source: [Anthropic webapp-testing](https://github.com/anthropics/skills/tree/main/skills/webapp-testing). Opt in for report/web-interface verification when already installed, compatible and useful beyond the existing project tests.

Use the existing browser/test setup, a controlled viewport and stable data. Wait for the required element/state and loaded fonts; do not treat networkidle or a fixed sleep as proof of readiness. Inspect actual behavior, keyboard operation and screenshots. Use an authorized local server only when necessary, with bounded lifecycle/cleanup. No uploads, production probing, dependency installation or browser download without separate authority. Never update a reference screenshot to suppress a failure.

Reference: [Playwright page readiness](https://playwright.dev/python/docs/api/class-page#page-wait-for-load-state) discourages networkidle for test readiness. [Visual comparisons](https://playwright.dev/docs/test-snapshots) explains controlled environments and reference images. Local Python checks do not become live specialist invocation merely because they follow similar methods.

## Both helpers

Supply existing plan/approval, allowed writes, evidence destination and relevant local adapters. Verify actual outputs. Incompatibility means skip/resolve this optional integration, not bypass permissions or replace the main workflow. Log “evaluated”, “available”, “used” and “verified” distinctly. These sources were reviewed on 16 October 2026; check the installed revision before use rather than silently following upstream main.
