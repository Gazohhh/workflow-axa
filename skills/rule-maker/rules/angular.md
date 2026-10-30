# Angular defaults

Load for Angular components, templates, routing, dependency injection, reactive state or tests, together with TypeScript. Establish the affected application's actual Angular/CLI, TypeScript, RxJS and Node versions; workspaces can differ. Use the exact compatibility ranges for that Angular minor. For example, Angular 20 documentation specifies Node `^20.19.0 || ^22.12.0 || ^24.0.0`, not unrestricted "20.19 or newer". Consult current version-matched metadata/docs for other versions; this is not an upgrade instruction.

Preserve the project's supported architecture (NgModules/standalone, signals/observables, zoned/zoneless, forms and test runner). Do not convert it wholesale because the current documentation recommends a newer default. Keep template expressions side-effect free and understandable; validate external data without silent coercion and preserve typed service contracts. Scope providers intentionally; do not accidentally share page state globally or recreate a service meant to be shared.

Match subscriptions, effects, timers and pending responses to their owner. Use supported lifecycle/cleanup APIs for the installed version; Angular destruction is not the same as an Ionic page becoming hidden. Load ionic.md for Ionic navigation. Account for replacement, destroy and late completion; do not mutate a destroyed view or duplicate listeners on re-entry.

Use the existing test layout/runner. Mock the HTTP backend with the installed Angular testing API and check unexpected outstanding requests; a real environment URL is not isolation. Inspect effective test configuration and side effects before execution. Template/type checks and a build are not proof of lifecycle or native-device behaviour. Do not add broad schema/error suppressions to hide incorrect bindings.

Application presentation still follows design.md and ui-design. Existing Angular selectors, Ionic tags or CSS classes are not automatic design approval. Preserve required labels, focus and keyboard behaviour.

Primary leads, reviewed 2026-10-30: [version compatibility](https://angular.dev/reference/versions), [Angular 20 compatibility](https://v20.angular.dev/reference/versions), [lifecycle](https://angular.dev/guide/components/lifecycle), [HTTP tests](https://angular.dev/guide/http/testing). Current and archived docs can disagree on a constraint; use the actual installed package's peer requirements plus matching release documentation and report unresolved conflicts, rather than selecting whichever permits the desired upgrade.
