"""Screens composed from a saved design-kit snapshot (kit_snapshot.py), shown live in the report.

A kit screen is a small .html file holding body markup copied from the snapshot. Before rendering,
every tag, class, inline style value and image in it must already exist in the snapshot, so a screen
cannot invent a class or CSS. The report stores each snapshot's styles once and each screen's markup
as JSON; report JS builds sandboxed frames (no scripts, forms or network except Typekit fonts).
"""
from __future__ import annotations

import html
import json
import re
from html.parser import HTMLParser
from pathlib import Path

MAX_SNAPSHOT = 7_000_000
MAX_SCREEN = 1_000_000
FRAME_WIDTH = 1280            # default when a snapshot names no width
CSS_CLASS = re.compile(r'\.(-?[A-Za-z_][\w-]*)')
FORBIDDEN_TAGS = {'script', 'iframe', 'object', 'embed', 'link', 'meta', 'base', 'frame', 'frameset', 'noscript'}
URL_ATTRS = {'href', 'src', 'srcset', 'action', 'formaction', 'xlink:href', 'poster', 'ping', 'background'}
VOID_TAGS = {'area','base','br','col','embed','hr','img','input','link','meta','source','track','wbr'}
ASSET = re.compile(r'__KIT_ASSET_\d+__')
TYPEKIT = re.compile(r'<link rel="stylesheet" href="(https://use\.typekit\.net/[A-Za-z0-9]+\.css)">')


