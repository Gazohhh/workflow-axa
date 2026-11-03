"""Digest Claude Code session transcripts for a workflow retrospective.

usage: python -X utf8 -I scripts/digest_sessions.py <project-transcript-dir> <out.md> [--min-user N]
Read-only over the transcripts. Emits per-session facts and every human message (truncated).
"""
import collections, json, pathlib, re, sys

SKIP_USER = re.compile(r'^(<local-command|<command-name>|<system-reminder>|<task-notification>|<cross-session|<agent-message|\[Request interrupted|Caveat:)')


def text_of(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return '\n'.join(c.get('text', '') for c in content if isinstance(c, dict) and c.get('type') == 'text')
    return ''


def digest(path):
    s = dict(user=[], skills=[], tools=collections.Counter(), asks=0, ask_qs=[], errors=0, compactions=0,
             first=None, last=None, assistant_turns=0, denied=0)
    for line in open(path, encoding='utf8', errors='replace'):
        try:
            rec = json.loads(line)
        except ValueError:
            continue
        ts = rec.get('timestamp')
        if ts:
            s['first'] = s['first'] or ts
            s['last'] = ts
        if rec.get('type') == 'system' and 'compact' in json.dumps(rec)[:400].lower():
            s['compactions'] += 1
        if rec.get('isSidechain'):
            continue
        msg = rec.get('message') or {}
        content = msg.get('content')
        if rec.get('type') == 'user':
            if isinstance(content, list) and any(isinstance(c, dict) and c.get('type') == 'tool_result' for c in content):
                for c in content:
                    if isinstance(c, dict) and c.get('type') == 'tool_result' and c.get('is_error'):
                        s['errors'] += 1
                        if 'denied' in json.dumps(c.get('content'))[:300].lower():
                            s['denied'] += 1
                continue
            t = text_of(content).strip()
            if t and not SKIP_USER.match(t) and not rec.get('isMeta'):
                s['user'].append((ts or '')[:16] + ' ' + re.sub(r'\s+', ' ', t)[:400])
            elif t.startswith('<command-name>'):
                m = re.search(r'<command-name>(.*?)</command-name>.*?<command-args>(.*?)</command-args>', t, re.S)
                if m:
                    s['user'].append((ts or '')[:16] + ' [CMD ' + m[1] + '] ' + re.sub(r'\s+', ' ', m[2])[:300])
        elif rec.get('type') == 'assistant' and isinstance(content, list):
            s['assistant_turns'] += 1
            for c in content:
                if c.get('type') != 'tool_use':
                    continue
                name, inp = c.get('name'), c.get('input', {})
                s['tools'][name] += 1
                if name == 'Skill':
                    s['skills'].append(inp.get('skill'))
                if name == 'AskUserQuestion':
                    s['asks'] += 1
                    s['ask_qs'] += [q.get('question', '')[:160] for q in inp.get('questions', [])]
    return s


def main():
    src, out = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    min_user = int(sys.argv[sys.argv.index('--min-user') + 1]) if '--min-user' in sys.argv else 0
    rows = []
    for p in sorted(src.glob('*.jsonl'), key=lambda p: p.stat().st_mtime):
        s = digest(p)
        if len(s['user']) >= min_user:
            rows.append((p, s))
    with open(out, 'w', encoding='utf8') as f:
        f.write(f'# Session digest: {src.name}\n\n{len(rows)} sessions. Human messages truncated to 400 chars.\n\n')
        for p, s in rows:
            top = ', '.join(f'{k}:{v}' for k, v in s['tools'].most_common(8))
            f.write(f"## {p.stem}  ({(s['first'] or '')[:16]} → {(s['last'] or '')[:16]}, {p.stat().st_size // 1024} KB)\n")
            f.write(f"- human messages: {len(s['user'])}; assistant turns: {s['assistant_turns']}; compactions: {s['compactions']}; tool errors: {s['errors']} (denied {s['denied']})\n")
            f.write(f"- skills: {s['skills']}\n- AskUserQuestion calls: {s['asks']}\n- tools: {top}\n")
            for q in s['ask_qs'][:12]:
                f.write(f'  - Q: {q}\n')
            f.write('\n')
            for u in s['user']:
                f.write(f'  > {u}\n')
            f.write('\n')
    print(out, sum(len(s['user']) for _, s in rows), 'human messages')


if __name__ == '__main__':
    main()
