# Select rules against the actual project version

Read once when establishing the affected stack; refresh when the scope, dependencies, runtime or rule library changes. The newest shared guidance is not permission to use the newest API.

## Establish four different facts

| Fact | Examples | Does not prove |
|---|---|---|
| Declared requirement | `react: ^18.2`, `php: ^8.1` | The exact dependency/runtime in use |
| Resolved dependency | npm/Composer lock entry | A matching installation or deployed binary |
| Installed/runtime environment | Verified compiler/interpreter, package install, container/device | The environment used by every other teammate or deployment |
| Configuration/structure | Compiler target, renderer, Laravel bootstrap layout, Unity backend | That a guide for a different configuration applies |

Inspect per application/package, not one guessed version for a monorepo. Include workspace roots and custom manifest/lock paths. Resolve mismatches before version-sensitive edits; never run dependency updates, package scripts, Composer plugins or a remote installer to discover a version.

## Practical sources

- **JS/TS:** relevant package.json, actual manager/lockfile, engines, compiler options, renderer and plugins. npm lock v1/v2/v3 formats differ; aliases, workspaces, linked/local packages and overrides need context. A pnpm/yarn lock must not be parsed as npm or guessed from its name.
- **Angular/Ionic/Capacitor:** inspect the affected package, exact peer/runtime ranges, framework integration, angular/ionic/capacitor config and native plugin/toolchain ownership. Hash configurations without executing them. Node ranges with alternatives are not a single lower bound; Capacitor does not require Ionic.
- **PHP/Laravel:** composer.json, composer.lock, PHP/extensions, `config.platform`, relevant runtime/container and application structure. Composer's emulated platform is not the real PHP runtime. CLI, web/FPM and worker runtimes can differ. Composer requirements are not interchangeable with npm semver rules.
- **Unity:** exact ProjectVersion, package manifest/lock, pipeline, backend, supported C# level and target device. A generic .NET guide is not proof a language feature is supported in this Editor.
- **Rust:** edition, rust-version/minimum supported compiler, toolchain file, workspace inheritance, features/target and lockfile. An edition is not the compiler version.

## Apply guidance without upgrading

Load the common framework module, then inspect version-specific primary documentation for the operation in question. Keep shared principles once; add narrow compatibility notes rather than entire copied rulebooks for every release. React 18 must not receive React 19-only APIs. A Laravel 11 application upgraded from 10 may deliberately retain its earlier structure; the major version alone does not require reorganisation.

When no reviewed guidance covers a required API/version, disclose the gap, research the matching primary source and settle material uncertainty. Do not silently add the researched conclusion to the global library. Unsupported/offline documentation or ambiguous lock resolution is a limit, not a guessed pass.

## Optional tooling and boundaries

The read-only `scripts/version_facts.py` helper reports selected static declarations and lock observations to stdout, without executing project code. Use the adjacent CHECKER guide for its formats and limits. It is not a dependency solver, runtime probe, readiness verdict or compatibility certification. Unsupported formats stay explicit. The readiness snapshot also fingerprints version inputs; changed files invalidate old assessments.

Keep any consequential version facts in the existing checkpoint, not another report. Source leads: [Composer](https://getcomposer.org/doc/01-basic-usage.md), [platform emulation](https://getcomposer.org/doc/06-config.md#platform), [npm locks](https://docs.npmjs.com/cli/v11/configuring-npm/package-lock-json), [React versions](https://react.dev/versions), [Laravel structure exception](https://laravel.com/docs/11.x/upgrade#application-structure), [Cargo manifest](https://doc.rust-lang.org/cargo/reference/manifest.html).
