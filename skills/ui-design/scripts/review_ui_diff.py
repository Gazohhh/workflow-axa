#!/usr/bin/env python3
"""Read-only unified-diff triage. Cues require review; no result grants design authority."""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath
from typing import TextIO

MAX_BYTES = 5 * 1024 * 1024
MAX_CHANGED_LINES = 100_000
HUNK = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@(?:.*)$")
STYLE_SUFFIXES = {".css", ".scss", ".sass", ".less", ".styl", ".uss"}
VISUAL_SUFFIXES = {".svg", ".png", ".jpg", ".jpeg", ".webp", ".gif", ".ico", ".avif", ".ttf", ".woff", ".woff2", ".otf", ".mat", ".shader", ".shadergraph", ".uxml", ".unity", ".prefab"}
# These cues include legitimate APIs. Only the recorded task determines authority.
PATTERNS = (
    ("inline-or-runtime-style", r"\bstyle\s*=|\.style\b|cssText\b|setProperty\s*\(|insertRule\s*\(|adoptedStyleSheets\b|CSSStyleSheet\b|setAttribute\s*\(\s*['\"]style['\"]"),
    ("style-injection-or-css-in-js", r"<\s*style\b|createElement\s*\(\s*['\"]style['\"]|\bstyled\s*[.(]|\b(?:css|keyframes)\s*`|styled-components|@emotion/|StyleSheet\.create|makeStyles\s*\("),
    ("classes-or-utility-composition", r"\b(?:className|class|classList)\s*(?:=|[.{:])|\b(?:clsx|classNames|twMerge|cva)\s*\("),
    ("visual-prop-or-token", r"\b(?:sx|css|variant|color|colour|size|radius|rounded|shadow|spacing|padding|margin|gap|theme|fontSize|background|bg|opacity|transition|animation)\s*(?:=|:)|--[\w-]+\s*:|ThemeProvider\b"),
    ("style-import-or-visual-library", r"\.(?:css|scss|sass|less|styl|uss)(?:['\"?]|$)|tailwind|bootstrap|@mui/|@chakra-ui/|@emotion/|styled-components|lucide|heroicons|@radix-ui/"),
    ("rendered-or-native-appearance", r"<\s*(?:svg|path|rect|circle|ellipse|polygon|polyline)\b|\b(?:fill|stroke)\s*=|\b(?:fillStyle|strokeStyle|fillRect|drawImage|beginFill|lineStyle|setTint|setStyle|SetColor|SetFloat|MaterialPropertyBlock|VisualElement|RectTransform|backgroundColor)\b|\.material\b|android:(?:background|tint|textColor)|\.(?:foregroundStyle|background|padding|cornerRadius|font)\s*\("),
    ("markup-or-control-structure", r"<\s*/?\s*(?:[A-Za-z][\w.:\-]*)(?:\s|/?>)|createElement\s*\("),
)
COMPILED = [(code, re.compile(pattern, re.I)) for code, pattern in PATTERNS]
LIMITS = [
    "Review cues are not violations, approval, policy compliance or release readiness.",
    "Only the supplied diff is inspected; omitted untracked/binary content and source context are not recovered.",
    "Dynamic styling, arbitrary component props and visual/interaction effects require manual/runtime review.",
    "No path, test folder or report filename is automatically exempt; check the actual scoped authority.",
]


@dataclass
class Patch:
    label: str
    old_path: str | None = None
    new_path: str | None = None
    lines: list[tuple[str, int, str]] = field(default_factory=list)
    opaque: bool = False
    old_header: bool = False
    has_headers: bool = False

    @property
    def path(self) -> str:
        return self.new_path or self.old_path or self.label


def path_from_header(text: str) -> str | None:
    value = text.split("\t", 1)[0].strip()
    if value == "/dev/null":
        return None
    if value.startswith('"'):
        try:
            value = json.loads(value)
        except (ValueError, TypeError) as exc:
            raise ValueError("Unsupported quoted path encoding; inspect the original patch manually.") from exc
    if not isinstance(value, str) or not value or any(ord(c) < 32 for c in value):
        raise ValueError("Empty or control-character path in diff.")
    if value.startswith(("a/", "b/")):
        value = value[2:]
    # These paths are never opened. Reject odd paths to avoid misleading evidence labels.
    p = PurePosixPath(value)
    if not value or p.is_absolute() or ".." in p.parts or "\\" in value or re.match(r"^[A-Za-z]:", value):
        raise ValueError("Unsupported path; supply a normal repository-relative patch.")
    return value


