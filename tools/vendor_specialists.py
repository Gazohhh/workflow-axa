"""Build the vendored Matt Pocock skills (skills/<name>/) from pinned upstream copies plus local adaptations.

usage: python -X utf8 -I vendor_specialists.py <upstream-root> <package-root>
Re-runnable: refreshes the upstream part and keeps each SKILL.md's own "workflow-axa adaptation" section.
"""
import hashlib, json, pathlib, re, sys

COMMIT = '4ae2317ddb22b046e26455e4f9c9b3aaaf62212d'
SPECIALISTS = {
    'grilling': ('skills/productivity/grilling', ['SKILL.md']),
    'tdd': ('skills/engineering/tdd', ['SKILL.md', 'tests.md', 'mocking.md']),
    'code-review': ('skills/engineering/code-review', ['SKILL.md']),
    'writing-for-agents': ('skills/productivity/writing-for-agents', ['SKILL.md', 'SKILL-MECHANICS.md']),
    'codebase-design': ('skills/engineering/codebase-design', ['SKILL.md', 'DEEPENING.md', 'DESIGN-IT-TWICE.md']),
    'domain-modeling': ('skills/engineering/domain-modeling', ['SKILL.md', 'GLOSSARY-FORMAT.md', 'ADR-FORMAT.md']),
    'implement-spec': ('skills/engineering/implement-spec', ['SKILL.md']),
    'retro': ('skills/engineering/retro', ['SKILL.md']),
}

MARK = '\n---\n\n## workflow-axa adaptation\n'



def split_front(text):
    m = re.match(r'\A---\n(.*?)\n---\n', text, re.S)
    meta = dict(re.findall(r'^([\w-]+):\s*(.*)$', m[1], re.M)) if m else {}
    return meta, (text[m.end():] if m else text).lstrip('\n')


def main():
    up, pkg = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    license_text = (up / 'LICENSE').read_bytes()
    rows = []
    for name, (src, files) in SPECIALISTS.items():
        d = pkg / 'skills' / name
        (d / 'agents').mkdir(parents=True, exist_ok=True)
        (d / 'LICENSE').write_bytes(license_text)
        for f in files:
            raw = (up / src / f).read_bytes()
            rows.append([name, f'{src}/{f}', hashlib.sha256(raw).hexdigest()[:16], '—'])
            text = raw.decode('utf8').replace('\r\n', '\n')
            if f != 'SKILL.md':
                (d / f).write_text(text, encoding='utf8', newline='\n')
                continue
            meta, body = split_front(text)
            desc = meta.get('description', '').strip().strip('"')
            front = f'---\nname: {name}\ndescription: {json.dumps(desc)}\n'
            if meta.get('disable-model-invocation') == 'true':
                front += 'disable-model-invocation: true\n'
            front += '---\n\n'
            head = (f'> Bundled with workflow-axa from [mattpocock/skills](https://github.com/mattpocock/skills) `{src}/SKILL.md` '
                    f'at `{COMMIT[:7]}`, MIT ([LICENSE](LICENSE)). The upstream text below is unchanged; the '
                    '**workflow-axa adaptation** at the end overrides it where they conflict.\n\n')
            old = (d / 'SKILL.md').read_text(encoding='utf8') if (d / 'SKILL.md').exists() else ''
            # The adaptation section lives in the skill file itself; regeneration keeps it.
            tail = old[old.index(MARK):] if MARK in old else MARK + '\n- None yet.\n'
            kept = body.rstrip('\n') + '\n'
            rows[-1][3] = hashlib.sha256(kept.encode('utf8')).hexdigest()[:16]
            (d / 'SKILL.md').write_text(front + head + kept + tail, encoding='utf8', newline='\n')
            short = desc.split('. ')[0].rstrip('.')[:110]
            (d / 'agents/openai.yaml').write_text(
                f'interface:\n  display_name: {json.dumps(name)}\n  short_description: {json.dumps(short)}\n',
                encoding='utf8', newline='\n')
    table = '\n'.join(f'| {n} | `{p}` | `{h}` | {"`" + b + "`" if b != "—" else b} |' for n, p, h, b in rows)
    names = ', '.join(f'`{n}`' for n in SPECIALISTS)
    (pkg / 'VENDORED-SKILLS.md').write_text(f"""# Vendored skills

Eight skills in this package are copies of Matt Pocock's skills: {names}. They are separate skills like the others (plugin names `workflow-axa:<name>`). The workflow phases load them from their sibling folders, so an upstream change, a removed skill or a same-named skill installed elsewhere can't change the workflow. Each `SKILL.md` keeps the upstream text and ends with a **workflow-axa adaptation** section that overrides it where they conflict; supporting files are unchanged upstream copies.

Source: [mattpocock/skills](https://github.com/mattpocock/skills) at commit `{COMMIT}`, MIT license; each skill folder carries its own `LICENSE` copy. Keep it with the files.

| Skill | Upstream file | SHA-256 (first 16) of the upstream file | SHA-256 (first 16) of the unchanged upstream text inside our SKILL.md |
|---|---|---|---|
{table}

## Updating from upstream

1. Fetch the new upstream files into a scratch folder outside the package.
2. Compare each file's SHA-256 with the table. Unchanged: nothing to do.
3. For a changed file, read the upstream diff and decide with the maintainer whether to take it. Re-check each adaptation section.
4. Regenerate with `python -X utf8 -I tools/vendor_specialists.py <upstream-root> .`, update the commit, then run `tools/validate.py` and the tests.

Never take an upstream change unread: these files steer the agent.
""", encoding='utf8', newline='\n')
    print('vendored', len(rows), 'files')


if __name__ == '__main__':
    main()
