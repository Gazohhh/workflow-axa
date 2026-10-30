# Ionic defaults

Load for Ionic navigation, pages, overlays, gestures, focus and presentation. Detect the actual Ionic major and integration (Angular/React/Vue); load its framework guidance too. Do not transplant lifecycle APIs between integrations. An installed Ionic package is not approval to redesign with its default theme.

## Visibility is not destruction

An ion-router-outlet can retain a routed page while hiding it. ngOnDestroy is therefore not sufficient for work intended to run only while the page is visible. Establish whether each operation belongs to visibility, the component instance, or the application. For Angular routed pages, use the applicable ionViewWillEnter/DidEnter and ionViewWillLeave/DidLeave behaviour for visible work, and destruction for final instance cleanup. Keep intentionally longer-lived subscriptions alive; do not blanket-unsubscribe everything on leave.

Page lifecycle events are for the routed page, not automatically every child component. Re-entry must not multiply subscriptions/timers or allow an old request to replace newer state. Test enter -> leave while retained -> return -> actual destruction, including relevant navigation/back and overlay cases. Check installed-version limitations (including change-detection strategy with router outlets) before changing them.

Use the project's approved navigation and overlays. Preserve custom action-sheet contracts, back-button behaviour, dismissal roles, focus return, safe-area/keyboard handling and accessibility. Do not replace them with stock Ionic components just because they are available. A component catalogue needs explicit project authority; unsupported visual variants are gaps.

Load capacitor.md for native app state, plugin listeners, permissions, keyboard/device or platform integration. A successful browser test is not proof on the native device. Preview/new UI follows the same functionality-only boundary and existing protected outputs.

Primary leads, reviewed 2026-10-30: [Ionic 8 Angular lifecycle](https://ionicframework.com/docs/v8/angular/lifecycle), [current lifecycle](https://ionicframework.com/docs/angular/lifecycle), [React lifecycle](https://ionicframework.com/docs/react/lifecycle), [focus](https://ionicframework.com/docs/developing/managing-focus). Select the installed version; current pages are not evidence that its APIs exist in an older application.
