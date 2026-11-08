"""Save a rendered design-kit page as one self-contained, script-free HTML file. No installs.

usage: python -X utf8 kit_snapshot.py <kit-url> [<kit-url> ...] <out.html> [--browser PATH] [--wait-selector CSS] [--width PX]

--click SELECTOR (repeatable) clicks a kit control on every captured page before saving it, for
examples the kit only shows after a click (a page preview, an open dialog). Playwright selectors such
as 'text=Open page preview' work.

--width is the window width the app is used at: 1280 (default) for desktop admin pages, 390 for a
phone app. The report shows the screens at this width.

Opens the developer's own local kit page (Blade, Angular/Ionic, React or anything else that renders in
Chromium) in an already-installed Edge or Chrome through Python Playwright, waits for it to settle and
writes the rendered page. A kit that shows one example or category at a time takes the address
of each one the screens need (same site); their markup is merged and shared styles are kept once:

- every element as it rendered, with open shadow roots written as declarative shadow DOM
  (<template shadowrootmode="open">), so web components such as Ionic show without their scripts;
- every stylesheet's rules inlined once (shadow-root styles are shared by reference), with fonts and
  small images inlined as data: URIs;
- no scripts, event handlers, links, external sources or form actions. A Typekit stylesheet is the
  only outside reference kept (the report allows use.typekit.net and nothing else).

Requests to any other origin than the kit's own are blocked while the page loads, so a kit that
would call a backend fails visibly instead of reaching real data. The kit URL itself is never written
into the file. Put the output in the task's output folder (ARTIFACTS.md); it is report input, not a
deliverable. Run it without -I: Playwright is often a per-user package. Exit 0: written; 1: the page or browser failed; 2: bad input, Playwright for Python or a
browser is missing (nothing is installed automatically; use the sketch fallback and say why).
"""
from __future__ import annotations

import importlib.util
import json
import pathlib
import re
import sys
from urllib.parse import urlsplit

MAX_ASSET = 2_000_000          # one inlined font or image (some dev fonts are full TTFs)
MAX_ASSETS_TOTAL = 4_000_000   # everything inlined; the report itself stays under 8 MiB
TYPEKIT = re.compile(r'^https://use\.typekit\.net/[A-Za-z0-9]+\.css$')
ALLOWED_HOSTS = {'use.typekit.net', 'p.typekit.net'}

