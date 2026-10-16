# Questions and shared understanding

## Trigger the decision check, not just the known questions

For every new substantive goal and material change to an existing goal, invoke Matt's installed **grilling** through [SPECIALISTS.md](SPECIALISTS.md). Its job includes discovering missing decisions. Do not skip it because the prompt is long, the code owner is obvious, or implementation looks easy. `grill-me` is the user's manual wrapper; workflow calls the reusable `grilling` specialist.

A complete request may produce no further questions. Record why the relevant choices are settled; there is no minimum question count. Reuse a prior decision check for an unchanged approved task after checking that its sources still apply. Resume only the affected branches after new information, a changed outcome or contradictory answers. Lightweight edits, ordinary explanations and single access questions do not need a design interview. Respect an explicit no-interview instruction: record it, provide labelled options or blocked work rather than silently deciding protected matters.

## Find the real gaps

Inspect enough current code to make questions informed, but do not choose an approach before checking intent. Consider only decision areas relevant to this task:

| Area | What might still be missing? |
|---|---|
| Outcome and audience | Who uses it, what triggers it, and what visible result counts as success? |
| Scope and existing behavior | Extend or replace what exists? What must remain unchanged? |
| State and timing | Remember a choice after closing? Across devices? Apply immediately or on the next action? |
| Failures and access | Invalid input, interrupted work, unavailable service, permissions or privacy consequences? |
| Compatibility and limits | Existing data/callers, allowed dependencies or cost, target environments and exclusions? |
| Verification | Which observable checks demonstrate the agreed result, and what cannot be tested here? |

These are prompts for the specialist's bounded decision tree, not a mandatory questionnaire. Do not ask about unrelated platforms or invent product features. An established implementation convention can settle a delegated coding detail; it cannot settle an unstated product preference.

**Code is evidence of current behavior, not user intent.** An earlier agent proposal, generated plan, attractive diagram, silence or partially answered batch is not a user decision. A request, a recorded user answer or applicable approved policy can settle a choice. Resolve contradictions instead of picking the convenient answer.

## Investigate facts; ask for decisions

| Missing information | Action |
|---|---|
| Discoverable fact such as owner, runner or API behavior | Inspect code/tools/primary sources; ask only if inaccessible and necessary. |
| User choice that changes which next action is useful, valid or safe | Ask early and pause dependent work. |
| User choice that can wait during useful inspection | Save it and batch it with other currently answerable choices. |
| Immaterial unknown | Label it; do not fabricate a value or interrupt the task. |

Do not perform a lengthy investigation built on an unanswered direction constraint. Independent authorized work can continue in the active session; do not promise unsupported background work.

## Ask a useful round

Use stable question IDs, plain language, meaningful alternatives and a recommendation with its consequence. Keep technical evidence nearby, not inside an unexplained term. Only ask questions whose prerequisites are settled. After answers, update the tree and ask newly uncovered consequential questions; do not scatter questions that could be grouped. See [WRITING.md](WRITING.md).

```text
Q1 — Should the app remember this setting after someone closes and reopens it?
Today it resets when the app closes. I recommend remembering it on this device
so the user does not have to set it again. This does not add cross-device syncing.
This answer is needed before we choose how to store the setting.
```

Do not run a detached background interview that cannot receive the user's answers. The owner asks or uses the host's real question interface, records the answers, and returns them to the specialist. Missing/disabled grilling follows the explicit setup/fallback path, not a pretend local invocation.

## Record answers and close the loop

Keep a concise decision check in the existing FINDINGS (or lightweight PLAN): applicable area, settled answer and source / open Q-ID / delegated detail. No new QUESTIONS.md per task, no full skill transcript, no empty rows for irrelevant areas. Put material approved choices in DECISIONS and link them; do not duplicate their authority. Link this check in the checkpoint.

A partial reply settles only addressed items. “Yes to all recommendations” settles the recommendations actually presented; do not ask them again. Generic “go” cannot resolve an unpresented choice. A user may explicitly delegate a bounded choice; record the delegation and its limits rather than pretending an individual option was selected by them.

When no material gaps remain, prepare the plan and visual review. Do not add an empty extra “did I understand?” round before it. The report shows the understanding; the user's actual response confirms it and authorizes the identified implementation revision. Grilling completion alone does not. A draft can honestly show open choices; research/plan-only work may end with those choices documented, but affected implementation stays blocked.
