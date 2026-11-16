# Select engineering guidance by the change's risks

Read this selection table during code planning/review, not every source document. Load the relevant modules before designing or editing their area. Add modules if the scope grows. A selected module is not permission to change architecture, add tooling or expand scope. For simple prose changes, framework and runtime guidance may be irrelevant.

| Trigger in the actual change | Read | Evidence to consider |
|---|---|---|
| Side-effecting checks, builds, profiling or external services | [OPERATIONS.md](OPERATIONS.md) | Actual command/prerequisites, target/isolation, authority, quiet host and fresh proof |
| Application markup, controls, interaction states, visuals or rendered/native UI | [DESIGN.md](DESIGN.md) and local `ui-design` | Mode/authority, approved sources, preview isolation, behavior and design acceptance kept separate |
| State, identifiers, units, boundary parsing, error contracts | [data-contracts.md](data-contracts.md) | Valid/invalid transitions, boundary cases, meaningful error distinctions |
| Resources, subscriptions, async work, threads, replacement or disposal | [LIFETIMES.md](LIFETIMES.md) | Setup failure, replacement, cancellation, late completion, shared ownership |
| Network calls, jobs, retries, queues, caches | [RELIABILITY.md](RELIABILITY.md) | Retry safety, time/size limits, failure visibility and recovery |
| Behavior change, bug fix, refactor or new checks | [TESTING.md](TESTING.md) | Independent expected results, meaningful failing case, final-state checks |
| Untrusted input, identity, permissions, secrets, logs or tool execution | [SECURITY.md](SECURITY.md) | Authorization, trusted boundary, injection/data exposure and negative tests |
| Runtime/loading/rendering cost, database work or memory | [PERFORMANCE.md](PERFORMANCE.md) | Same-workload baseline and result, target environment, resource/query limits |
| Persisted formats, shared APIs, native bridges, migrations or delivery | [COMPATIBILITY.md](COMPATIBILITY.md) | Supported version combinations, transitions and recovery |

**Selection example:** a React search response loads React, TypeScript, data-contracts, lifetimes and testing. Add reliability/security when network/trust handling changes. A Laravel queued charge also needs PHP/Laravel, reliability, security and relevant compatibility/performance guidance. A simple label correction must not trigger full device profiling unless project rules require it.

## Small review, not paperwork

Within the existing plan, identify the consequential risks and their checks. Pass selected rules and actual dependency context to `codebase-design`, `tdd` and `code-review` through the established adapters. These local modules complement those specialists; they do not replace them or start another workflow.

At review, inspect the final changed behavior and relevant callers. Explain material issues with evidence and the smallest correction. Report unverified aspects, not a self-awarded compliance score. Do not produce one checklist per function, one report per module, or an extra task folder. The source catalog is optional background for researching a rule; it is not mandatory context for ordinary work.

## Comments

The detail behind CORE's comment rules. When a comment and the code disagree, reason from the actual behaviour. A comment states an intended contract when it is a public doc comment, or when a spec, test name, decision record or issue supports it; that mismatch is a possible bug, never settled by deleting the comment or by assuming the code is right. Delete stale or narrating comments only in the lines an approved change already edits; list misleading comments elsewhere as comment debt. Check a claim such as "do not remove" or "talk to X first" before acting (trace the symbol, read the history); an unverified one stays unless the approved scope names its removal and any authority it names is given. Tool-read annotations (static-analysis types, decorators, pragmas, lint or type suppressions) stay until the scope justifies their replacement and the check passes without them; a suppression that hides a correctness or safety rule is flagged, never just removed.

## Applying defaults

Use the existing project error model, resource owner, design system and test runner. A general preference cannot justify breaking a supported contract. Resolve material contradictions before dependent work. Concrete examples illustrate contracts; they are not templates to paste into unrelated projects.