SERIALIZE = r"""
async ({maxAsset, maxTotal}) => {
  const VOID = new Set(['area','base','br','col','embed','hr','img','input','link','meta','source','track','wbr']);
  const SKIP = new Set(['script','noscript','iframe','object','embed','video','audio','canvas','link','style','meta','base','title','template']);
  const DROP_ATTR = /^(on|href$|src$|srcset$|action$|formaction$|xlink:href$|ping$|poster$|data-src$)/i;
  const notes = [];
  await document.fonts.ready;
  const esc = s => s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
  const attrEsc = s => s.replace(/&/g,'&amp;').replace(/"/g,'&quot;').replace(/</g,'&lt;');

  // Assets are fetched by the capture script, not here: a page may replace window.fetch.
  const assetUrls = [];
  const priority = {};
  function dataUri(url, score = 1) {
    if (url.startsWith('data:')) return url;
    let i = assetUrls.indexOf(url);
    if (i < 0) { i = assetUrls.length; assetUrls.push(url); }
    priority[i] = Math.max(priority[i] || 0, score);
    return `__KIT_ASSET_${i}__`;
  }

  async function inlineUrls(css, base, score = 1) {
    const found = [...css.matchAll(/url\(\s*(['"]?)([^'")]+)\1\s*\)/g)];
    for (const m of found) {
      const raw = m[2].trim();
      if (raw.startsWith('data:') || raw.startsWith('#') || raw.startsWith('__KIT_ASSET_')) continue;
      let abs; try { abs = new URL(raw, base).href; } catch { continue; }
      css = css.split(m[0]).join(`url("${dataUri(abs, score)}")`);
    }
    return css;
  }

  // Only font families the page actually loaded are kept; unused faces would fill the budget.
  const familyName = f => String(f).replace(/^['"]|['"]$/g, '').trim().toLowerCase();
  const weight = w => ({normal: '400', bold: '700', '': '400'}[String(w).trim()] || String(w).trim());
  const slant = v => (String(v).trim() || 'normal').startsWith('italic') || String(v).startsWith('oblique') ? 'italic' : 'normal';
  const faceKey = (family, w, st) => `${familyName(family)}|${weight(w)}|${slant(st)}`;
  const loaded = [...document.fonts].filter(f => f.status === 'loaded');
  const loadedFaces = new Set(loaded.map(f => faceKey(f.family, f.weight, f.style)));
  const loadedFamilies = new Set(loaded.map(f => familyName(f.family)));
  // How many elements render in each family decides which fonts fit the budget first:
  // icon and interface fonts before the one-off previews of a font picker.
  const familyUse = {};
  for (const el of document.querySelectorAll('*')) {
    const first = familyName(getComputedStyle(el).fontFamily.split(',')[0]);
    familyUse[first] = (familyUse[first] || 0) + 1;
  }
  async function fontFaceText(rule, base) {
    const family = familyName(rule.style.getPropertyValue('font-family'));
    if (!loadedFamilies.has(family)) return '';
    // A family whose faces were loaded keeps only those exact weights and styles.
    const key = faceKey(family, rule.style.getPropertyValue('font-weight'), rule.style.getPropertyValue('font-style'));
    if (!loadedFaces.has(key) && !/\s/.test(weight(rule.style.getPropertyValue('font-weight')))) return '';
    // Keep one source per face: woff2 when listed, so each font is inlined once.
    const src = rule.style.getPropertyValue('src');
    const parts = src.split(/,(?![^(]*\))/).map(s => s.trim()).filter(Boolean);
    const pick = parts.find(p => /woff2/i.test(p)) || parts.find(p => /url\(/i.test(p)) || parts[0];
    const text = pick ? rule.cssText.replace(src, pick) : rule.cssText;
    return inlineUrls(text, base, 10 + (familyUse[family] || 0));
  }

  async function sheetText(sheet, base) {
    let rules;
    try { rules = sheet.cssRules; } catch { return {external: sheet.href || null}; }
    const out = [];
    for (const r of rules) {
      if (r.type === CSSRule.IMPORT_RULE) {
        if (r.styleSheet) { const sub = await sheetText(r.styleSheet, r.styleSheet.href || base); if (sub.text) out.push(sub.text); else if (sub.external) out.push(`@import url("${sub.external}");`); }
        continue;
      }
      out.push(r.type === CSSRule.FONT_FACE_RULE ? await fontFaceText(r, base) : r.cssText);
    }
    return {text: await inlineUrls(out.join('\n'), base)};
  }

  const externals = [];
  const seenSheets = new Set();
  async function collectList(sheets, base) {
    const out = [];
    for (const s of sheets) {
      if (s.disabled) continue;
      if (s.href && s.ownerNode && seenSheets.has(s.href)) continue;  // the same file linked twice
      if (s.href && s.ownerNode) seenSheets.add(s.href);
      const r = await sheetText(s, s.href || base);
      if (r.text) out.push(r.text);
      else if (r.external) externals.push(r.external);
    }
    return out;
  }
  const collect = async (sheets, base) => (await collectList(sheets, base)).join('\n');

  const shadowKeys = new Map();
  const shadowCss = {};
  async function shadowStyle(root) {
    const css = await collect([...(root.adoptedStyleSheets || []), ...root.styleSheets], location.href);
    if (!css) return '';
    let key = shadowKeys.get(css);
    if (!key) { key = 'k' + (shadowKeys.size + 1); shadowKeys.set(css, key); shadowCss[key] = css; }
    return `<style data-kit-shadow-ref="${key}"></style>`;
  }

  function attrs(el) {
    const out = [];
    for (const a of el.attributes) {
      const name = a.name;
      if (DROP_ATTR.test(name)) {
        if (name === 'href' && el.namespaceURI === 'http://www.w3.org/2000/svg' && a.value.startsWith('#')) out.push(` href="${attrEsc(a.value)}"`);
        continue;
      }
      if (/^\s*javascript:/i.test(a.value)) continue;
      let value = a.value;
      if (name === 'style' && /url\(/i.test(value)) {
        value = value.replace(/url\(\s*(['"]?)([^'")]+)\1\s*\)/g, (m, q, raw) => {
          if (raw.startsWith('data:') || raw.startsWith('__KIT_ASSET_')) return m;
          try { return `url("${dataUri(new URL(raw, location.href).href)}")`; } catch { return 'url("data:,")'; }
        });
      }
      if (value.includes(location.host)) { notes.push(`attribute ${name} dropped: it named the kit site`); continue; }
      out.push(value === '' ? ` ${name}` : ` ${name}="${attrEsc(value)}"`);
    }
    return out;
  }

  async function node(n) {
    if (n.nodeType === Node.TEXT_NODE) return esc(n.data);
    if (n.nodeType !== Node.ELEMENT_NODE) return '';
    const tag = n.localName;
    if (SKIP.has(tag)) return '';
    const list = attrs(n);
    if (tag === 'img') {
      const src = n.currentSrc || n.getAttribute('src');
      if (src) list.push(` src="${dataUri(new URL(src, location.href).href)}"`);
    }
    if (tag === 'input') {
      const filtered = list.filter(a => !/^ (value|checked)(=|$)/.test(a));
      if (n.type !== 'password' && n.value) filtered.push(` value="${attrEsc(n.value)}"`);
      if (n.checked) filtered.push(' checked');
      list.length = 0; list.push(...filtered);
    }
    if (tag === 'option' && n.selected && !n.hasAttribute('selected')) list.push(' selected');
    let inner = '';
    if (n.shadowRoot) {
      let sh = await shadowStyle(n.shadowRoot);
      for (const c of n.shadowRoot.childNodes) sh += await node(c);
      inner += `<template shadowrootmode="open">${sh}</template>`;
    }
    if (tag === 'textarea') inner += esc(n.value);
    else for (const c of n.childNodes) inner += await node(c);
    if (VOID.has(tag)) return `<${tag}${list.join('')}>`;
    return `<${tag}${list.join('')}>${inner}</${tag}>`;
  }

  const docSheets = await collectList([...document.styleSheets, ...(document.adoptedStyleSheets || [])], location.href);
  let body = '';
  for (const c of document.body.childNodes) body += await node(c);
  return {
    html_attrs: attrs(document.documentElement).join(''),
    body_attrs: attrs(document.body).join(''),
    sheets: docSheets, shadow: shadowCss, body, externals, notes, assets: assetUrls, priority,
  };
}
"""


