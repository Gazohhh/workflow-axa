"""Source-backed, inert HTML/CSS fragment previews for the existing UI review.

Only an existing DOM subtree and existing compiled CSS are displayed. No framework
runtime, application network calls, generated UI classes or designer approvals.
"""
from __future__ import annotations

import html
import re
from html.parser import HTMLParser
from pathlib import Path

MAX_HTML = 250_000
MAX_CSS = 500_000
MAX_PREVIEWS = 6
VOID = {'br', 'hr', 'input', 'meta', 'source', 'wbr', 'img', 'link', 'base', 'embed'}
ALLOWED = {'div','span','p','strong','em','b','i','small','label','button','input',
           'section','article','header','footer','main','nav','aside','ul','ol','li',
           'h1','h2','h3','h4','h5','h6','table','thead','tbody','tr','td','th','a'}
SELECTOR = re.compile(r'^(?:[a-z][a-z0-9-]*)?(?:\.[a-zA-Z_][\w-]*|#[a-zA-Z_][\w-]*)$')
SAFE_ATTR = {'class', 'id', 'role', 'type', 'value', 'placeholder', 'title',
             'disabled', 'checked', 'selected', 'readonly', 'name', 'for', 'tabindex'}


def tag_allowed(tag: str) -> bool:
    return tag in ALLOWED or bool(re.fullmatch(r'(?:ion|app)-[a-z][a-z0-9-]*', tag))


class Fragment(HTMLParser):
    """Select one element by tag/class/id; copy only inert elements and attributes."""
    def __init__(self, selector: str):
        super().__init__(convert_charrefs=True)
        self.selector = selector
        self.depth = 0
        self.started = False
        self.done = False
        self.parts: list[str] = []
        self.stack: list[bool] = []
        self.blocked = 0

    def matches(self, tag: str, attrs: dict[str, str]) -> bool:
        selector = self.selector
        name = selector.split('.', 1)[0].split('#', 1)[0]
        if name and tag != name:
            return False
        if '#' in selector:
            return attrs.get('id') == selector.split('#', 1)[1]
        return selector.rsplit('.', 1)[1] in attrs.get('class', '').split()

    def handle_starttag(self, tag, attrs):
        if self.done:
            return
        values = dict(attrs)
        if not self.started:
            if not self.matches(tag, values):
                return
            self.started = True
        if self.blocked or tag in {'script','style','iframe','object','embed','form','template',
                                   'svg','math','video','audio','img','link','base'}:
            self.blocked += 1 if tag not in VOID else 0
            self.stack.append(False)
            self.depth += 1
            if tag in VOID:
                self.handle_endtag(tag)
            return
        permitted = tag_allowed(tag)
        self.stack.append(permitted)
        self.depth += 1
        if permitted:
            safe = []
            for key, value in attrs:
                if value is None and key not in {'disabled', 'checked', 'selected', 'readonly'}:
                    continue
                if key in SAFE_ATTR or key.startswith('aria-'):
                    if key == 'type' and value not in {'text','number','checkbox','radio','button','submit','email','password'}:
                        continue
                    safe.append(f' {key}="{html.escape(value if value is not None else key, quote=True)}"')
            self.parts.append(f'<{tag}{"".join(safe)}>')
        if tag in VOID:
            self.handle_endtag(tag)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if not self.started or self.done or not self.stack:
            return
        allowed = self.stack.pop()
        self.depth -= 1
        if self.blocked and tag not in VOID:
            self.blocked -= 1
        elif allowed and tag not in VOID:
            self.parts.append(f'</{tag}>')
        if self.depth <= 0:
            self.done = True

    def handle_data(self, data):
        if self.started and not self.done and not self.blocked:
            self.parts.append(html.escape(data))


def extract_fragment(source: str, selector: str) -> str:
    parser = Fragment(selector)
    parser.feed(source)
    parser.close()
    if not parser.done or not parser.parts:
        raise ValueError(f'Quick preview cannot find a complete element at {selector!r}')
    result = ''.join(parser.parts)
    if len(result.encode('utf-8')) > 100_000:
        raise ValueError('Quick preview fragment is too large; select a smaller element')
    return result


