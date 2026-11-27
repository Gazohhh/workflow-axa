# Decisions

- D1 (2026-11-27, by: user): agreement 1 agreed. The owner answered "Agree" to the agreement question in this thread (question tool). Status: settled.
- D2 (2026-11-27, by: agent): agent-marked messages are ignored completely, pauses included. Reason: the request says marked messages are not the owner's; the owner can still stop the work. Shown as an assumption in agreement 1. Status: settled with D1.
- D3 (2026-11-27, by: agent): the open_items warning reads only the template states in progress, implemented and partial. Reason: older tasks say "Implementation: complete" and would warn for no reason (FINDINGS E8). Status: settled with D1.
- D4 (2026-11-27, by: agent): proposal option (c), never narrowing on a question, is not taken. Reason: the brief keeps "only the tests?" as a narrowing. Status: settled.
- D5 (2026-11-27, by: agent): workflow-specify step 5 documents the `run: <exact command>` operation, because that step today says an offer never lists a check. Status: proposed in the offer.

- D6 (2026-11-27, by: user): offer #1 (cb12000e32d57753) approved. The owner answered "Approve from this summary" to the one question in this thread (question tool). Status: settled.

- D7 (2026-11-27, by: user): after the delivery the owner answered "yes do it" to "whether to commit and merge this branch, and whether to restore ARTIFACTS.md". That plain answer approves no protected action, so offer #2 (1ac1ca1101648226) listed git add, git commit, git push to origin main and the global_policy.py --apply run; the owner answered "Approve from this summary (Recommended)" (question tool). Status: settled.

- D8 (2026-11-27, by: agent): release version 2.13.0, a minor version (PLAN "Revision 2"). Shown in offer #3; the owner could change it. Status: settled with D9.
- D9 (2026-11-27, by: user): offer #3 (05609ef11b62ddc1, release 2.13.0 and install) approved: the owner answered "Approve from this summary (Recommended)" (question tool), after asking "make a new release if you did not already and install the new plugin." Status: settled.