def find_browser(explicit: str | None) -> str | None:
    spec = importlib.util.spec_from_file_location(
        'workflow_screenshot_report', pathlib.Path(__file__).with_name('screenshot_report.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.find_browser(explicit)


def inline_assets(result: dict, request, origin: str) -> tuple[int, list[str]]:
    """Replaces asset placeholders with data: URIs fetched from the kit's own origin, within budget."""
    import base64
    total, notes, values = 0, [], {}
    order = sorted(range(len(result['assets'])), key=lambda i: -result['priority'].get(str(i), 1))
    for i in order:
        url = result['assets'][i]
        value = 'data:,'
        target = urlsplit(url)
        if f'{target.scheme}://{target.netloc}' != origin:
            notes.append(f'not inlined (other origin): {target.netloc}')
        else:
            try:
                response = request.get(url, timeout=30_000)
                body = response.body() if response.ok else b''
                kind = (response.headers.get('content-type') or 'application/octet-stream').split(';')[0].strip()
                if not response.ok:
                    notes.append(f'asset failed ({response.status}): {target.path}')
                elif len(body) > MAX_ASSET or total + len(body) > MAX_ASSETS_TOTAL:
                    notes.append(f'asset over budget: {target.path}{"?" + target.query[:60] if target.query else ""} ({len(body)} bytes)')
                else:
                    total += len(body)
                    value = f'data:{kind};base64,' + base64.b64encode(body).decode('ascii')
            except Exception as exc:  # one missing icon must not stop the capture
                notes.append(f'asset error: {target.path} ({type(exc).__name__})')
        values[f'__KIT_ASSET_{i}__'] = value
    # Each asset is stored once; the report fills the placeholders in when it builds a frame.
    result['asset_values'] = values
    return total, notes


def merge(pages: list[dict]) -> dict:
    """One snapshot from several kit pages: shared stylesheets, shadow styles and assets stored once."""
    urls, priority, sheets, shadow_keys, bodies, externals, notes = [], {}, [], {}, [], [], []
    placeholder = re.compile(r'__KIT_ASSET_(\d+)__')
    for page in pages:
        local = {}
        for i, url in enumerate(page['assets']):
            if url not in urls:
                urls.append(url)
            g = urls.index(url)
            local[str(i)] = g
            priority[str(g)] = max(priority.get(str(g), 1), page['priority'].get(str(i), 1))
        swap = lambda text, local=local: placeholder.sub(
            lambda m: f'__KIT_ASSET_{local[m.group(1)]}__' if m.group(1) in local else m.group(0), text)
        refs = {}
        for key, css in page['shadow'].items():
            css = swap(css)
            shadow_keys.setdefault(css, f'k{len(shadow_keys) + 1}')
            refs[key] = shadow_keys[css]
        for sheet in page['sheets']:
            sheet = swap(sheet)
            if sheet not in sheets:
                sheets.append(sheet)
        body = re.sub(r'data-kit-shadow-ref="(k\d+)"', lambda m: f'data-kit-shadow-ref="{refs.get(m.group(1), m.group(1))}"',
                      swap(page['body']))
        bodies.append(body)
        externals += page['externals']
        notes += page['notes']
    return {'html_attrs': pages[0]['html_attrs'], 'body_attrs': pages[0]['body_attrs'], 'css': '\n'.join(sheets),
            'shadow': {key: css for css, key in shadow_keys.items()}, 'body': '\n'.join(bodies),
            'externals': externals, 'notes': notes, 'assets': urls, 'priority': priority}


def css_block(text: str) -> str:
    # A stylesheet must not close its own <style> element; "\/" is a valid CSS escape for "/".
    return re.sub(r'</(style)', r'<\\/\1', text, flags=re.I)


def document(result: dict, typekit: list[str], width: int = 1280) -> str:
    shadow = ''.join(f'<template data-kit-shadow-css="{key}"><style>{css_block(css)}</style></template>'
                     for key, css in result['shadow'].items())
    links = ''.join(f'<link rel="stylesheet" href="{href}">' for href in typekit)
    assets = ''.join(f'<template data-kit-asset="{key}">{value}</template>'
                     for key, value in result.get('asset_values', {}).items())
    return ('<!doctype html>\n'
            f'<html{result["html_attrs"]}><head><meta charset="utf-8">'
            '<meta name="workflow-kit-snapshot" content="1">'
            f'<meta name="workflow-kit-width" content="{width}">'
            f'{links}<style data-kit-css>{css_block(result["css"])}</style>{shadow}{assets}</head>'
            f'<body{result["body_attrs"]}>{result["body"]}</body></html>\n')


def main(argv: list[str]) -> int:
    args = argv[1:]
    options = {}
    clicks = []
    while '--click' in args:
        i = args.index('--click')
        clicks.append(args[i + 1])
        del args[i:i + 2]
    for flag in ('--browser', '--wait-selector', '--width'):
        if flag in args:
            i = args.index(flag)
            if i + 1 >= len(args):
                print(f'{flag} needs a value.')
                return 2
            options[flag] = args[i + 1]
            del args[i:i + 2]
    if not str(options.get('--width', '1280')).isdigit() or not 320 <= int(options.get('--width', 1280)) <= 2560:
        print('--width must be a number of pixels from 320 to 2560.')
        return 2
    if len(args) < 2:
        print(__doc__)
        return 2
    urls, out = args[:-1], pathlib.Path(args[-1]).resolve()
    parts = urlsplit(urls[0])
    if any(urlsplit(u).scheme not in ('http', 'https') or urlsplit(u).netloc != parts.netloc for u in urls):
        print('Every kit address must be an http(s) URL of the same local site.')
        return 2
    if out.suffix.lower() != '.html' or not out.parent.is_dir():
        print('The output must be an .html file in an existing folder (the task output folder).')
        return 2
    if out.exists():
        print(f'{out.name} exists; choose a new name or remove your own earlier snapshot first.')
        return 2
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print('Playwright for Python is not installed. Nothing was installed; use the sketch fallback and say why.')
        return 2
    browser_path = find_browser(options.get('--browser'))
    if not browser_path:
        print('No installed Edge or Chrome found; pass --browser PATH. Nothing was installed.')
        return 2
    origin = f'{parts.scheme}://{parts.netloc}'
    blocked: list[str] = []

    def route(r):
        target = urlsplit(r.request.url)
        own = f'{target.scheme}://{target.netloc}' == origin
        if own or target.scheme in ('data', 'blob') or target.hostname in ALLOWED_HOSTS:
            return r.continue_()
        blocked.append(target.netloc)
        return r.abort()

    width = int(options.get('--width', 1280))
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path=browser_path, headless=True)
            context = browser.new_context(viewport={'width': width, 'height': 900}, service_workers='block')
            context.route('**/*', route)
            if hasattr(context, 'route_web_socket'):
                context.route_web_socket(re.compile('.*'), lambda ws: (blocked.append('websocket'), ws.close()))
            page = context.new_page()
            pages = []
            for url in urls:
                page.goto(url, wait_until='networkidle', timeout=90_000)
                if '--wait-selector' in options:
                    page.wait_for_selector(options['--wait-selector'], timeout=60_000)
                page.wait_for_timeout(1500)
                for target in clicks:  # opens kit examples that only show after a click
                    if page.locator(target).count():
                        page.locator(target).first.click()
                        page.wait_for_timeout(1200)
                pages.append(page.evaluate(SERIALIZE, {'maxAsset': MAX_ASSET, 'maxTotal': MAX_ASSETS_TOTAL}))
            result = merge(pages)
            inlined, asset_notes = inline_assets(result, page.context.request, origin)
            browser.close()
    except Exception as exc:  # report the browser failure plainly; nothing is half-written
        print(f'The kit page could not be captured: {exc}')
        return 1
    typekit = sorted({h for h in result['externals'] if h and TYPEKIT.match(h)})
    dropped = sorted({h for h in result['externals'] if h and not TYPEKIT.match(h)})
    text = document(result, typekit, width)
    # Last guard: the kit's own address never stays in the file (text content included).
    leaks = text.count(origin) + text.count(parts.netloc)
    text = text.replace(origin, '').replace(parts.netloc, 'local-site')
    if leaks:
        result['notes'].append(f'{leaks} mention(s) of the kit address removed')
    out.write_text(text, encoding='utf-8')
    summary = {'file': str(out), 'bytes': out.stat().st_size, 'inlined_asset_bytes': inlined,
               'shadow_styles': len(result['shadow']), 'typekit': typekit, 'dropped_stylesheets': dropped,
               'blocked_hosts': sorted(set(blocked)), 'notes': sorted(set(result['notes'] + asset_notes))[:20]}
    print(json.dumps(summary, indent=1))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
