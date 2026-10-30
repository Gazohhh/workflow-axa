# Rust defaults

**Load only for actual Rust work.** Other languages may use the shared ownership/type-safety principles without adopting Rust syntax or library patterns.

Establish the package/workspace edition, minimum supported Rust version, toolchain, target/features and lockfile. Resolve inherited workspace settings and mismatches; do not upgrade them automatically. Use the existing project's formatting, lint and test policy, including relevant feature/target combinations. Do not add nightly features or convert all Clippy suggestions into errors without approval.

Prefer idiomatic types and ownership that make the API's contract clear. Use enums/newtypes where they prevent meaningful mistakes, not as mandatory wrappers around every scalar. Borrow where appropriate rather than cloning to appease the compiler; shared ownership and cloning can be valid when the actual lifetime requires them. Prefer direct iteration when combinators obscure intent.

Use Option, Result, assertions and panic according to the contract. External input is not a justified invariant merely because a test passed. Avoid unchecked unwraps of fallible external data; explain genuine invariant assumptions where necessary. Do not impose one application's panic/error policy on every library.

Keep unsafe blocks narrow, with explicit safety obligations and a reviewed safe-facing contract. Do not add unsafe code or thread synchronisation for speculative speed. Respect runtime cancellation, blocking and lock ownership; Rust memory safety does not remove logic races, deadlocks or stale-result bugs.

Public documentation explains meaningful usage, failure/safety conditions and examples. Do not embed agent compliance essays or design diaries in API docs. Preserve required compatibility exports until their removal is approved; do not copy an upstream rule that would break consumers automatically.

**Do not transplant project-specific rules:** Google's Chromium-only async/thread restrictions are not universal Rust bans. Microsoft library throughput preferences are not automatically the goal of a latency-sensitive application. Apply the reason behind the advice to this project.

Sources: [Google Rust style/context](https://google.github.io/styleguide/rustguide.html), [Microsoft Rust guidelines](https://microsoft.github.io/rust-guidelines/), [Rust API guidelines](https://rust-lang.github.io/api-guidelines/), [Cargo manifest](https://doc.rust-lang.org/cargo/reference/manifest.html). Review against these as sources, not vendor endorsement of this package.
