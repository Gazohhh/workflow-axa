# Unity and C# defaults

Inspect the exact Editor, render pipeline/packages, scripting backend, supported C# language level and target devices. Do not globally assume one project's domain-reload setting, layer numbers, bridge ownership, test proof or allocation budget.

Understand lifecycle and ownership before changing subscriptions, static state, pooling, assets or disposal. Preserve Unity object semantics and established scene/prefab/GUID references. Avoid unnecessary recurring allocations and work in hot paths; measure the actual workload rather than calling all code CPU/GPU safe. Do not automatically add pooling, batching or caching, or lower visual quality, to claim improvement.

Use the project's verification/build/provenance contracts and relevant EditMode/PlayMode/device checks. Tests passing in the Editor do not prove phone performance or shipping-player identity. Source/version upgrades and asset migrations remain separately approved work.

Primary references: [Unity manual](https://docs.unity3d.com/Manual/index.html), [Unity profiling](https://docs.unity3d.com/6000.0/Documentation/Manual/Profiler.html). Select the documentation version matching the project; these links are entry points, not a fixed required Unity version.

## Related checks

Use [VERSIONS.md](VERSIONS.md), [lifetimes.md](lifetimes.md) and [performance.md](performance.md) where relevant. Verify actual Editor/package/backend compatibility; a newer C# guide does not grant newer syntax. Cross-native/web bridge changes also need [compatibility.md](compatibility.md). Do not infer GPU work from a callback counter or impose blanket zero-allocation/pooling rules outside established hot-path budgets.
