"""Digest Claude Code session transcripts for a workflow retrospective.

usage: python -X utf8 -I scripts/digest_sessions.py <project-transcript-dir> <out.md> [--min-user N] [--counts]
Read-only over the transcripts. Emits per-session facts and every human message (truncated), with anything
that looks like a password or token replaced by <redacted> (Hooqd retro: a pasted server password reached the digest).
--counts writes only the per-session numbers (no message text), for baselines that are kept in task records.

Approval messages, process-only turns and denial reasons are heuristics over the message text, labelled as such:
an approval message is a short whole message that approves ("approve r4, no report", "yes", "akkoord"); a
process-only turn is a short human message that only moves the process along (an approval, "ok", "done",
"continue"); a denial reason is the first known phrase in a workflow-axa hook refusal.
"""
import collections, json, pathlib, re, sys

# A value after a secret keyword, and any long token mixing upper case, lower case and digits.
SECRET_AFTER = re.compile(r'(?i)\b(password|passwd|pwd|pw|token|secret|api[_-]?key|credentials?)(\s*[:=]\s*|\s+)(\S+)')
SECRET_TOKEN = re.compile(r'\b(?=\w*[A-Z])(?=\w*[a-z])(?=\w*\d)\w{16,}\b')
SKIP_USER = re.compile(r'^(<local-command|<command-name>|<command-message>|<system-reminder>|<task-notification>|<cross-session|<agent-message|\[Request interrupted|Caveat:)')


# The whole message is an assent, optionally naming what it approves ("approve r4, no report", "Approve both").
# A request after the assent ("go investigate the bug", "yes, change the schema") is substantive, so not counted.
APPROVAL = re.compile(r'^(?:approve[sd]?|approved|yes|ok(?:ay)?|go|ja|akkoord|doe maar|agree[sd]?|lgtm)'
                      r'(?:[\s,.!]+(?:r\d+|both|all|it|that|this|please|now|ahead|go|no (?:html )?report|without (?:the )?report))*'
                      r'[\s.!]*$', re.I)
PROCESS_WORDS = re.compile(r'^(?:ok(?:ay)?|done|continue|go on|yes|sure|ja|next|proceed|you do it)[\s.!]*$', re.I)
DENIAL_REASONS = (
    ('no plan report', 'no plan report'),
    ('found no presentation', 'plan not seen as presented'),
    ('came before the plan', 'answer before presentation'),
    ('current task changed', 'task switch'),
    ('requires a complete read', 'required reads'),
    ('record.py', 'use record.py'),
    ('only part of the owner', 'partial quote'),
    ('quotes ', 'quote not matched'),
    ('install', 'install'),
    ('needs implementation approval', 'no approval'),
)


def denial_reason(text):
    low = text.lower()
    return next((label for phrase, label in DENIAL_REASONS if phrase in low), 'other')


def approval_like(text):
    return bool(APPROVAL.match(text.strip(' *_')))


def process_only(text):
    return approval_like(text) or bool(PROCESS_WORDS.match(text.strip(' *_')))


def redact(text):
    text = SECRET_AFTER.sub(lambda m: m[1] + m[2] + '<redacted>', text)
    return SECRET_TOKEN.sub('<redacted>', text)


