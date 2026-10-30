# Capacitor and native-host defaults

Load for Capacitor with any web framework, including React without Ionic. Establish core, CLI, platform and plugin versions, actual Android/iOS toolchains and build identity. Check each plugin's documented compatibility; do not assume every third-party plugin uses the same version numbering as core. No automatic upgrades, native sync, package installation or migration.

Treat `cap sync` as a write operation: it can copy web output and update/install native dependencies. Inspect the project's approved build/sync commands and generated-file ownership first. Edit authoritative inputs; do not overwrite custom native source as if every Android/iOS file were generated. Preserve signing, entitlements, permission declarations, URL schemes, allowNavigation restrictions and plugin-registration conventions. Resolve required new permissions/domains explicitly; do not relax transport security to make a test pass.

Separate page visibility, app foreground/background and native process lifetime. Own and remove the appropriate plugin listener handle when its owner ends; do not remove other owners' listeners globally. Handle permission denial, unavailable plugins, background/resume, restored callbacks and late results where the changed feature needs them. Dispatch native/UI work on the platform thread required by the actual API and existing bridge contract. A browser mock is not a native-platform verification result.

Keep web/native contracts compatible across supported installed binaries. An OTA/web-only change cannot supply a new native plugin or binary capability. Check approved protocol/export identity and existing update controls before release; do not invent fallback behaviour or bypass version guards. No deployment, store submission, device installation or SDK changes merely to establish rules readiness.

For UI work load design.md and the actual framework module. Native attributes, themes, bridge-driven geometry and rendered game assets are not styling loopholes. Record actual device/build/source identity for relevant checks, not an unverified claim of performance or parity.

Primary leads, reviewed 2026-10-30: [workflow and sync](https://capacitorjs.com/docs/basics/workflow), [configuration](https://capacitorjs.com/docs/config), [App lifecycle API](https://capacitorjs.com/docs/apis/app), [plugins](https://capacitorjs.com/docs/plugins). Match the installed major and plugin docs; this module defines inspection boundaries, not a universal native build command.
