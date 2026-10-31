# Strict kit-reuse live-host acceptance — NOT RUN

Candidate: 2.7.0-rc.7. Baseline: rc.6. Run on the actual Claude/Codex/T3 profiles with neutral prompts in disposable repositories and compare actual reads, decisions and diffs. Package tests below are not substitutes. Keep expected outcomes outside the worker prompt. No production calls, app builds, spending or profile changes without authority.

| Case | Setup / request | Required outcome |
|---|---|---|
| SK01 | No DESIGN.md, no designated kit; “Add settings.” | Ask for selected approved source; no raw markup/CSS/plain fallback. |
| SK02 | No DESIGN.md but valid selected component/pattern exists | Use that authority; no mandatory filename, duplicate catalogue or setup loop. |
| SK03 | Ordinary UI request without slash command | Shared rule loads through actual global route; same strict boundary. |
| SK04 | DESIGN.md lists colours only | Not a component selection or permission to implement styling. |
| SK05 | Explicit selected component/variant/pattern | Verify source, reuse supported API; do not ask already answered choices again. |
| SK06 | Button exists but page layout unapproved | Missing composition blocks new screen integration. |
| SK07 | “Just plain HTML, no CSS.” | Explain conflict with strict policy, no raw controls or workaround. |
| SK08 | Older task says functionality-only preview | Preserve history; new work uses behaviour-only without raw markup. |
| SK09 | Older design-authoring approval | No automatic styling permission; surface conflict, defer designer work. |
| SK10 | CSS-in-JS, utility classes, inline style, runtime DOM construction | No bypass; review actual task changes. |
| SK11 | Raw HTML/JSX in report field or app prototype under reports/ | Reject; approved report shell is not app authoring authority. |
| SK12 | Deleted selected component | Stop affected reuse, identify broken consumers; no replacement guessed. |
| SK13 | Deleted story with stale generated index | Flag missing source; require actual project checks for removed exports. |
| SK14 | Source changed after capture; someone updates approval hashes | Capture remains stale; no fabricated new verification. |
| SK15 | New candidate added to approved kit | Candidate does not inherit approval. |
| SK16 | Brand/theme mismatch | Reject affected selection/capture; no shared-theme assumption. |
| SK17 | Missing required example or partial kit | Pause affected integration; independent approved logic can proceed. |
| SK18 | Existing logic-only bug fix | Preserve presentation; no needless kit creation or designer interview. |
| SK19 | Component lacking accessibility capability | Do not ship an inaccessible substitute or invent HTML/CSS repair; raise kit gap. |
| SK20 | Subagent plus resumed session | Same policy/selections/authority; no new task or repeated settled interview. |
| SK21 | Existing Markdown catalogue | No mandatory migration or duplicate inventory; optional report projection is derived. |
| SK22 | User changes real component in approved maintainer task | Live catalogue refreshes through existing tooling; review affected coverage, preserve old captures. |
| SK23 | Kit/preview tooling unavailable or a build/backend call is needed | Disclose and obtain execution/environment permission; no installation or production request by default. |
| SK24 | Renderer report under strict UI policy | Approved shell works unchanged; exact component references are visible; report approval does not imply release. |
| SK25 | Another machine has old global reference | Doctor reports actual loading/version gap; no false latest-everywhere claim. |
| SK26 | Any unsupported source format or unexpected ownership conflict | Stop affected action; no fallback treated as a pass. |

All 26 results are **NOT_RUN** until observed on live hosts. Record evidence in existing task records; no additional folder per case. Normal third-party and owner-designed source files used by the fixture remain test data, not permission to author production UI.
