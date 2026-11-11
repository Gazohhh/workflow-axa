"""List every stylesheet rule that styles a class, with its full selector, so a copy keeps its context.

usage: python -X utf8 -I class_rules.py <project-root> <class> [<class> ...]
       python -X utf8 -I class_rules.py <project-root> --compare <parent-it-comes-from> <parent-it-goes-into>
       python -X utf8 -I class_rules.py <project-root> --match <tag> <class> [<class> ...]

Reads .css/.scss/.sass/.less files under the root (skipping node_modules, .git and build output). Nested SCSS
selectors are joined with their parents (`&` included). Prints `file:line  selector` for each rule whose
selector names one of the classes, and marks rules that only apply inside an ancestor ("needs context"):
a copy placed outside that ancestor does not get those styles. --compare prints both parents' own declarations
and every rule that styles their children, so a layout difference is visible. --match lists existing elements in markup,
templates and JS strings with exactly that tag and class set (exit 1 when none). Read-only; no installs, no writes.
Exit 0: rules listed; 1: no rule names the classes; 2: bad input.
Limits: a text scan, not a CSS engine. It does not evaluate mixins, @extend, generated class names,
CSS modules, inline styles or rules in other languages; check those by hand.
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

EXTENSIONS = {'.css', '.scss', '.sass', '.less'}
SKIP = {'node_modules', '.git', 'dist', 'build', 'www', '.angular', '.artifacts', 'coverage'}


def strip_comments(text: str) -> str:
    """Blank comments but keep newlines so line numbers stay right."""
    text = re.sub(r'/\*.*?\*/', lambda m: re.sub(r'[^\n]', ' ', m.group()), text, flags=re.S)
    return re.sub(r'(?<![:"\'])//[^\n]*', '', text)


def join(parents: list[str], selector: str) -> list[str]:
    parts = [p.strip() for p in selector.split(',') if p.strip()]
    if not parents:
        return parts
    out = []
    for parent in parents:
        for part in parts:
            out.append(part.replace('&', parent) if '&' in part else f'{parent} {part}')
    return out


def rules(text: str) -> list[tuple[int, list[str], list[str]]]:
    """(line, full selectors, own declarations) for every rule block in a CSS/SCSS text, in file order."""
    stack: list[tuple[list[str] | None, int, list[str]]] = []
    found = []
    start, line = 0, 1
    for i, ch in enumerate(text):
        if ch == '\n':
            line += 1
        if ch not in '{};':
            continue
        head = ' '.join(text[start:i].split())
        if ch == '{':
            first = line - text[start:i].lstrip().count('\n')  # the line where the selector starts
            parents = next((s for s, _, _ in reversed(stack) if s is not None), [])
            selectors = None if head.startswith('@') or not head else join(parents, head)  # @media keeps parents
            stack.append((selectors, first, []))
        else:
            if head and stack:
                stack[-1][2].append(head)  # a declaration of the innermost block
            if ch == '}' and stack:
                selectors, first, declarations = stack.pop()
                if selectors is not None:
                    found.append((first, selectors, declarations))
        start = i + 1
    return sorted(found, key=lambda row: row[0])


def sheets(root: Path):
    for folder, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d not in SKIP)
        for name in sorted(files):
            path = Path(folder, name)
            if path.suffix.lower() in EXTENSIONS:
                try:
                    yield path, strip_comments(path.read_text(encoding='utf-8', errors='replace'))
                except OSError:
                    continue


def compare(root: Path, source: str, target: str) -> int:
    """Layout of the parent an element is copied from versus the parent it goes into."""
    for label, name in (('FROM', source), ('INTO', target)):
        own = re.compile(r'\.' + re.escape(name) + r'(?![\w-])$')
        children = re.compile(r'\.' + re.escape(name) + r'(?![\w-])\S*\s+\S')  # also .title.wide .x
        print(f'== {label} .{name}')
        hits = 0
        for path, text in sheets(root):
            for line, selectors, declarations in rules(text):
                for selector in selectors:
                    kind = 'itself' if own.search(selector) else 'styles children' if children.search(selector) else ''
                    if kind:
                        hits += 1
                        print(f'{path.relative_to(root).as_posix()}:{line}  {selector}  [{kind}]  {"; ".join(declarations)}')
        if not hits:
            print('  no stylesheet rule names this class')
    print('Any layout difference (display, flex direction or alignment, width, line-height, a rule that styles '
          'children) means the copy will not look the same there: it is not a match (ask DESIGN.md rule 4).')
    # Round 8: a tag copied into an <h1> turned bold; neither parent's rules said so.
    print('Text properties pass down from the new parent (font-weight, font-size, color, line-height, letter-spacing), '
          'and browsers make h1-h6, strong, b and th bold by default: compare the tag you place the copy in too, '
          'for every placement you offer.')
    return 0


MARKUP = {'.html', '.htm', '.tsx', '.jsx', '.ts', '.js', '.vue', '.svelte', '.php'}
OPENING = re.compile(r'<([a-zA-Z][\w-]*)\b([^<>]*?)>', re.S)
CLASS_ATTR = re.compile(r'\b(?:class|className)\s*=\s*(["\'])(.*?)\1', re.S)


BINDING = re.compile(r'\[ngClass\]|\[class(?:\.[\w-]+)?\]|\[className\]|(?<![\w-]):class\b|v-bind:class|className=\{|class:[\w-]+=')


def bound_matches(root: Path, tag: str, wanted: set[str]) -> list[tuple[str, str]]:
    """Same-tag elements whose static classes are a subset of `wanted` and that also bind classes, where each
    missing class appears as a quoted string in the code (round 17: Angular adds the chip variant at runtime)."""
    literals: set[str] = set()
    candidates = []
    for folder, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d not in SKIP)
        for name in sorted(files):
            path = Path(folder, name)
            if path.suffix.lower() not in MARKUP:
                continue
            try:
                text = path.read_text(encoding='utf-8', errors='replace')
            except OSError:
                continue
            literals.update(re.findall(r'["\'`]([-\w]+)["\'`]', text))
            for element in OPENING.finditer(text):
                if element.group(1).lower() != tag.lower() or not BINDING.search(element.group(2)):
                    continue
                attr = CLASS_ATTR.search(element.group(2))
                static = set(attr.group(2).split()) if attr and '{' not in attr.group(2) else set()
                if static and static < wanted:
                    where = f'{path.relative_to(root).as_posix()}:{text.count(chr(10), 0, element.start()) + 1}'
                    candidates.append((where, wanted - static))
    return [(where, 'bound: ' + ' '.join(sorted(missing))) for where, missing in candidates if missing <= literals]


def match(root: Path, tag: str, classes: list[str]) -> int:
    """Existing elements with exactly this tag and class set: a copy must keep the source's whole class list."""
    wanted, exact, near = set(classes), [], []
    for folder, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d not in SKIP)
        for name in sorted(files):
            path = Path(folder, name)
            if path.suffix.lower() not in MARKUP:
                continue
            try:
                text = path.read_text(encoding='utf-8', errors='replace')
            except OSError:
                continue
            for element in OPENING.finditer(text):
                if element.group(1).lower() != tag.lower():
                    continue
                attr = CLASS_ATTR.search(element.group(2))
                if not attr or '{' in attr.group(2):
                    continue
                found = set(attr.group(2).split())
                where = f'{path.relative_to(root).as_posix()}:{text.count(chr(10), 0, element.start()) + 1}'
                if found == wanted:
                    exact.append(where)
                elif found & wanted:
                    near.append(f'{where}  <{tag} class="{" ".join(sorted(found))}">')
    for where in exact:
        print(f'MATCH {where}  <{tag} class="{" ".join(classes)}">')
    if exact:
        print('Ignore the lines you added yourself; at least one other match must remain.')
        return 0
    bound = bound_matches(root, tag, wanted)
    for where, extra in bound:
        print(f'BOUND MATCH {where}  static classes plus a class binding; {extra}')
    if bound:
        print('These elements get the remaining classes at runtime (ngClass, [class], :class, className={...}). '
              'Open each location and make sure that the binding really produces exactly this set.')
        return 0
    print(f'NO MATCH: no existing <{tag}> has exactly these classes. A copy keeps the whole class list of the element '
          'it mirrors; a different set is a new combination (ask DESIGN.md rule 4).')
    for line in near[:10]:
        print(f'  same tag, some of the classes: {line}')
    return 1


