# Decisions

- D1 (by: user, 2026-11-11, Q1): build on top of the staged rc.35 work, leave it staged.
- D2 (by: user, 2026-11-11, Q2): delete the duplicate links in `~/.claude/skills`, keep the plugin and `~/.agents/skills`.
- D3 (by: agent, 2026-11-11): also removed 6 links of the same kind that my count had missed (FINDINGS correction). Reason: leaving them kept the duplicate the owner asked to remove. Reported to the owner.
- D4 (by: user, 2026-11-11, Q3): the guard asks and pauses change work, with a one-session override.
- D5 (by: user, 2026-11-11, Q4): the five review findings are a separate second task.

- D6 (by: user, 2026-11-11): agreement r1 agreed. Owner's answer to "Does this describe what should be built?": "yes". R5 and R6 were shown as assumptions and not rejected.

- D7 (by: user, 2026-11-11): plan r1 (reviews/plan-r1.html) approved for implementation: "approve". Tickets T1 to T3. No commit, push or installation included.

- D8 (by: user, 2026-11-11, Q5): "T3 - a". Register the guard in hooks/hooks.json in this checkout once T1 and T2 are verified and reviewed, knowing that new sessions on this machine load it at once.

- D9 (by: user, 2026-11-11, Q6): "Q6 - A". Only a message that is exactly the words "continue with duplicates" lifts the pause (letter case, spaces, quotes and end punctuation ignored). This narrows R4: the words inside a longer message do not count.


## Options not chosen
- Q1 (staged rc.35 work). Not chosen: commit rc.35 first, which would have published someone else's unfinished release under this task. Not chosen: wait until another session finishes it, which the owner did not need.
- Q2 (existing duplicates). Not chosen: also delete the 17 broken links, which are a different defect (skills that no longer exist) and outside this task. Not chosen: delete nothing now, which would have kept every skill listed twice.
- Q3 (what the guard does). Not chosen: warn only, because the agent could still load the wrong copy unnoticed. Not chosen: block all workflow use, because one stale link could stop urgent work and even read-only questions.
- Q4 (the five review findings). Not chosen: one task together with the guard, because the guard would have waited for a much larger plan.
- Q5 (registration). Not chosen: hand over the registration as a patch, because the owner wanted the guard active in new sessions at once.
- Q6 (override wording). Not chosen: the words anywhere in the message except after "not", "never" or "don't", because a word list misses some phrasings and pasted text could trigger it.
- Design choices by the agent. Not chosen: change hooks/phase_gate.py to hold the pause, because that file carries open approval defects the owner asked not to touch. Not chosen: a hard-coded list of skill names, because plugin.json already is that list. Not chosen: delete the copies automatically, because the owner asked to be asked.

## Note for the second task (owner, 2026-11-11)
The owner relayed a request from another agent: "For the second task (the review findings), add this: rework the plan report in skills/codebase-map/ to follow the attached recipe, with plan-r1-v5.html as the reference output and plan-r1.html as the 'before'. Keep the existing stylesheet and diagram style; the recipe lists every change. Do not start until the guard is delivered." The recipe and plan-r1-v5.html are not on this disk yet (searched the repository and Downloads, 2026-11-11). The owner also said they made fixes to codebase-map themselves.

- D10 (by: user, 2026-11-11, Q7): "also for Q7 - A". Keep version 2.8.0-rc.35 and add the guard to its CHANGELOG entry. Not chosen: set rc.36, which needed two files outside the approved list and would have made the rules copy differ. This replaces "release it as rc.36" in ticket T3.
- D11 (by: user, 2026-11-11): the delivery report lists seven behaviours as their own checks: equal bytes still reported, a broken link not reported, the refusal names both ways out, the next call allowed after deletion without a restart, existing hook registrations unchanged, workflow-specify and workflow-execute refused, workflow-doctor still loads. Owner: "List all seven as checks in the delivery report."
- D12 (by: user, 2026-11-11): the earlier recipe and plan-r1-v5.html are superseded: "Do not rework the report from the old recipe or from plan-r1-v5.html; both are superseded." The report rework arrives as a finished patch and is its own task (docs/plans/2026-11-11-report-rework).

- D13 (by: user, 2026-11-11): agreement revision r2 confirmed. I explained the 12 hour limit on the override and the stop of a typed change command and asked for agreement or a change. Owner's answer: "sure fix it". Both points were already built, so nothing further was changed. Not chosen: another time limit or no limit, and letting typed commands through.

- D14 (by: user, 2026-11-11): after the live check the owner said "done and plan r2": the test copy is deleted, and the four remaining defects get a plan. Not chosen: "leave them".

- D15 (by: user, 2026-11-11): agreement to the r2 additions (R7 to R10) and approval of plan r2 (reviews/plan-r2.html), asked in one message: "Yes to both". Tickets T4 and T5. Includes the choice to name the read-only temp folder as a limit in the docs. Not chosen: a write probe on every refused call. No commit, push or version change included.