class Inventory(HTMLParser):
    """Collects tags, classes, style values and image sources; flags anything unsafe."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tags: set[str] = set()
        self.classes: set[str] = set()
        self.styles: set[str] = set()
        self.images: set[str] = set()
        self.refs: set[str] = set()
        self.uses: list[tuple[str, str, str]] = []   # (kind, value, tag) for the check
        self.unsafe: list[str] = []
        self.in_style = False
        self.stack: list[str] = []
        self.styled_hosts: set[str] = set()   # hosts whose shadow root starts with a kit style
        self.bare_hosts: set[str] = set()     # hosts whose shadow root has no kit style
        self.pending: str | None = None       # host of a shadow root that just opened

    def handle_starttag(self, tag, attrs):
        if self.pending is not None:
            (self.styled_hosts if tag == 'style' and dict(attrs).get('data-kit-shadow-ref') else self.bare_hosts).add(self.pending)
            self.pending = None
        if tag == 'template' and dict(attrs).get('shadowrootmode') and self.stack:
            self.pending = self.stack[-1]
        if tag not in VOID_TAGS:
            self.stack.append(tag)
        self.tags.add(tag)
        self.uses.append(('tag', tag, tag))
        for key, value in attrs:
            value = value or ''
            if key.startswith('on') or re.match(r'\s*javascript:', value, re.I):
                self.unsafe.append(f'<{tag} {key}>')
            elif key == 'class':
                for name in value.split():
                    self.classes.add(name)
                    self.uses.append(('class', name, tag))
            elif key == 'style':
                self.styles.add(value.strip())
                self.uses.append(('style', value.strip(), tag))
            elif key == 'data-kit-shadow-ref':
                self.refs.add(value)
            elif key in URL_ATTRS:
                if tag == 'img' and key == 'src' and (value.startswith('data:image/') or ASSET.fullmatch(value)):
                    self.images.add(value)
                    self.uses.append(('image', value, tag))
                elif key == 'href' and value.startswith('#'):
                    pass
                else:
                    self.unsafe.append(f'<{tag} {key}="{value[:40]}">')
        if tag in FORBIDDEN_TAGS:
            self.unsafe.append(f'<{tag}>')
        if tag == 'template' and dict(attrs).get('shadowrootmode') != 'open':
            self.unsafe.append('<template> other than a copied shadow root')
        self.in_style = tag == 'style'
        if tag == 'style' and 'data-kit-shadow-ref' not in dict(attrs):
            self.unsafe.append('<style> (copy kit elements; never add CSS)')

    def handle_endtag(self, tag):
        if self.pending is not None and tag == 'template':
            self.bare_hosts.add(self.pending)
            self.pending = None
        if tag in self.stack:
            while self.stack and self.stack.pop() != tag:
                pass
        if tag == 'style':
            self.in_style = False

    def handle_data(self, data):
        if self.in_style and data.strip():
            self.unsafe.append('CSS text inside <style>')


def inventory(text: str) -> Inventory:
    parser = Inventory()
    parser.feed(text)
    parser.close()
    return parser


def load_snapshot(path: Path) -> dict:
    if path.stat().st_size > MAX_SNAPSHOT:
        raise ValueError('Kit snapshot is larger than 7 MB; capture a smaller kit section')
    text = path.read_text(encoding='utf-8')
    head_end = text.find('</head>')
    body_at = text.find('<body', head_end)
    if '<meta name="workflow-kit-snapshot" content="1">' not in text[:2000] or head_end < 0 or body_at < 0:
        raise ValueError('Kit snapshot must be a file written by kit_snapshot.py')
    html_attrs = re.match(r'<!doctype html>\s*<html([^>]*)>', text, re.I)
    body_open = text.index('>', body_at)
    body_end = text.rfind('</body>')
    head = text[text.index('<head>') + 6:head_end]
    css = re.search(r'<style data-kit-css>(.*?)</style>', head, re.S)
    shadow = dict(re.findall(r'<template data-kit-shadow-css="(k\d+)"><style>(.*?)</style></template>', head, re.S))
    assets = dict(re.findall(r'<template data-kit-asset="(__KIT_ASSET_\d+__)">(.*?)</template>', head, re.S))
    width = re.search(r'<meta name="workflow-kit-width" content="(\d{3,4})">', head)
    # Classes the kit's own stylesheets define count as existing styles too (for example every icon
    # glyph of an icon font), even when no kit example happens to use them.
    defined = set(CSS_CLASS.findall((css.group(1) if css else '') + ''.join(shadow.values())))
    return {'width': int(width.group(1)) if width else FRAME_WIDTH, 'defined': defined,'html_attrs': html_attrs.group(1) if html_attrs else '', 'body_attrs': text[body_at + 5:body_open],
            'css': css.group(1) if css else '', 'shadow': shadow, 'assets': assets, 'typekit': TYPEKIT.findall(head),
            'inventory': inventory(text[body_open + 1:body_end])}


def check(markup: str, snapshot: dict) -> list[str]:
    """Every problem in one list: unknown tags, classes, inline styles and images, or unsafe markup."""
    have = snapshot['inventory']
    used = inventory(markup)
    problems = [f'{u} is not allowed in a kit screen' for u in dict.fromkeys(used.unsafe)]
    missing = {}
    for kind, value, tag in used.uses:
        known = {'tag': have.tags, 'class': have.classes | snapshot['defined'], 'style': have.styles,
                 'image': have.images}[kind]
        if value not in known:
            label = {'tag': f'tag <{value}>', 'class': f'class "{value}" on <{tag}>',
                     'style': f'inline style "{value[:60]}" on <{tag}>', 'image': f'an image on <{tag}>'}[kind]
            missing[label] = None
    problems += [f'{m} is not in the kit snapshot' for m in missing]
    problems += [f'shadow style reference {r} is not in the kit snapshot' for r in sorted(used.refs - set(snapshot['shadow']))]
    # A copied web component keeps its shadow style: the kit's copy has one, so this one needs it too.
    problems += [f'the shadow root of <{h}> lost its kit style; copy the element whole, including its '
                 f'<style data-kit-shadow-ref> line' for h in sorted(used.bare_hosts & have.styled_hosts)]
    return problems


def validate_screen(screen: dict, root: Path, sources: dict, api) -> int:
    """Checks one kit screen; returns its rendered byte size for the report budget."""
    for field, role in (('kit_snapshot', 'kit-snapshot'), ('kit_markup', 'kit-screen')):
        sid = screen.get(field)
        if sid not in screen['sources'] or sources[sid]['role'] != role or not sources[sid]['path'].lower().endswith('.html'):
            raise ValueError(f'Kit screen needs {field}: a listed .html source with role {role}')
    if {'content', 'capture', 'markers'} & set(screen):
        raise ValueError('Kit screen is built from kit markup; it has no sketch content, capture or markers')
    snapshot = load_snapshot(api.safe_source(root, sources[screen['kit_snapshot']]['path']))
    markup_path = api.safe_source(root, sources[screen['kit_markup']]['path'])
    if markup_path.stat().st_size > MAX_SCREEN:
        raise ValueError('Kit screen markup is larger than 1 MB; split the screen')
    markup = markup_path.read_text(encoding='utf-8')
    if not markup.strip():
        raise ValueError('Kit screen markup is empty')
    problems = check(markup, snapshot)
    if problems:
        raise ValueError('Kit screen uses parts that are not in the kit. Copy existing kit elements, or ask '
                         '"I couldn\'t find a matching style for [element]. Is there an existing element I should mimic?": '
                         + '; '.join(problems[:12]) + (f' (and {len(problems) - 12} more)' if len(problems) > 12 else ''))
    return len(markup.encode('utf-8'))


def payload(ui: dict, root: Path, sources: dict, api) -> dict:
    kits, screens = {}, {}
    for s in ui['screens']:
        if s.get('representation') != 'kit':
            continue
        sid = s['kit_snapshot']
        if sid not in kits:
            snap = load_snapshot(api.safe_source(root, sources[sid]['path']))
            kits[sid] = {k: snap[k] for k in ('html_attrs', 'body_attrs', 'css', 'shadow', 'assets', 'typekit', 'width')}
        screens[s['id']] = {'kit': sid,
                            'markup': api.safe_source(root, sources[s['kit_markup']]['path']).read_text(encoding='utf-8')}
    return {'kits': kits, 'screens': screens}


def uses_typekit(data: dict) -> bool:
    return any(k['typekit'] for k in data['kits'].values())


def page_width(screen: dict, root: Path, sources: dict, api) -> int:
    return load_snapshot(api.safe_source(root, sources[screen['kit_snapshot']]['path']))['width']


def frame(screen: dict, suffix: str, width: int, height: int, page: int) -> str:
    """A placeholder frame; report JS fills srcdoc from the payload. Thumbnails scale the page down."""
    title = html.escape(screen['title'])
    scale = min(1, width / page)
    shown = round(page * scale)
    viewport = max(400, round(height / scale))
    return (f'<div class="ui-kit-frame ui-kit-{suffix}" style="width:{shown}px;height:{height}px">'
            f'<iframe sandbox="" referrerpolicy="no-referrer" data-kit-screen="{html.escape(screen["id"])}" '
            f'title="Kit preview: {title}" width="{page}" height="{viewport}" tabindex="-1" '
            f'style="transform:scale({scale:.4f})"></iframe></div>')


def card(screen: dict, page: int) -> str:
    width, height = screen['width'], screen['height']
    return (f'<div class="ui-kit-card"><p class="ui-kit-caption">{html.escape(screen["title"])}</p>'
            f'{frame(screen, "thumb", width - 16, height - 86, page)}'
            '<p class="ui-kit-footnote">Kit preview · real kit markup and CSS, fake data</p></div>')


def detail(screen: dict, page: int) -> str:
    return (f'<div class="ui-kit-detail" style="max-width:{page}px"><iframe sandbox="" referrerpolicy="no-referrer" '
            f'data-kit-screen="{html.escape(screen["id"])}" title="Kit preview at full size: {html.escape(screen["title"])}" '
            f'width="{page}" height="{900 if page >= 768 else 844}"></iframe></div>'
            '<p class="ui-evidence">Built only from markup copied out of the saved kit page, shown with the kit\'s own '
            'stylesheets. Scripts do not run here, so menus and toggles show the state the kit example shows.</p>')


def data_script(data: dict) -> str:
    text = json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    return f'<script type="application/json" id="ui-kit-data">{text}</script>'
