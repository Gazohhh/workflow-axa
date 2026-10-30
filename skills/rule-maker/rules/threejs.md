# Three.js defaults

Check the installed revision, renderer and project resource-ownership model. Removing an object from a scene does not necessarily release GPU resources. Dispose resources owned by this lifetime through the established cleanup path; do not dispose shared/cache-owned resources from an individual view.

Handle listeners, animation loops, asynchronous loads and teardown consistently. Avoid unnecessary per-frame allocation and repeated uploads, but do not introduce speculative caches or renderer upgrades. Measure the actual scene/device workload when changing rendering cost. Keep quality and behaviour fixed during comparisons unless a change is explicitly approved.

Primary reference: [Disposing objects](https://threejs.org/manual/pages/how-to-dispose-of-objects.html). Verify APIs against the installed revision and project ownership decisions.

## Related checks

Use [VERSIONS.md](VERSIONS.md), [lifetimes.md](lifetimes.md) and [performance.md](performance.md) as applicable. Removing a scene object is not proof that its GPU resources were released. Preserve the project owner/cache cleanup contract; do not destroy borrowed resources or infer improvement from fewer source lines.
