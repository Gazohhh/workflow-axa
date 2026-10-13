# Synthetic example evidence
E1: src/scoreboard.py, format_score and web_score. Static inspection: web calls the shared formatter; it interpolates integers without negative validation. No runtime test is claimed.
E2: src/scoreboard.py, _legacy_score and player_score. Static inspection: player uses a separate helper, also without negative validation.
E3: The supplied small fixture has these two display entrypoints. Static inspection identifies duplicated formatting; this does not establish all callers in a real repository.
The proposed validation/error path does not exist yet. This report is not implementation evidence.
