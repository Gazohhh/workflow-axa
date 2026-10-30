# React defaults

Load only for relevant React work. Detect the actual React, router, renderer and lint versions; no automatic upgrades or adoption of newer APIs. Preserve the project's established architecture, error contracts and component patterns.

Keep rendering pure. Ordinary Hooks such as useState/useEffect belong at the top level before conditional early returns, not in loops or event callbacks. Verify documented exceptions for APIs such as `use` only when installed and actually used. Prefer deriving values over extra state/effect machinery when it preserves behaviour. Effects synchronise external resources; pair setup with cleanup and test replacement, unmount and late asynchronous completion. Do not add memoisation everywhere without a demonstrated reason.

Reuse approved components and accessibility patterns. Check the actual user interaction and relevant failure/empty/loading states, not just a build. Apply the project's tests and Hook checks; do not suppress diagnostics to force a pass.

Primary references: [Rules of Hooks](https://react.dev/reference/rules/rules-of-hooks), [useEffect](https://react.dev/reference/react/useEffect). Current pages are reference leads, not permission to use APIs unavailable in the project.

## Related checks

For version selection use [VERSIONS.md](VERSIONS.md). For affected state and effects, load [data-contracts.md](data-contracts.md) and [lifetimes.md](lifetimes.md); use [testing.md](testing.md) for behavioural changes. Do not adopt React 19-only APIs in React 18 or rearrange Hook order just to reduce nesting. Renderer/compiler configuration also matters. React Compiler is not inherently React-19-only: official targets include React 17/18 with the separate runtime. Inspect the installed compiler target, runtime and approved configuration; this fact does not authorise enabling/installing it. See [compiler target](https://react.dev/reference/react-compiler/target).