def text_of(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return '\n'.join(c.get('text', '') for c in content if isinstance(c, dict) and c.get('type') == 'text')
    return ''


def digest(path):
    s = dict(user=[], skills=[], tools=collections.Counter(), asks=0, ask_qs=[], errors=0, compactions=0,
             first=None, last=None, assistant_turns=0, denied=0, hook_denied=0, host_denied=0,
             approvals=0, process_turns=0, denial_reasons=collections.Counter())
    for line in open(path, encoding='utf8', errors='replace'):
        try:
            rec = json.loads(line)
        except ValueError:
            continue
        if not isinstance(rec, dict):
            continue
        ts = rec.get('timestamp')
        if ts:
            s['first'] = s['first'] or ts
            s['last'] = ts
        if rec.get('type') == 'system' and 'compact' in json.dumps(rec)[:400].lower():
            s['compactions'] += 1
        if rec.get('isSidechain'):
            continue
        if rec.get('type') == 'system' and rec.get('subtype') == 'permission_denied':
            s['host_denied'] += 1  # Separate events may describe an already-counted tool error.
        msg = rec.get('message') or {}
        if not isinstance(msg, dict):
            continue
        content = msg.get('content')
        if rec.get('type') == 'user':
            if isinstance(content, list) and any(isinstance(c, dict) and c.get('type') == 'tool_result' for c in content):
                for c in content:
                    if isinstance(c, dict) and c.get('type') == 'tool_result' and c.get('is_error'):
                        s['errors'] += 1
                        body = json.dumps(c.get('content'))
                        head = body[:300].lower()
                        if 'hook error' in head or 'blocked by hook' in head:
                            s['hook_denied'] += 1  # P1-P3 digest: gate denials were counted as plain errors
                            if 'workflow-axa' in head:
                                s['denial_reasons'][denial_reason(body[:1200])] += 1
                        elif 'denied' in head:
                            s['denied'] += 1
                continue
            t = text_of(content).strip()
            if t and not SKIP_USER.match(t) and not rec.get('isMeta') and not t.startswith('Base directory for this skill:'):
                s['user'].append((ts or '')[:16] + ' ' + redact(re.sub(r'\s+', ' ', t))[:400])
                s['approvals'] += approval_like(t)
                s['process_turns'] += process_only(t)
            elif '<command-name>' in t[:200]:
                m = re.search(r'<command-name>(.*?)</command-name>.*?<command-args>(.*?)</command-args>', t, re.S)
                if m:
                    s['skills'].append(m[1])  # a typed /skill expands without a Skill tool call
                    s['user'].append((ts or '')[:16] + ' [CMD ' + m[1] + '] ' + redact(re.sub(r'\s+', ' ', m[2]))[:300])
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
                    s['ask_qs'] += [redact(q.get('question', ''))[:160] for q in inp.get('questions', [])]
    return s


def write_counts(out, rows):
    """One table row per session: numbers only, no message text, so the result can live in task records."""
    with open(out, 'w', encoding='utf8') as f:
        f.write('Approval messages and process-only turns are heuristics over whole short messages; denials by reason '
                'count workflow-axa hook refusals only (hook denials count every hook).\n\n')
        f.write('| session | start | human messages | approval messages | process-only turns | hook denials | '
                'workflow-axa denials by reason |\n|---|---|---|---|---|---|---|\n')
        for p, s in rows:
            reasons = ', '.join(f'{k} {v}' for k, v in s['denial_reasons'].most_common()) or '-'
            f.write(f"| {p.stem[:8]} | {(s['first'] or '')[:10]} | {len(s['user'])} | {s['approvals']} | "
                    f"{s['process_turns']} | {s['hook_denied']} | {reasons} |\n")


def main():
    src, out = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    min_user = int(sys.argv[sys.argv.index('--min-user') + 1]) if '--min-user' in sys.argv else 0
    rows = []
    for p in sorted(src.glob('*.jsonl'), key=lambda p: p.stat().st_mtime):
        s = digest(p)
        if len(s['user']) >= min_user:
            rows.append((p, s))
    if '--counts' in sys.argv:
        write_counts(out, rows)
        print(out, len(rows), 'sessions (counts only)')
        return
    with open(out, 'w', encoding='utf8') as f:
        f.write(f'# Session digest: {src.name}\n\n{len(rows)} sessions. Human messages truncated to 400 chars.\n\n')
        for p, s in rows:
            top = ', '.join(f'{k}:{v}' for k, v in s['tools'].most_common(8))
            f.write(f"## {p.stem}  ({(s['first'] or '')[:16]} → {(s['last'] or '')[:16]}, {p.stat().st_size // 1024} KB)\n")
            f.write(f"- human messages: {len(s['user'])}; assistant turns: {s['assistant_turns']}; compactions: {s['compactions']}; tool errors: {s['errors']} (denied {s['denied']}); hook denials: {s['hook_denied']}\n")
            f.write(f"- host permission denials: {s['host_denied']} (separate stream events; may overlap tool errors)\n")
            f.write(f"- approval messages: {s['approvals']}; process-only turns: {s['process_turns']}; "
                    f"workflow-axa denials by reason: {dict(s['denial_reasons'])} (heuristics)\n")
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
