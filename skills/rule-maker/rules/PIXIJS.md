# PixiJS defaults

Read the installed major/minor version and actual renderer/event/resource conventions. Do not interchange v7 and v8 APIs or silently rewrite the project's cleanup chain. Distinguish view-owned resources from shared textures/caches; destroy/release only what the owner contract permits.

Keep render-loop work and uploads proportional to the actual change. Culling, batching and caching have tradeoffs; measure before treating them as universal optimizations. Test teardown, re-entry, late loads and relevant interactions. Do not reduce quality or alter event behavior to improve a benchmark without approval.

Primary references: [PixiJS guides](https://pixijs.com/guides), [v8 performance guidance](https://pixijs.com/8.x/guides/concepts/performance-tips). Use version-matched guidance; a v8 reference is not authority to change a v7 project.

## Related checks

Use [VERSIONS.md](VERSIONS.md), [LIFETIMES.md](LIFETIMES.md) and [PERFORMANCE.md](PERFORMANCE.md) as applicable. Major-version resource/event APIs and destroy options differ.
