# Resource lifetimes and concurrent work

**Applies to:** subscriptions, timers, GPU assets, connections, tasks, threads and owner replacement. Load the relevant framework module too.

## Required

- Establish who owns each acquired resource, who borrows or shares it, and when it is released. Do not dispose a shared texture, stop another owner's worker, or replace the project's cleanup chain with a generic destroy call.
- Pair setup with cleanup, including partial setup failure. Avoid starting side effects in code the framework may repeat without committing. Use its established lifecycle mechanisms.
- Obsolete work must not incorrectly mutate its former owner. Handle replacement, navigation, cancellation and out-of-order completion. Cancellation alone is not proof that a late callback cannot arrive.
- Respect thread/renderer affinity and ownership boundaries. Identify shared mutable state, ordering and consistency needs; do not introduce a global singleton or lock for convenience.
- Review cleanup errors and repeated disposal according to the contract. Do not require universal idempotency where the API intentionally reports misuse, but prevent accidental double release.

## Example and defaults

Room A begins loading; the player switches to Room B; A finishes last. A must not replace B or release B's resources. Reuse the existing owner/session identity or cancellation mechanism. A new request manager is not automatically needed.

Prefer a small explicit lifetime over scattered listeners and flags. Keep the meaningful unit together; splitting setup and cleanup into unrelated helpers may obscure who owns the resource. Avoid copying every resource into a task-local cache.

## Verification

Where affected, exercise setup failure, repeated mount/unmount or enable/disable, owner replacement, late/out-of-order completion, duplicate notifications and relevant cleanup paths. Use controlled scheduling rather than arbitrary sleeps. Inspect what the test observes: zero listeners after release is different from merely checking that a cleanup function was called.

Sources: [React effect lifecycle and race guidance](https://react.dev/reference/react/useEffect), [Three.js disposal and sharing](https://threejs.org/manual/pages/how-to-dispose-of-objects.html). Verify the installed framework's API and the project's actual ownership before applying a mechanism.