def parse_diff(text: str) -> list[Patch]:
    if not text.strip():
        return []
    if "\x00" in text:
        raise ValueError("NUL data is not a supported text diff.")
    patches: list[Patch] = []
    current: Patch | None = None
    old_remaining = new_remaining = 0
    old_line = new_line = 0
    active_hunk = False
    seen_changes = 0
    for line in text.splitlines():
        if active_hunk and (old_remaining or new_remaining):
            if line == "\\ No newline at end of file":
                continue
            prefix = line[:1]
            if prefix not in {" ", "+", "-"}:
                raise ValueError("Truncated/malformed hunk; diff coverage is not verified.")
            assert current is not None
            if prefix in {" ", "-"}:
                if old_remaining <= 0:
                    raise ValueError("Old hunk length mismatch.")
                old_remaining -= 1
            if prefix in {" ", "+"}:
                if new_remaining <= 0:
                    raise ValueError("New hunk length mismatch.")
                new_remaining -= 1
            if prefix != " ":
                current.lines.append(("added" if prefix == "+" else "removed", new_line if prefix == "+" else old_line, line[1:]))
                seen_changes += 1
                if seen_changes > MAX_CHANGED_LINES:
                    raise ValueError("Diff too large; review bounded attributed patches instead.")
            if prefix in {" ", "-"}:
                old_line += 1
            if prefix in {" ", "+"}:
                new_line += 1
            continue
        active_hunk = False
        if line.startswith(("diff --cc ", "diff --combined ", "@@@")):
            raise ValueError("Combined diffs are unsupported; supply an ordinary unified diff.")
        if line.startswith("diff --git "):
            current = Patch(label=line[len("diff --git "):])
            patches.append(current)
            continue
        if line.startswith("--- "):
            if current is None or current.has_headers:
                current = Patch(label="unified file")
                patches.append(current)
            if current.old_header:
                raise ValueError("Repeated old-file header.")
            current.old_path = path_from_header(line[4:])
            current.old_header = True
            continue
        if line.startswith("+++ "):
            if current is None or not current.old_header or current.has_headers:
                raise ValueError("New file header without a matching old header.")
            current.new_path = path_from_header(line[4:])
            if current.old_path is None and current.new_path is None:
                raise ValueError("Both file paths are /dev/null.")
            current.has_headers = True
            continue
        match = HUNK.fullmatch(line)
        if match:
            if current is None or not current.has_headers:
                raise ValueError("Hunk without complete file headers.")
            old_line, new_line = int(match[1]), int(match[3])
            old_remaining = int(match[2]) if match[2] is not None else 1
            new_remaining = int(match[4]) if match[4] is not None else 1
            active_hunk = True
            continue
        if line == "\\ No newline at end of file" or not line:
            continue
        if current is not None and line.startswith(("index ", "old mode ", "new mode ", "new file mode ", "deleted file mode ", "similarity index ", "dissimilarity index ", "rename from ", "rename to ", "copy from ", "copy to ")):
            if not line.startswith("index "):
                current.opaque = True
            continue
        if current is not None and (line.startswith("Binary files ") or line == "GIT binary patch"):
            current.opaque = True
            if line == "GIT binary patch":
                raise ValueError("Encoded binary patch unsupported; provide a text diff plus binary-change inventory.")
            continue
        raise ValueError("Unsupported diff text; no complete triage result is available.")
    if old_remaining or new_remaining:
        raise ValueError("Truncated hunk; not all declared lines were supplied.")
    if not patches:
        raise ValueError("No supported file diff found.")
    for patch in patches:
        if not patch.has_headers and not patch.opaque:
            raise ValueError("Incomplete file diff headers.")
    return patches


def review(text: str) -> dict:
    if len(text.encode("utf-8")) > MAX_BYTES:
        raise ValueError("Diff exceeds 5 MiB; provide bounded patches without dropping coverage.")
    patches = parse_diff(text)
    results = []
    any_cue = False
    for patch in patches:
        cues: dict[str, dict[str, list[int]]] = {}
        def add(code: str, side: str | None = None, number: int | None = None) -> None:
            cue = cues.setdefault(code, {"added_lines": [], "removed_lines": []})
            if side is not None and number is not None:
                cue[side + "_lines"].append(number)
        paths = [p for p in (patch.old_path, patch.new_path) if p]
        suffixes = {PurePosixPath(p).suffix.lower() for p in paths}
        if suffixes & STYLE_SUFFIXES:
            add("stylesheet-change")
        if suffixes & VISUAL_SUFFIXES:
            add("visual-asset-or-renderer-file")
        if patch.opaque or not patch.lines:
            add("nontext-or-file-operation-needs-review")
        for side, number, content in patch.lines:
            for code, pattern in COMPILED:
                if pattern.search(content):
                    add(code, side, number)
        any_cue |= bool(cues)
        results.append({"path": patch.path, "old_path": patch.old_path, "new_path": patch.new_path,
                        "changed_lines": len(patch.lines),
                        "cues": [{"category": code, **locations} for code, locations in sorted(cues.items())]})
    return {"schema_version": 1,
            "status": "review-required" if any_cue else "no-patterns-detected" if patches else "no-changes",
            "policy_decision": "not-evaluated", "design_accepted": False,
            "implementation_authorized": False, "files": results, "limitations": LIMITS}


def read_input(path: Path | None, stream: TextIO) -> str:
    if path is None:
        text = stream.read(MAX_BYTES + 1)
        if len(text.encode("utf-8")) > MAX_BYTES:
            raise ValueError("Diff exceeds 5 MiB.")
        return text
    if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_BYTES:
        raise ValueError("Supply an existing non-linked UTF-8 diff file no larger than 5 MiB.")
    with path.open("rb") as handle:
        raw = handle.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ValueError("Diff exceeds 5 MiB.")
    return raw.decode("utf-8-sig")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--diff", type=Path, help="Read an existing UTF-8 diff instead of stdin; no output files.")
    args = parser.parse_args(argv)
    try:
        result = review(read_input(args.diff, sys.stdin))
    except (OSError, UnicodeError, ValueError) as exc:
        result = {"schema_version": 1, "status": "invalid-input", "policy_decision": "not-evaluated",
                  "error": str(exc), "limitations": LIMITS}
        print(json.dumps(result, ensure_ascii=True, indent=2))
        return 2
    print(json.dumps(result, ensure_ascii=True, indent=2))
    return 1 if result["status"] == "review-required" else 0


if __name__ == "__main__":
    raise SystemExit(main())
