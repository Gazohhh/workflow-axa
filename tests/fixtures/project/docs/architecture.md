# Score display

The two public entrypoints are src/web.py and src/player.py. The web path calls src/labels.py. The player currently has a separate legacy formatter with the same output, so changes to the common formatter do not automatically reach the player.

Ordinary non-negative integer scores display as `home - away`. The project has no explicit negative-score validation yet. Update this description when that behavior or ownership changes. No external service or package is involved.