def collect(ui: dict, root: Path, sources: dict, api) -> list[dict]:
    previews = ui.get('quick_previews', [])
    if not isinstance(previews, list) or len(previews) > MAX_PREVIEWS:
        raise ValueError('quick_previews must be a list of at most six existing elements')
    seen = set()
    prepared = []
    for item in previews:
        if not isinstance(item, dict) or set(item) != {'id','title','html_source','selector','css_sources','note'}:
            raise ValueError('Quick preview needs id, title, html_source, selector, css_sources and note')
        name = item['id']
        if not isinstance(name, str) or not re.fullmatch(r'[A-Za-z][\w-]{0,35}', name) or name in seen:
            raise ValueError('Quick preview IDs must be unique simple identifiers')
        seen.add(name)
        api.text(item['title'], 'quick_preview.title', 80)
        api.text(item['note'], 'quick_preview.note', 300)
        selector = item['selector']
        if not isinstance(selector, str) or not SELECTOR.fullmatch(selector):
            raise ValueError('Quick preview selector must be a single tag.class, .class or #id')
        hs = item['html_source']
        if hs not in sources or not sources[hs]['path'].lower().endswith(('.html','.htm')):
            raise ValueError('Quick preview needs an existing supplied HTML source')
        html_path = api.safe_source(root, sources[hs]['path'])
        if html_path.stat().st_size > MAX_HTML:
            raise ValueError('Quick preview HTML source too large; use a smaller saved example')
        fragment = extract_fragment(html_path.read_text(encoding='utf-8'), selector)
        css_sources = item['css_sources']
        if not isinstance(css_sources,list) or not 1 <= len(css_sources) <= 4 or len(set(css_sources)) != len(css_sources):
            raise ValueError('Quick preview needs one to four unique compiled CSS sources')
        css = []
        for sid in css_sources:
            if sid not in sources or not sources[sid]['path'].lower().endswith('.css'):
                raise ValueError('Quick preview requires supplied compiled .css files (SCSS must be compiled first)')
            path = api.safe_source(root, sources[sid]['path'])
            if path.stat().st_size > MAX_CSS:
                raise ValueError('Quick preview stylesheet too large; select focused compiled CSS')
            contents = path.read_text(encoding='utf-8')
            if '</style' in contents.lower():
                raise ValueError('Quick preview stylesheet contains an unsafe style-tag terminator')
            css.append(contents)
        if sum(len(c.encode('utf-8')) for c in css) > MAX_CSS:
            raise ValueError('Quick preview CSS total exceeds 500 KB')
        prepared.append({**item, 'markup': fragment, 'css': '\n'.join(css)})
    return prepared


def frame_document(markup: str, css: str) -> str:
    # An opaque sandbox origin, no script/forms/navigation, and no remote assets.
    csp = ("default-src 'none'; script-src 'none'; style-src 'unsafe-inline'; "
           "img-src data:; font-src data:; connect-src 'none'; form-action 'none'; "
           "base-uri 'none'; frame-src 'none'")
    return (f'<!doctype html><html><head><meta charset="utf-8">'
            f'<meta http-equiv="Content-Security-Policy" content="{csp}">'
            f'<style>{css}\nhtml,body{{margin:0;}}body{{padding:20px;box-sizing:border-box;}}</style>'
            f'</head><body>{markup}</body></html>')


def render(previews: list[dict], api) -> str:
    if not previews:
        return ''
    rows = []
    for p in previews:
        doc = html.escape(frame_document(p['markup'], p['css']), quote=True)
        title = html.escape(p['title'])
        note = html.escape(p['note'])
        src = api.links([p['html_source'],*p['css_sources']], 's')
        frame = (f'<iframe sandbox="" loading="lazy" referrerpolicy="no-referrer" '
                 f'title="Static source-backed style sample: {title}" srcdoc="{doc}"></iframe>')
        rows.append(f'<article class="ui-quick-card"><h3>{title}</h3><p>{note}</p>'
                    f'<div class="ui-quick-small">{frame}</div>'
                    f'<details><summary>Expand full-size sample</summary><div class="ui-quick-full">{frame}</div></details>'
                    f'<p class="ui-evidence">Existing source and compiled CSS: {src}</p></article>')
    return ('<section class="ui-quick-gallery" aria-label="Existing styled UI samples">'
            '<h2>Real-style component samples</h2>'
            '<p class="hint">Static snippets of existing markup with existing compiled CSS. '
            'No Angular/React runtime, interactions or network. Not a rendered proposed page or design approval.</p>'
            f'<div class="ui-quick-grid">{"".join(rows)}</div></section>')
