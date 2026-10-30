#!/usr/bin/env python3
"""Print bounded static version facts; never execute projects, resolve packages or write reports."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import stat
import sys
from pathlib import Path

MAX_BYTES = 2_000_000
JS_PACKAGES = {
    "react": "react.md", "react-dom": "react.md", "react-router": "react.md",
    "react-router-dom": "react.md", "typescript": "typescript.md", "vite": "vite.md",
    "three": "threejs.md", "pixi.js": "pixijs.md",
    "@angular/core": "angular.md", "@angular/cli": "angular.md",
    "@angular/common": "angular.md", "@angular/router": "angular.md",
    "@angular/forms": "angular.md", "@angular/compiler-cli": "angular.md",
    "@angular/platform-browser": "angular.md", "rxjs": "typescript.md",
    "@ionic/angular": "ionic.md", "@ionic/react": "ionic.md", "@ionic/vue": "ionic.md",
    "@ionic/core": "ionic.md", "@capacitor/core": "capacitor.md",
    "@capacitor/cli": "capacitor.md", "@capacitor/android": "capacitor.md",
    "@capacitor/ios": "capacitor.md", "@capacitor/app": "capacitor.md",
    "@capacitor/keyboard": "capacitor.md", "@capacitor/preferences": "capacitor.md",
}
JS_LOCKS = ("npm-shrinkwrap.json", "package-lock.json", "pnpm-lock.yaml", "yarn.lock", "bun.lock", "bun.lockb")
LIMITS = (
    "Static facts only: declared constraints and lock observations are not installed/runtime versions.",
    "No dependency-range solving, environment/container probing, project execution, network or writes.",
    "Use matching primary documentation and inspect configuration before claiming API compatibility.",
    "Custom manifest locations, linked packages and unsupported formats require explicit inspection.",
)


def relative(value: str) -> Path:
    if not value or "\\" in value or ":" in value or any(c in value for c in "\r\n\0"):
        raise ValueError("Use nonempty relative forward-slash scopes.")
    p = Path(value)
    if p.is_absolute() or ".." in p.parts:
        raise ValueError("Scope escapes the supplied root.")
    return p


class Inputs:
    """Read only named, bounded ordinary files; record hashes without exposing whole manifests."""

    def __init__(self, root: Path):
        self.root = root.resolve(strict=True)
        if not self.root.is_dir():
            raise ValueError("Root must be a directory.")
        self.sources: dict[str, str] = {}
        self.cache: dict[Path, bytes | None] = {}

    def checked(self, path: Path) -> Path:
        if not path.resolve().is_relative_to(self.root):
            raise ValueError("Input escapes the supplied root.")
        for ancestor in (path, *path.parents):
            if ancestor == self.root.parent:
                break
            if ancestor.is_symlink() or (ancestor.exists() and getattr(ancestor.lstat(), "st_file_attributes", 0) & 0x400):
                raise ValueError("Linked/junction input requires manual review: " + str(path))
        return path

    def raw(self, path: Path) -> bytes | None:
        self.checked(path)
        if path in self.cache:
            return self.cache[path]
        if not path.exists():
            self.cache[path] = None
            return None
        info = path.stat()
        if not stat.S_ISREG(info.st_mode) or info.st_size > MAX_BYTES:
            raise ValueError("Input must be an ordinary file of at most 2 MB: " + str(path))
        with path.open("rb") as stream:
            content = stream.read(MAX_BYTES + 1)
        if len(content) > MAX_BYTES:
            raise ValueError("Input grew beyond the read limit.")
        self.sources[path.relative_to(self.root).as_posix()] = hashlib.sha256(content).hexdigest()
        self.cache[path] = content
        return content

    def obj(self, path: Path) -> dict | None:
        raw = self.raw(path)
        if raw is None:
            return None
        data = json.loads(raw.decode("utf-8-sig"))
        if not isinstance(data, dict):
            raise ValueError("Expected a JSON object: " + str(path))
        return data

    def name(self, path: Path) -> str:
        return path.relative_to(self.root).as_posix()


def field(data: dict, name: str) -> dict:
    value = data.get(name, {})
    if not isinstance(value, dict):
        raise ValueError("Expected an object for " + name)
    return value


def specification(value) -> str:
    """Do not echo URLs, credentials or arbitrary metadata as version evidence."""
    if not isinstance(value, str) or not value.strip() or len(value) > 160:
        raise ValueError("Expected a bounded version/constraint string.")
    if re.fullmatch(r"[A-Za-z0-9~^<>=|*.+_ -]+", value):
        return value
    return "[non-version specification; inspect source locally]"


def ancestors(inputs: Inputs, scope: str) -> list[Path]:
    target = inputs.checked(inputs.root / relative(scope))
    directory = target if target.is_dir() or not target.exists() else target.parent
    result = []
    while directory.is_relative_to(inputs.root):
        result.append(directory)
        if directory == inputs.root:
            break
        directory = directory.parent
    return result


def nearest(inputs: Inputs, dirs: list[Path], name: str) -> Path | None:
    for directory in dirs:
        candidate = directory / name
        if inputs.raw(candidate) is not None:
            return candidate
    return None


def npm_version(lock: dict, lock_dir: Path, package_dir: Path, package: str) -> tuple[str | None, str | None]:
    kind = lock.get("lockfileVersion")
    if type(kind) is not int or kind not in (1, 2, 3):
        return None, "Unsupported npm lock schema; resolve with the project's package manager."
    if package_dir != lock_dir and (kind == 1 or package_dir.relative_to(lock_dir).as_posix() not in field(lock, "packages")):
        return None, "Ancestor lock has no entry for this package/workspace; do not borrow its versions."
    if kind == 1:
        row = field(lock, "dependencies").get(package)
    else:
        packages = field(lock, "packages")
        directory = package_dir
        row = None
        while directory.is_relative_to(lock_dir):
            prefix = directory.relative_to(lock_dir).as_posix()
            key = ("" if prefix == "." else prefix + "/") + "node_modules/" + package
            if key in packages:
                row = packages[key]
                break
            if directory == lock_dir:
                break
            directory = directory.parent
    if row is None:
        return None, "No applicable direct lock entry was found."
    if not isinstance(row, dict):
        raise ValueError("Malformed npm package lock entry.")
    if row.get("link") or row.get("name", package) != package:
        return None, "Linked/aliased package needs explicit resolution."
    version = row.get("version")
    if not isinstance(version, str) or not re.fullmatch(r"v?\d+\.\d+\.\d+(?:[-+][A-Za-z0-9.+_-]+)?", version):
        return None, "Lock version is non-registry or unresolved; inspect explicitly."
    return version, None


def js_context(inputs: Inputs, manifest: Path, dirs: list[Path]) -> dict:
    data = inputs.obj(manifest)
    declared = {}
    for group in ("dependencies", "devDependencies", "peerDependencies", "optionalDependencies"):
        for package, constraint in field(data, group).items():
            if package in JS_PACKAGES or package.startswith("@capacitor/"):
                declared.setdefault(package, []).append({"group": group, "constraint": specification(constraint)})
    result = {"ecosystem": "javascript", "manifest": inputs.name(manifest), "packages": [], "warnings": []}
    if "packageManager" in data:
        # Manager+version only, never a URL/custom command.
        value = data["packageManager"]
        result["package_manager"] = value if isinstance(value, str) and re.fullmatch(r"(npm|pnpm|yarn|bun)@[0-9A-Za-z.+_-]+", value) else "[inspect source]"
    result["engine_constraints"] = {k: specification(v) for k, v in field(data, "engines").items() if k in {"node", "npm"}}
    locks = []
    for directory in dirs[dirs.index(manifest.parent):]:
        local = [directory / n for n in JS_LOCKS if inputs.raw(directory / n) is not None]
        if local:
            locks = local
            break
    result["lockfiles"] = [inputs.name(p) for p in locks]
    lock = None
    if len(locks) > 1:
        result["warnings"].append("Multiple lockfiles at the same scope; choose the authoritative manager explicitly.")
    elif not locks:
        result["warnings"].append("No lockfile found on the scope's ancestor path; resolved versions are unknown.")
    elif locks[0].name in {"npm-shrinkwrap.json", "package-lock.json"}:
        declared_manager = result.get("package_manager", "")
        if declared_manager and not declared_manager.startswith("npm@"):
            result["warnings"].append("Declared package manager conflicts with the npm lock; no authoritative resolution selected.")
        else:
            lock = inputs.obj(locks[0])
    else:
        result["warnings"].append("This helper does not parse pnpm/yarn/bun locks; use a compatible read-only resolver or inspect them.")
    for package, declarations in sorted(declared.items()):
        row = {"name": package, "declared": declarations, "locked": None, "module": JS_PACKAGES.get(package, "capacitor.md")}
        if any(d["constraint"].startswith("[") for d in declarations):
            row["limit"] = "Non-version/alias/local declaration requires explicit resolution."
        elif lock is not None:
            row["locked"], problem = npm_version(lock, locks[0].parent, manifest.parent, package)
            if problem:
                row["limit"] = problem
        result["packages"].append(row)
    result["configuration_sources"] = []
    for name in ("angular.json", "ionic.config.json", "capacitor.config.ts", "capacitor.config.js", "capacitor.config.json"):
        config = nearest(inputs, dirs, name)
        if config is not None:
            result["configuration_sources"].append(inputs.name(config))
    result["configuration_evaluated"] = False
    result["constraint_compatibility"] = "NOT_CHECKED: no npm semver or peer-dependency solver is run."
    return result


def composer_context(inputs: Inputs, manifest: Path) -> dict:
    data = inputs.obj(manifest)
    requirements = {}
    for group in ("require", "require-dev"):
        for package, constraint in field(data, group).items():
            if package == "php" or package == "laravel/framework" or package.startswith(("illuminate/", "ext-")):
                requirements.setdefault(package, []).append({"group": group, "constraint": specification(constraint)})
    config = field(data, "config")
    platform = field(config, "platform")
    result = {"ecosystem": "php", "manifest": inputs.name(manifest), "requirements": requirements,
              "platform_emulation": {k: (v if type(v) is bool else specification(v)) for k, v in platform.items() if k == "php" or k.startswith("ext-")},
              "packages": [], "warnings": [], "modules": ["php.md"],
              "constraint_compatibility": "NOT_CHECKED: Composer ranges, replacements and runtime compatibility require review."}
    lockpath = manifest.parent / "composer.lock"
    lock = inputs.obj(lockpath)
    result["lockfile"] = inputs.name(lockpath) if lock is not None else None
    if lock is None:
        result["warnings"].append("No corresponding composer.lock; resolved dependency versions are unknown.")
    else:
        for group in ("packages", "packages-dev"):
            rows = lock.get(group, [])
            if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
                raise ValueError("Malformed Composer lock package list.")
            for row in rows:
                name = row.get("name")
                if isinstance(name, str) and (name == "laravel/framework" or name.startswith("illuminate/")):
                    result["packages"].append({"name": name, "locked": specification(row.get("version")), "group": group})
        for key in ("platform", "platform-dev", "platform-overrides"):
            values = lock.get(key, {})
            # Older/generated locks may serialise an empty PHP map as an empty JSON array.
            if values == []:
                values = {}
            if not isinstance(values, dict):
                raise ValueError("Malformed Composer lock platform map.")
            result["lock_" + key] = {k: (v if type(v) is bool else specification(v)) for k, v in values.items() if k == "php" or k.startswith("ext-")}
        if lock.get("aliases"):
            result["warnings"].append("Composer aliases exist; inspect alias/replacement semantics before selecting version-specific APIs.")
    if any(k == "laravel/framework" or k.startswith("illuminate/") for k in requirements) or result["packages"]:
        result["modules"].append("laravel.md")
    result["application_structure"] = "NOT_INFERRED: inspect bootstrap/providers/middleware; an upgrade may preserve an older layout."
    result["runtime"] = "NOT_OBSERVED: config.platform and lock platform fields are not the executing PHP/extension versions."
    return result


def unity_context(inputs: Inputs, editor_file: Path) -> dict:
    text = inputs.raw(editor_file).decode("utf-8-sig")
    match = re.search(r"^m_EditorVersion:\s*(\S+)\s*$", text, re.M)
    result = {"ecosystem": "unity", "manifest": inputs.name(editor_file), "editor_configured": specification(match[1]) if match else None,
              "packages": [], "modules": ["unity.md"], "warnings": [],
              "runtime": "NOT_OBSERVED: Editor/backend/language support and actual build environment still need verification."}
    base = editor_file.parent.parent
    manifest = inputs.obj(base / "Packages/manifest.json")
    lock = inputs.obj(base / "Packages/packages-lock.json")
    if manifest is not None:
        resolved = field(lock, "dependencies") if lock is not None else {}
        for name, constraint in sorted(field(manifest, "dependencies").items()):
            if name.startswith("com.unity.render-pipelines."):
                row = resolved.get(name, {})
                if not isinstance(row, dict):
                    raise ValueError("Malformed Unity package lock entry.")
                result["packages"].append({"name": name, "declared": specification(constraint), "locked": specification(row["version"]) if "version" in row else None})
    return result


def inspect_versions(root: Path, scopes: list[str]) -> dict:
    if not scopes or len(scopes) > 64:
        raise ValueError("Supply 1–64 bounded scopes; no recursive repository crawl.")
    inputs = Inputs(root)
    contexts, seen = [], set()
    for scope in sorted(set(scopes)):
        dirs = ancestors(inputs, scope)
        for name, handler in (("package.json", js_context), ("composer.json", composer_context), ("ProjectSettings/ProjectVersion.txt", unity_context)):
            manifest = nearest(inputs, dirs, name)
            if manifest is not None and manifest not in seen:
                seen.add(manifest)
                context = handler(inputs, manifest, dirs) if name == "package.json" else handler(inputs, manifest)
                contexts.append(context)
        # Rust/TOML parsing is deliberately not guessed on Python 3.10; preserve exact source identity.
        cargo = nearest(inputs, dirs, "Cargo.toml")
        if cargo is not None and cargo not in seen:
            seen.add(cargo)
            refs = [cargo]
            for name in ("Cargo.lock", "rust-toolchain.toml", "rust-toolchain"):
                p = nearest(inputs, dirs, name)
                if p is not None:
                    refs.append(p)
            contexts.append({"ecosystem": "rust", "manifest": inputs.name(cargo), "sources": [inputs.name(p) for p in refs],
                             "modules": ["rust.md"], "versions": "NOT_PARSED: inspect edition, rust-version, toolchain, workspace inheritance and target/features with a compatible reader."})
    return {"schema_version": 1, "state": "REVIEW_REQUIRED", "root": str(inputs.root), "scopes": sorted(set(scopes)),
            "contexts": contexts, "sources": dict(sorted(inputs.sources.items())), "limits": list(LIMITS),
            "runtime_verified": False, "compatibility_verified": False, "implementation_approved": False}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--scope", required=True, action="append")
    args = parser.parse_args(argv)
    try:
        result = inspect_versions(args.root.expanduser(), args.scope)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    except (OSError, UnicodeError, ValueError, TypeError, RecursionError) as exc:
        print(json.dumps({"state": "BLOCKED", "reason": str(exc), "compatibility_verified": False}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
