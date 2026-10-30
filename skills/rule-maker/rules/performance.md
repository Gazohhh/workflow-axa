# Performance and resource budgets

**Applies to:** work that can affect runtime, rendering, loading, memory, database or network cost. Assess impact proportionally; this default never waives an existing project measurement gate.

## Required

- Identify the workload, target environment and relevant metric before claiming improvement. Distinguish CPU time, GPU work, displayed frames, callback cadence, memory and loading latency; one does not prove another.
- Compare equivalent workloads and settings against a suitable baseline. Record important environment/build differences and uncertainty. A successful build, a shorter function or an editor-only observation does not establish device performance.
- Inspect repeated work on the affected path: unnecessary effects/queries, per-frame allocations, scene/resource creation, uploads and unbounded retention. Establish the cost before selecting a broad optimisation.
- Keep approved behaviour and visual quality intact. Do not lower resolution, remove assets, reduce correctness or skip checks to improve a metric without approval.
- Any cache, pool, memoisation or concurrency layer needs a purpose, lifetime, invalidation/limit policy where relevant and verification. Do not add it merely because a checklist mentions it.

## Defaults and example

Prefer removing demonstrated unnecessary work before adding machinery. Batching, culling and prefetching can exchange CPU, GPU, memory and latency costs; evaluate the actual constraint rather than calling them universally faster.

For a Laravel list, measure relevant query behaviour before changing eager loading. For a Unity surface, identify the bottleneck rather than claiming fewer objects guarantee faster GPU rendering. Use the project's approved profiling setup, not a new environment or capture folder per retry.

## Verification

Select the required workload/devices, warm/cold state, repetition and acceptable change with the project owner where not already defined. Use targeted measurements and existing budgets. Report unmeasured performance explicitly. Ordinary documentation edits should not manufacture profiling work unless a project rule requires it.

Sources: [Microsoft hot-path profiling](https://microsoft.github.io/rust-guidelines/guidelines/performance/index.html), [Unity CPU/GPU bottlenecks](https://docs.unity3d.com/6000.0/Documentation/Manual/OptimizingGraphicsPerformance.html), [Pixi performance tradeoffs](https://pixijs.com/8.x/guides/concepts/performance-tips). Match documentation to installed versions.

For side-effecting verification, use [operations.md](operations.md): inspect prerequisites and effective target/isolation, preserve protected build authority, and report current evidence rather than assumed success.