def main(argv: list[str]) -> int:
    if len(argv) < 3 or not Path(argv[1]).is_dir():
        print(__doc__)
        return 2
    root, classes = Path(argv[1]), argv[2:]
    if classes[:1] == ['--match']:
        if len(classes) < 3 or not re.fullmatch(r'[a-zA-Z][\w-]*', classes[1]) or not all(
                re.fullmatch(r'-?[A-Za-z_][\w-]*', c) for c in classes[2:]):
            print('BLOCKED: --match <tag> <class> [<class> ...], for example --match button btn btn-danger')
            return 2
        return match(root, classes[1], classes[2:])
    comparing = classes[:1] == ['--compare']
    if comparing:
        classes = classes[1:]
    if (comparing and len(classes) != 2) or not classes or not all(re.fullmatch(r'-?[A-Za-z_][\w-]*', c) for c in classes):
        print('BLOCKED: give bare class names, for example sm-chip (with --compare: exactly two parent classes)')
        return 2
    if comparing:
        return compare(root, *classes)
    patterns = {c: re.compile(r'\.' + re.escape(c) + r'(?![\w-])') for c in classes}
    found = 0
    for path, text in sheets(root):
        for line, selectors, _ in rules(text):
            for selector in selectors:
                hits = [c for c, p in patterns.items() if p.search(selector)]
                if not hits:
                    continue
                found += 1
                context = '' if ' ' not in selector.strip() else '  [needs context]'
                print(f'{path.relative_to(root).as_posix()}:{line}  {selector}{context}')
    if not found:
        print('No stylesheet rule names these classes (they may still come from a component, a mixin or generated CSS).')
        return 1
    print('Rules marked [needs context] apply only inside the ancestors in their selector: '
          'place the copy inside the same wrapper, or it is not a match (ask DESIGN.md rule 4).')
    return 0


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.exit(main(sys.argv))
