# Preserve the approved flowchart appearance

The existing browser suite tests geometry and controls. The additional visual tool compares actual pixels from the same stable fixture, so spacing, type size, arrows and mobile presentation cannot change unnoticed.

The tool uses already installed Playwright/Chromium for capture and Pillow for comparison. These are optional maintenance dependencies, not report-generation requirements. It never installs them. Use a controlled browser/OS/font environment; a mismatch is NOT_VERIFIED rather than a false failure or pass. Browser sandboxing stays enabled unless the explicit trusted-container flag is needed.

## Capture then compare

From the candidate package root, supply an existing browser and new output directories:

```powershell
python -X utf8 tools/visual_regression.py capture --browser "C:\Path\To\Chromium\chrome.exe" --output "C:\Dev\report-candidate"
python -X utf8 tools/visual_regression.py compare --baseline "C:\Dev\approved-report-reference" --candidate "C:\Dev\report-candidate" --output "C:\Dev\report-difference"
```

To establish a carry-forward reference, capture the trusted previous package in the **same environment** using `capture --package "C:\Dev\workflow-axa-2.2.1" ...`. This executes that package's renderer; never point it at an untrusted arbitrary checkout. Review the images and their source before adopting a reference. Do not create a reference from the candidate just because comparison failed.

The shipped `visual-baselines/2.2.1/` directory contains four reference captures of the previous package's unchanged synthetic example, based on the already accepted visual design. The maintenance session established them; they are **not** newly obtained screenshot-by-screenshot human approvals. Their manifest records browser, OS, device scale, font-rendering fingerprint and source hashes. They may be incompatible with a Windows or different browser installation; establish and review the team's own baseline there rather than stripping environment checks.

The tool captures the proposed/current/build flow panels on desktop and the proposed panel on mobile at fixed sizes. It waits for visible content, fonts and stable consecutive frames, not networkidle. It crops the review region, excluding changing generation timestamps. It tries direct file navigation offline; a managed-policy fallback loads identical HTML and is disclosed in the manifest. Desktop opener behavior is still a separate check.

## Results and authority

- Compare exit 0: all selected fixture pixels match exactly in the recorded environment.
- Exit 1: pixels or image dimensions changed; inspect generated difference images and fix unintended changes.
- Exit 2: missing/corrupt input, different environment/case coverage or unavailable tooling; no verified comparison.

Inputs are read-only. The tool refuses an existing output path and never creates a missing baseline, updates a reference or changes thresholds. For an intentional design change, present it to the user first, record approval, then adopt a separately captured and reviewed reference while retaining the prior one. Generation or a green test is not approval.

Pixel equality is not semantic correctness, accessibility or comprehension. Check branch meaning, independent actions, build dependencies, readable labels, keyboard controls and the cold-reader explanation as well. Use an application's own design system for its UI; this report theme is not a universal application design.

Official references: [Playwright visual comparisons](https://playwright.dev/docs/test-snapshots) and [page readiness](https://playwright.dev/python/docs/api/class-page#page-wait-for-load-state). The tool uses Python Playwright capture plus exact Pillow comparison, not Node Playwright's toHaveScreenshot assertion.
