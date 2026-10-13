# Synthetic visual review example

This is an illustrative fixture, not the user's application. [review.html](review.html) shows the current two formatting paths and a proposed shared validation change. All tasks remain unexecuted and approval pending. [review.json](review.json) is the editable projection of PLAN/TODO/FINDINGS and the tiny source file.

The bundled report is a saved offline example. A new render has a different generation timestamp. Use a new output filename; do not overwrite an approved report revision. No actual score feature is implemented by the skill package.

## Current fixture usage

The bundled `src/scoreboard.py` web and player entrypoints return `home - away` text for integer inputs. The current fixture has no negative-score validation. The proposed behavior is described in PLAN.md and has not been implemented.
