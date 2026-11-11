# Core standards

Shared standards for new and meaningfully changed work. They do not authorize a repository-wide cleanup or override approved project constraints. **Required** protects correctness, safety, authority or verification; **default** is a design preference that may be replaced by a justified, compatible approach. Explain consequential exceptions in the existing task record, not a new compliance report.

## Understand and bound the change — required

Inspect the actual implementation, callers, local changes, applicable rules and versions. Memory and old plans are leads, not current evidence or authority to replace an approved rule; resolve competing scopes through POLICY.md before recommending policy changes. Establish rules readiness before implementation planning. Investigate facts; use the workflow's grilling for user-owned decisions. Preserve the separate setup, implementation and publication approvals. New instructions do not reopen settled decisions unless their substance changes.

Make one coherent change with related tests and documentation. Preserve user edits, supported behavior and project ownership boundaries. Improving touched code is not permission to refactor unrelated code, run bulk formatting, install dependencies or upgrade frameworks.

## Prefer necessary, understandable code — default

Reuse established owners, vocabulary and patterns; a project rule for new code wins over an older neighbor that breaks it. A helper, abstraction, cache, fallback or configuration layer must solve a concrete requirement or demonstrated problem. Similar-looking lines do not by themselves justify coupling unrelated responsibilities. Keep control flow readable; early returns, loops and modest nesting are tools, not targets. No arbitrary universal function-length, zero-nesting, naming or comment-count quotas. Do not introduce interfaces or wrappers solely to satisfy a slogan.

Comments explain non-obvious intent, constraints or tradeoffs rather than narrating syntax. Preserve useful safety, API, algorithm and license documentation. Source/API docs explain the end-state; decisions and failed attempts remain in existing task history, not essays inside each function.

## Preserve contracts and ownership — required

Represent meaningful states, units and identities clearly. Validate untrusted data at the appropriate boundary; do not turn invalid input into plausible defaults silently. Preserve intentional absence/error distinctions and language-idiomatic error handling. No broad suppression or hidden failures to force success.

Respect resource lifetimes, shared ownership and asynchronous replacement. Identify relevant security, performance and compatibility effects before choosing tests. Follow START's conditional module selection; do not load every module or apply Rust-specific syntax to other languages.

## Communicate and verify honestly — required

Explain concrete meaning for a reader new to the project, then provide precise evidence. State what changes, what stays unchanged and how completion will be checked. Avoid unexplained abbreviations and unsupported claims of completeness or CPU/GPU safety.

Use version-compatible checks and targeted regression/characterization tests. Expected results come from the agreed contract, not the implementation being tested. Distinguish existing failures, introduced failures and untested behavior. Do not weaken tests, reference images, permissions or checks to obtain a pass. Project-required gates remain required unless explicitly changed by an authorized owner; host protections still apply. Inspect command prerequisites and effective environments through OPERATIONS.md. A required GREEN result is not an observed pass; an unapproved build or production-target action remains blocked.

## Protect progress and evidence — required

Reuse task records, preserve revision history and follow the shared artifact policy. Retain necessary proof rather than redundant build copies; do not delete unfamiliar/live files or recreate reusable tools per task. Pass exact scope, rules and permissions to workers; inspect their results and label self-review honestly. A readiness result is neither authenticated approval nor proof of good code.

For application UI, apply DESIGN.md and the local ui-design route before dependent work, small edits included. Never write CSS, `<style>` or `style=""`; reuse only existing kit or code classes/IDs, mirroring class and tag. When nothing matches, ask exactly "I couldn't find a matching style for [element]. Is there an existing element I should mimic?", listing only same-tag existing elements, nothing else; plain unstyled HTML only on the user's explicit instruction. Preserve existing interfaces. Selection, accessibility, preview limits and design/release acceptance remain distinct.
