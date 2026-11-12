# AGENTS.md

Shared coding standards come from the workflow-axa rule library installed on each machine. Before planning changes,
resolve the installed `rule-maker` skill (host skill list or the global shared-rules block) to its `rules/START.md`,
then read START, CORE and the modules START selects. If it is missing or several copies conflict, say so and stop.
Load the modules the changed files need: `TYPESCRIPT.md` (TypeScript 4.9 here), `REACT.md` (React 18.3 here),
`VITE.md` for the build, `CAPACITOR.md` for native-host or plugin work, `THREEJS.md` or `PIXIJS.md` for those
renderers, `UNITY.md` for `UnityClient/`, `OPERATIONS.md` for tests and builds, and the risk modules START and
ENGINEERING.md select. Project rules here win where they are stricter. Certify with a fresh run on current source.

## Scoped rules

Each area has its own rules file. Before editing files in an area, read its file (Claude Code loads it through the
sibling `CLAUDE.md`; Codex reads only the files from the repo root down to its working directory):

- `src/` (React, TypeScript, state, network, security, styles, renderers): [src/AGENTS.md](src/AGENTS.md)
- `test/` (Vitest, Playwright, stress): [test/AGENTS.md](test/AGENTS.md)
- `UnityClient/` (C#, Unity tests, Unity tools, Blender exporter): [UnityClient/AGENTS.md](UnityClient/AGENTS.md)
- `scripts/` and `config/` (Node build and test tools): [scripts/AGENTS.md](scripts/AGENTS.md),
  [config/AGENTS.md](config/AGENTS.md)
- `android/` and `ios/` (native hosts): [android/AGENTS.md](android/AGENTS.md), [ios/AGENTS.md](ios/AGENTS.md)

`.claude/` is tracked except `worktrees/` and `settings.local.json`: shared instructions belong in this file, shared
skills in `.claude/skills/`, personal settings in `.claude/settings.local.json`.
Project rules win over any skill. The project skills: `phone-profiling` (native Android app
performance on a phone; not the website on a phone or the iPhone), `native-builds` (APK, Production iOS export, Mac
handoff) and `device-screenshot-capture` (screenshot sets and coverage report). Their log roots
(`.artifacts/unity-native-profiling/`, `.artifacts/device-screenshot-capture/`, `.artifacts/ios-mac-build/`) are
skill-owned; other output uses the output parent below. `scenario-unity-performance` is a third-party skill written
for Unity 6.3: advice only, and its player builds and tool installs need the owner's OK like any other.

Some subagent types skip project instructions. When delegating edits or tests, pass in the prompt the Git rule (no
index-changing Git), the CRLF rule, the exact output parent, ownership, protected paths, the keep-test-setups rule, the
backend and secrets rules, the folder's `AGENTS.md` for the files involved, the shared modules in use with their
revision, and the design rule (never write CSS; copy an existing element's tag, classes and wrapper; ask the owner
when nothing matches; `style={{}}` only for runtime positions and sizes from data).

## What this is

One React 18 + TypeScript 4.9 client for two brands, **Altinstar** and **OkeyPlaza**, on desktop web, mobile web and
Capacitor Android/iOS. Unity renders the four Okey variants (101, 101 U, Katlama, Duz): WebGL on websites and
the native transport on native migration builds. Tavla, Pisti and Turkish Poker keep their Pixi/Three renderers.
`src/components/Game/GameRenderer.tsx` (`supportsNativeGame`) picks one; `src/components/Game/unity/` owns the
React integration. `UnityClient/Assets/NativeGame/` is shared Unity source with WebGL and native transports,
with tooling in `UnityClient/Tools/` ([README](UnityClient/Tools/README.md)).

Native migration: `selectUnityHost` (`unityHostSelection.ts`) reads the static `IS_NATIVE_MOBILE_BUILD`. The Altinstar
store apps (`.env.altinstar.native.android` and `.apple` set `VITE_NATIVE_MOBILE=true`) use native Unity, which
requires the UnityBridge plugin and a compatible player, with no WebGL or legacy-game fallback. Altinstar web and
mobile web and OkeyPlaza web and mobile use WebGL. Mobile web play is OkeyPlaza only: Altinstar in a phone browser shows a
"download the app" message, so test Altinstar on phones through the store app and website behaviour on phones with
`.env.okeyplaza.mobile`. OkeyPlaza has no guest login: on a dev server open `/?sessionid=local:unitytester&affiliateid=human`
(real money: free or practice tables only); Altinstar uses `?guest`. Native leases bind at `ultra`; WebGL quality
follows the **Graphics preset** in [CONTEXT.md](CONTEXT.md).

## Two brands, one codebase

- Brand and platform are fixed at build time by `.env.<brand>.<platform>` (plus `.env.altinstar.native.*`, all on top
  of the base `.env`) through `env-cmd`. A shared change ships to both brands: test both, and tell the owner to
  build both (`build:vite:altinstar:*` and `build:vite:okeyplaza:*`), and for a server call, payload or text confirm that the
  OkeyPlaza server and translations have it too.
- In new or changed branches, branch on platform or brand with the `src/config/buildTarget.ts` constants (static
  reads, so each bundle ships only its own branch); existing `isMobile()`/`clientIsOkeyplaza()` calls stay until a
  task changes that branch. Environment *data* (currency, feature flags, URLs) is read through `getEnvString`,
  `getEnvBoolean` and `getEnvNumber` (`src/config/appEnv.ts`) and the `src/helpers/environment/` modules.
- **OkeyPlaza is real money** in any currency: read it from `VITE_CURRENCY` (`getMainCurrency()`), never hardcode TRY.
  With `VITE_MONEY_IN_CENTS` on, amounts are integer cents. Convert from the number you hold; a formatted display
  string parsed back into a number is wrong by 100x or 1000x. Analytics (`trackPlayerInteraction`) is a no-op there.
- Translations come from the server's `/language/<lang>.json` at runtime; the repo copies in
  `src/assets/languages/<brand>/` and `game-assets/<brand>/multiplatform/` are fallbacks generated from the brand
  spreadsheets, and the next sync overwrites repo edits. Report wrong or missing keys to the spreadsheet owner.
  `injectLangs.js` runs `git checkout main` and `git pull` in submodules, so only the owner runs it.

## Unity / React boundary

The web decides and Unity draws. React owns sessions, game models, rules, network and the retained HTML controls
(`#rack-button-wrapper`, `#game-bank-container`); Unity owns game-area presentation and input and
emits validated intents back through the JavaScript model. The website ships its WebGL player; native Android embeds a separately exported player tied to the native binary.
Bridge messages require the exact protocol version; OTA bundles must respect native binary compatibility: a native bundle refuses an app built from a different Unity export ([native export match](docs/plans/2026-09-17-unity-web-audit/UNITY_OKEY_ARCHITECTURE.md#native-export-match-for-instant-updates)).
A contract that two languages mirror changes on every side in the same change: the Okey protocol (`okeyProtocol.ts`,
`NativeOkeyProtocol.cs`, `NativeBridgeWire.json`) and the UnityBridge plugin's methods, reject codes and capabilities
(`android/.../UnityBridgePlugin.java`, `ios/UnityBridge/.../UnityBridgePlugin.swift`,
`src/components/Game/unity/UnityBridgePlugin.ts`). A new Capacitor npm plugin also goes into the iOS `includePlugins`
list in `capacitor.config.ts`, or iOS leaves it out; a new `allowNavigation` host needs the owner's approval.

- **UI and look**: agents never write CSS or new visual assets. Prefer entries the owner approved in the
  [design kit](docs/plans/2026-09-24-reference/DESIGN_KIT.md); otherwise copy an element already in that area (same
  tag, classes and wrapper), and when nothing matches ask the owner which existing element to mimic; plain unstyled
  markup only on the owner's explicit instruction. One owner-approved exception: `style={{}}` for runtime positions
  and sizes from data (`src/AGENTS.md`), never for colours, fonts or other looks. Other areas also go through the
  shared `ui-design` route: Unity-drawn tiles, rack and table follow the references the design kit names for them, and
  native host screens in `android/` and `ios/` have no designated reference yet.
- SCSS stays ASCII: a non-ASCII character makes Sass emit `@charset` mid-bundle.
- **Tiles are one tile everywhere** (important): rack, table grid, discards, bank, indicator, throws and drags all
  draw the same Unity tile. A change to the tile itself (model, size, material, face art) changes every place; check
  each one. Place-specific settings (grid scale, spacing) and the full list: **Tile** in [CONTEXT.md](CONTEXT.md).

## Writing code

These hold in every area; they apply to the code you write or change, not to untouched legacy code. For general code
structure, comments and verification, read the shared `CORE.md`; the rules below are this repo's own contracts and
evidence.

- Ask the owner every decision the task does not settle, small technical ones and any layout, camera or look choice
  included, as grouped multiple-choice questions; keep the original behaviour until answered. An answer to an audit
  or check is not approval to implement.
- Change what the task names. Ask the owner before removing, restructuring, renaming, caching or "cleaning up"
  anything else, including code that looks dead: past unasked cleanups and refactors were reverted.
- Represent a variant as one union or enum value, not several booleans that can contradict each other. Expected
  failures are values: a typed outcome in TypeScript (`RoomRecoveryOutcome`), `bool TryX(out T)` in C#
  (`NativeQualityTier.TryParse`); an exception or `fail()` means something is broken.
- Tie every async, socket, Unity, timer and animation callback to the generation of the resource that registered
  it (a `disposed` flag, `AbortController`, attempt guard or owner identity check), and keep cleanup from throwing:
  late callbacks from a replaced owner are this repo's most frequent bug class.
- Treat data crossing a boundary (server, socket, Unity, native plugin, storage, `postMessage`, URL) as untrusted:
  parse it from `unknown` into a typed value or a typed failure where it enters. A `catch` recovers, rethrows or
  returns a typed outcome; an intentional ignore says why.
- When a flag or condition reads inverted, fix it at its source and remove the compensating negation in the same
  change; ask first when that source lies outside the task.
- A regression test fails on the code before the fix, and its fixture sends the fields production sends.
- A comment that records a measured value says what was measured.
- **Performance**: every change to something that ships (code under `src/` or `UnityClient/`, assets, build config,
  dependencies) needs a before/after measurement with the same workload, player identity and quality, even when it
  looks harmless; docs, agent rules, task records, test-only files and comments are exempt (owner, 2026-11-03).
  Who measures: for web and React changes the agent runs the existing web checks and a local before/after of the
  affected screen; for Unity or native changes the agent writes the measurement plan, asks the owner to run the device
  build, and reports the measurement as pending until then (owner, 2026-11-03).
  Measure before memoizing or caching. Goal and FPS evidence rules: [Performance](docs/plans/2026-09-24-architecture-audit/README.md#performance).
- Report what you ran and what it printed; say which checks you did not run. Call an item done only with proof (a
  test, a gate run or a screenshot); unproven code is "code done, to verify".

## Backends, money and secrets

- Dev servers and dev-tools builds connect to `staging` (Altinstar) or `dev` (OkeyPlaza); production builds without
  dev tools connect to the live server (`play` in the base `.env`, or what the published versions file names)
  (`src/actions/Init.ts`, [build pipeline section 5](docs/plans/2026-09-24-reference/BUILD_PIPELINE.md#5-the-dev-tools-flag-end-to-end)).
  The `?environment=` URL parameter overrides this on any build. Pointing a run at another server with
  `?environment=`, `VITE_DIAGNOSTICS_SERVER_ENV` or `RECONNECT_LIVE_URL`, or playing with a real player account,
  needs the owner's OK each time, naming the target.
- `.npmrc` holds a literal registry token ([ADR 0032](docs/adr/0032-keep-the-fontawesome-registry-token-in-npmrc.md)),
  `NODE_AUTH_TOKEN` authenticates the private `@redwinx` registry, and `android/keystore.properties` holds the signing
  values. Never copy them into docs, logs, findings or output, and never move or rotate them unless the owner asks.

## Setup

Node 24 for builds (the build graph needs it); 22.13+ runs tests and the dev server. New checkout, private npm access
(`NODE_AUTH_TOKEN`), Unity, ValidationProject and Unity MCP (whose package stays in the manifest,
[ADR 0020](docs/adr/0020-keep-the-unity-mcp-package-in-the-manifest.md)):
[development guide section 1](docs/plans/2026-09-17-unity-web-audit/UNITY_OKEY_DEVELOPMENT.md#1-prerequisites-and-a-new-checkout).

## Commands (Git Bash)

The owner runs **Git Bash**: owner-facing commands use forward slashes, `./build-altinstar-android.bat`,
`(cd android && ./gradlew.bat assembleDebug)` and `"$LOCALAPPDATA/Android/Sdk/platform-tools/adb.exe"`, never
PowerShell `&`, `$env:` or `.\`. These commands are the current ones; the command block in the architecture audit is
history.

- Web gate: `node scripts/test-gate/run.js --maxWorkers=4` (Vitest, every Node lane and the Playwright reconnect lane;
  needs the Playwright Chromium browser, which the owner installs with `npx playwright install chromium`, and a free
  port 4179). Vitest flags go as `--flag=value`; bare args are path filters. It needs the ValidationProject and both
  Unity player slots. On a fresh checkout, `npm run build:unity:webgl` must run first: that is a Unity player build,
  so ask the owner to run it, or report the gate as blocked. Agents never start the Unity player build on their own
  (owner, 2026-11-03).
- TypeScript: Vite transpiles without type checking, so run
  `node scripts/typecheck/compare.cjs [--base <rev>] --out .artifacts/checks/typecheck` (a concurrent run passes its own
  child folder). The repo is not type-clean: review added diagnostics, not totals.
- Lint: `npm run lint` enforces only `react-hooks/rules-of-hooks`, as a warning (`eslint.config.cjs`), so a clean
  lint proves nothing; review problems in files you touched.
- The owner runs builds. Start a web, Unity player, APK or iOS build only when the owner asks for it in that request;
  otherwise name the brands and platforms the change touches (`npm run build:vite:<altinstar|okeyplaza>:<web|mobile>`)
  and, if Unity files changed, report the Unity gate result that your own run on the final tree printed (see
  "Unity changes and builds").
- Device tests run on an APK freshly built from the current tree.

## Unity changes and builds

A Production player build refuses without a current GREEN native test proof; keep it GREEN so the owner can always
build. Build commands, the identity check and MCP use: [development guide](docs/plans/2026-09-17-unity-web-audit/UNITY_OKEY_DEVELOPMENT.md);
how the build scripts fit together, the dev-tools flag end to end and the build graph:
[build pipeline](docs/plans/2026-09-24-reference/BUILD_PIPELINE.md); Android and iOS app builds: the `native-builds` skill
(`.claude/skills/native-builds/SKILL.md`).

- **After any change under `UnityClient/Assets`, `Packages` or `ProjectSettings`**, save and close both Unity Editors
  (including one an agent drives through MCP), then rerun `npm run test:unity -- --sync` until it prints GREEN and
  say in the report that it is GREEN. It mirrors sources into the ignored ValidationProject and publishes the tracked
  proof under `UnityClient/BuildProvenance/`. Details: [UnityClient/AGENTS.md](UnityClient/AGENTS.md).
- **When the owner asks how to build, or a build refuses:** the one-command builds are `npm run build:app:android`,
  `npm run build:app:ios`, `npm run build:web` and `npm run build:all` (all three) (README "Building everything yourself");
  `npm run build:unity:all` builds every Unity player and export but no app or website. The refusal reason is in
  `.artifacts/test-gates/unity-test-gate-latest.txt`. Fix the reported failure; the guard and proof stay tool-written.
- **Before any production build**, ask the owner "with dev tools: yes or no?". `VITE_DEVICE_DIAGNOSTICS=true` in the
  env file adds the developer panel and the Unity dev tools to production builds after a [y/N] prompt
  (`config/device-diagnostics-guard.cjs`); agents answer it with `DEVICE_DIAGNOSTICS_CONFIRM=yes` as a plain command
  prefix. Set env files back to `false` only when the owner asks. Full flow:
  [build pipeline section 5](docs/plans/2026-09-24-reference/BUILD_PIPELINE.md#5-the-dev-tools-flag-end-to-end).

## Git and the working tree

- An external process stages files here. Use read-only Git only: never `add`, `commit`, `reset`, `restore --staged`,
  `stash`, `checkout`/`switch`, `rm` or `mv`. Work stays local and unstaged unless the owner authorizes publication
  for the current task.
- Never merge, rebase onto or propose merging into `development/main`; the studio merges the finished port.
- Source, tests and docs use CRLF. Command-generated delivery/iOS files keep tool-written endings (owner-approved
  exception); never normalize hashed player/provenance bytes. `sed -i` in Git Bash rewrites CRLF as LF, so edit with a tool or a Node script that keeps
  `\r\n`, and check changed files with `file <path>`. Paths marked `-text` in `.gitattributes` (Unity project,
  players, `BuildProvenance`, byte-pinned harnesses) keep each file's existing endings; several are hashed.
- **HTML sources** are the root `index.html` and `config/html-shell-config.json`; the ignored `public/game-assets/` is
  a leftover. **Brand assets**: edit `game-assets/` or shared `public/`, then restart the affected dev server (each
  Vite run prepares its own ignored copy under `.artifacts/public/`).
- **Tracked outputs** regenerate only through their commands: `altinstar-android/build/`, `altinstar-apple/build/`
  ([ADR 0015](docs/adr/0015-keep-the-mobile-delivery-outputs-tracked.md)); `public/unity-native/` and
  `public/native-player-identity.json` ([ADR 0016](docs/adr/0016-keep-the-shipping-unity-player-tracked.md));
  `UnityClient/BuildProvenance/` ([ADR 0017](docs/adr/0017-unity-build-output-is-disposable-provenance-is-tracked.md));
  the Production iOS export `ios/UnityExport/` ([ADR 0028](docs/adr/0028-track-the-production-ios-unity-export.md)).
  Builds publish them through one guarded step ([ADR 0038](docs/adr/0038-publish-tracked-outputs-under-gits-index-lock.md));
  "NOT published yet" and interrupted publishes: [build pipeline](docs/plans/2026-09-24-reference/BUILD_PIPELINE.md#tracked-outputs-session-stage-publish).
- **Evidence and test output**: before tests, builds, device checks or profiling, read the installed workflow's
  `ARTIFACTS.md` or `~/.workflow-axa/ARTIFACTS.md`; if neither is available, say so and follow this fallback.
  Agent-chosen output reuses the task's recorded parent, otherwise `.artifacts/<full-existing-task-folder-name>/`, or
  `.artifacts/checks/<stable-purpose>/` for a small check without a task; no date, phase or retry folders. Isolate
  simultaneous runs below the parent and never overwrite live output or needed before/after evidence; keep no whole
  build copy as evidence; reuse the installed SDKs and emulators. Keep test setups (worktrees, branches,
  `.artifacts` output and players) until the owner says to remove them; this is stricter than the shared cleanup
  default and wins (owner, 2026-11-03).
  Protected: review pages, visual baselines, `.artifacts/publish/`, `.artifacts/public/`, required
  `test-gates/*-latest*` verdicts, provenance, and the tool state below; never sweep `.artifacts/` or follow linked
  paths. Keep tools used by a gate/runbook and asset generators ([ADR 0018](docs/adr/0018-no-permanent-evidence-dumps-or-one-off-scripts.md)).
- **Ignored tool state** is regenerated by its tool and left alone: `UnityClient/{Library,Temp,ValidationProject}`,
  `UnityClient/Tools/unity-mcp-current`, `.artifacts/unity/`, and the build graph's `.artifacts/build-store/`,
  `.artifacts/build-graph/` and `.artifacts/g/` ([ADR 0040](docs/adr/0040-build-graph-and-content-addressed-store.md)).
  Build and test output (`dist/`, `.preview-build/`, `coverage/`, `test-results/`, `android/app/build/`,
  `public/unity-native-dev/`) is removable only after the ownership/consumer/evidence checks above; the rest of
  `android/app/` is source.
- Package and Unity Editor versions stay as installed; an upgrade is separate owner-approved work. The
  `@capgo/capacitor-updater` and sign-in plugin pins are deliberate (see [README](README.md)).
- The Android signing configuration stays as it is: values in the ignored `android/keystore.properties`, read by
  `android/app/build.gradle`, unrotated and unquoted ([ADR 0019](docs/adr/0019-keep-the-android-signing-configuration.md)).

## Conventions

- **Task folders**: every change gets a `docs/plans/YYYY-MM-DD-<slug>/` folder (`PLAN.md`, `TODO.md`, `DECISIONS.md`,
  `FINDINGS.md`), unless an existing task folder already defines that work; then continue in that folder. Folders
  with `STATUS.md` predate this workflow. `docs/` holds only `adr/` and `plans/`; `docs/plans/2026-09-24-reference/`
  and the guides the index names are current references, not task history.
- **Review pages** (the plan's `review-r<N>.html` and its `.json`) live in the task folder's `reviews/` subfolder. When asking approval for a
  revision while older review pages exist, ask the owner whether to keep or delete the older ones; the approved page
  always stays ([ADR 0018](docs/adr/0018-no-permanent-evidence-dumps-or-one-off-scripts.md) amendment).
- A concept `CONTEXT.md` lacks gets added there; for a rejected direction a future reader needs, offer an
  ADR and write it once the owner agrees.
- **Tests**: Vitest specs live in `test/unit/`, mirroring their source path ([ADR 0037](docs/adr/0037-vitest-specs-live-in-test-unit.md),
  details in [test/AGENTS.md](test/AGENTS.md)); `node:test` suites for `config/` and `scripts/` tools stay in that
  tool's `__tests__/`; Playwright and stress suites stay in `test/`.
- **Framework versions**: read version-matched docs; versions and gotchas per area are in [src/AGENTS.md](src/AGENTS.md)
  and [frameworks](docs/plans/2026-09-24-reference/FRAMEWORKS.md).

## Index

- [CONTEXT.md](CONTEXT.md): product terms (games, rooms, tiles, graphics preset, platforms). Read when a name or a game concept is unclear.
- [PRODUCT.md](PRODUCT.md): users, brand personality and UI design principles. Read before UI or layout work.
- [docs/adr/README.md](docs/adr/README.md): every lasting decision, one line each. Read before reversing a past choice.
- [Architecture audit](docs/plans/2026-09-24-architecture-audit/README.md): the performance goal and FPS evidence rules (its status, totals, run IDs and command block are history). Read before a performance claim.
- [Unity index](docs/plans/2026-09-17-unity-web-audit/README.md): the Unity architecture, development guide and protocol versions. Read before Unity or bridge work.
- [Open findings](docs/plans/2026-09-17-unity-web-audit/OPEN_FINDINGS.md) and [BACKLOG](docs/plans/2026-09-24-reference/BACKLOG.md): known unresolved issues. Read when a task touches a known problem.
- [Build pipeline](docs/plans/2026-09-24-reference/BUILD_PIPELINE.md): build scripts, dev-tools flag, build graph and server targets. Read before a build question or a build-tool change.
- [Game-screen geometry](docs/plans/2026-09-24-reference/GAME_SCREEN_GEOMETRY.md): layout, SCSS-mirrored values, `@media` rules. Read before any game-screen layout change.
- [Rack](docs/plans/2026-09-24-reference/OKEY_RACK.md) and [table grid](docs/plans/2026-09-24-reference/OKEY_TABLE_GRID.md): rack slots, drag and drop, meld grid, grid scale presets. Read before rack or table work.
- [Reconnect](docs/plans/2026-09-24-reference/RECONNECT.md): lobby, room and game sockets, heartbeats, reconnect overlay. Read before connection work.
- [Styling](docs/plans/2026-09-24-reference/STYLING.md): theme builds, zoom ladder, iOS media queries, SCSS compile. Read to find where a style lives.
- [Design kit](docs/plans/2026-09-24-reference/DESIGN_KIT.md): reusable components and their approval state. Read before any new or changed presentation.
- [Analytics](docs/plans/2026-09-24-reference/ANALYTICS.md): event keys, `schema_rev`, dashboard queries. Read before adding or changing an event.
- [Frameworks](docs/plans/2026-09-24-reference/FRAMEWORKS.md): every version, its docs link and gotchas. Read before using a library API.
- [iPhone & Mac](docs/plans/2026-10-26-iphone-mac/PLAN.md): the iPhone host and the Mac build records. Read before iOS work.
- [README](README.md): owner build commands, release notes and troubleshooting. Read when the owner asks how to build.
