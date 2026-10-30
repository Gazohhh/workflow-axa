# Meaningful tests and final-state evidence

**Applies to:** behaviour changes, bug fixes, refactors and modifications to checks. Keep the existing Matt `tdd`/review routes and project gates; this module sharpens their evidence requirements.

## Required

- Derive expected results from an agreed requirement, an independent example or a justified reference. Do not mirror the implementation's calculation in the assertion or generate expectations by calling the function being tested.
- Test meaningful observable behaviour. Internal details matter when they are part of the contract, such as bounded retries, ownership or query limits; a private helper name usually is not.
- For a reproducible bug, demonstrate a targeted failing case before its fix when feasible. For risky cleanup, establish the behaviour to preserve first. Do not canonise an existing defect as intended behaviour.
- Select unit, integration, browser/device or visual checks according to the risk. Include relevant failure, boundary, lifecycle and compatibility cases, not a universal exhaustive test list for every edit.
- Re-run affected checks on the final state after repairs. Distinguish existing failures, new failures, unavailable environments, skipped checks and observed passes.
- Do not relax assertions, coverage/gate configuration, permissions or approved screenshots to obtain success. A justified test/baseline correction is separately explained and authorised where required.

## Defaults and examples

Prefer small, readable tests with isolated data and controlled time/randomness. Avoid excessive mocks, real-time sleeps and assertions that repeat the implementation. A persistence test can write a setting, create a fresh owner and inspect its restored behaviour; checking only that a setter was called may miss broken persistence.

Keep tests and the related production change together. Use existing test helpers where their contract fits; tests themselves should not become an abstraction-heavy subsystem.

## Verification of the tests

Ask whether the new test would detect the specific broken behaviour. Use a focused negative control in a disposable fixture when practical; never mutate production state to demonstrate a failure. Keep only necessary evidence under the artifact policy. Static rule-content tests do not establish that a live agent follows those rules.

Sources: [Google review/test quality](https://google.github.io/eng-practices/review/reviewer/looking-for.html), [Microsoft agent-oriented test guidance](https://microsoft.github.io/rust-guidelines/guidelines/ai/index.html). Adapt to the project's runner and contracts; no automatic tool installation.

For side-effecting verification, use [operations.md](operations.md): inspect prerequisites and effective target/isolation, preserve protected build authority, and report current evidence rather than assumed success.
