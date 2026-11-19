# Feature map section

One file per user-facing screen or feature, in `.claude/skills/verify-<app>/features/`, listed in that folder's `README.md`. Write it from the user's point of view; read the current code paths at run time instead of freezing them here.

The folder's `README.md` holds the index (one line per file: what it covers), the baseline preconditions every section starts from (the app started with Launch, Doctor passed, the test account logged in), and the driving rules (stable selectors only, restore data a journey changed, keep the evidence).

Each section file has a title, one paragraph saying what the user can do there, and exactly these four sections, in this order:

```markdown
# <Screen or feature name>

<One paragraph: what a user does here and what they see.>

## Sub-features

- `<short-id>` <one line per behaviour>

## How to get to it (user POV)

- <every way a user reaches it: menu path, button, route, deep link, shortcut>

## Driving it with <harness>

Preconditions:

- Account: <role or rights the test account needs>
- Data: <records that must exist, and how to create them through the app if missing>
- Settings: <flags or settings, or none>

- **<Action>.** <What the user does>. Drive it with <role and accessible name, label or data attribute>. <What appears.>
- **Reset.** <How to return to the starting state so a second run is independent.>

States: <default, loading, empty, error, selected, open, disabled and the screen's own states; mark those that do not apply>

Evidence:

- Screenshot: <what must be visible, including something that shows it is this app>
- Video: <from where to where>
- State check: <one read-only value that confirms what the screen shows: a stored value read back, a measured position, a response>

## Gotchas

- <traps that waste or spoil a run: slow loads, a control that only shows at some widths, data the test account lacks>
```

Never use generated class names, hashes, child positions or bare coordinates as selectors. When a precondition is missing, the journey reports it as missing here; never weaken the journey to pass.
