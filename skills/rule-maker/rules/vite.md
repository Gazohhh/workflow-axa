# Vite defaults

Inspect the installed Vite/plugins, actual entrypoints and configuration rather than copying current web examples. Preserve established environment, brand/platform and output handling. Client-visible environment values are not secret storage; inspect what becomes bundled. No new plugin or dependency without approval.

A successful Vite transform/build is not a TypeScript typecheck. Run the existing independent type/check commands where required. Profile the relevant build or runtime workload before speculative optimisations. Reuse the project build commands and artifact policy; do not generate whole extra builds as evidence or modify guarded outputs by hand.

Primary references: [Features](https://vite.dev/guide/features), [Environment and modes](https://vite.dev/guide/env-and-mode). Verify installed-version applicability.

## Related checks

Use [VERSIONS.md](VERSIONS.md) for the installed Vite/Node/plugin combination. Client-exposed configuration is not a secret store. Build success is not a typecheck or a device/browser compatibility verdict. Read [security.md](security.md) and [compatibility.md](compatibility.md) when configuration or delivery boundaries change.
