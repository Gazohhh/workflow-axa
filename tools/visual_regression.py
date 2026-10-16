#!/usr/bin/env python3
"""Capture trusted local report fixtures and compare immutable PNG references.

No browser/dependency installation, reference replacement, network or approval action.
Optional capture needs Playwright; compare needs Pillow. Normal report generation does not.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import importlib.util
import json
import platform
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CASES = (
    ('desktop-proposed', 'proposed', 1440, 1100),
    ('desktop-current', 'current', 1440, 1100),
    ('desktop-build', 'build', 1440, 1100),
    ('mobile-proposed', 'proposed', 390, 844),
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def new_output(output: Path, protected: tuple[Path, ...] = ()) -> Path:
    raw = output.expanduser()
    if raw.exists() or raw.is_symlink():
        raise ValueError(f'Choose a new output directory; refusing {raw}')
    resolved = raw.resolve()
    if any(resolved == p.resolve() or p.resolve() in resolved.parents for p in protected):
        raise ValueError('Output cannot be inside an input/reference directory.')
    resolved.mkdir(parents=True, exist_ok=False)
    return resolved


def load_capture(folder: Path) -> dict:
    root = folder.resolve()
    manifest = json.loads((root/'manifest.json').read_text(encoding='utf-8'))
    if not isinstance(manifest, dict) or manifest.get('schema_version') != 1 or manifest.get('kind') != 'visual-capture':
        raise ValueError('Unsupported visual capture manifest.')
    if not isinstance(manifest.get('environment'), dict) or not manifest['environment']:
        raise ValueError('Capture has no controlled environment metadata.')
    cases = manifest.get('cases')
    if not isinstance(cases, list) or not cases:
        raise ValueError('Capture has no screenshot cases.')
    names = set()
    for case in cases:
        if not isinstance(case, dict):
            raise ValueError('Invalid screenshot entry.')
        name, filename = case.get('name'), case.get('file')
        if not isinstance(name, str) or not name or name in names:
            raise ValueError('Duplicate or missing screenshot name.')
        names.add(name)
        if not isinstance(filename, str) or Path(filename).name != filename or not filename.endswith('.png'):
            raise ValueError('Screenshot must be a local PNG basename.')
        path = root/filename
        if not path.is_file() or path.is_symlink() or path.resolve().parent != root:
            raise ValueError(f'Missing or unsafe screenshot: {filename}')
        if sha(path) != case.get('sha256'):
            raise ValueError(f'Screenshot hash does not match manifest: {filename}')
        if any(type(case.get(k)) is not int or case[k] < 1 for k in ('width', 'height')):
            raise ValueError('Screenshot dimensions must be positive integers.')
    return manifest


def compare(baseline: Path, candidate: Path, output: Path) -> tuple[int, dict]:
    try:
        from PIL import Image, ImageChops
    except ImportError as exc:
        raise RuntimeError('Pillow is unavailable; comparison NOT RUN. No installation attempted.') from exc
    # Validate both inputs before creating anything. Neither input is ever modified.
    base, current = load_capture(baseline), load_capture(candidate)
    out = new_output(output, (baseline, candidate))
    result = {'status': 'NOT_VERIFIED', 'baseline': str(baseline.resolve()),
              'candidate': str(candidate.resolve()), 'checks': [], 'limits': [
                  'Image equality checks appearance of these fixtures only, not user comprehension, accessibility or plan correctness.',
                  'Environment fingerprints reduce accidental mismatch; they are not proof of identical hardware or all rendering settings.']}
    if base['environment'] != current['environment']:
        result['reason'] = 'Different rendering environments. Do not auto-update the reference or relax thresholds.'
        code = 2
    elif {c['name'] for c in base['cases']} != {c['name'] for c in current['cases']}:
        result['reason'] = 'Different screenshot case sets; missing coverage is not a pass.'
        code = 2
    else:
        lookup = {c['name']: c for c in current['cases']}
        mismatch = False
        for index, before in enumerate(base['cases']):
            after = lookup[before['name']]
            with Image.open(baseline/before['file']) as image:
                expected = image.convert('RGB')
            with Image.open(candidate/after['file']) as image:
                actual = image.convert('RGB')
            if expected.size != (before['width'], before['height']) or actual.size != (after['width'], after['height']):
                raise ValueError('PNG dimensions do not match capture metadata.')
            check = {'case': before['name'], 'expected_size': list(expected.size), 'actual_size': list(actual.size)}
            if expected.size != actual.size:
                mismatch = True
                check.update(status='FAIL', reason='Image dimensions changed.')
            else:
                difference = ImageChops.difference(expected, actual)
                box = difference.getbbox()
                if box is not None:
                    mismatch = True
                    diff_name = f'difference-{index+1}.png'
                    difference.save(out/diff_name)
                    changed = sum(1 for pixel in difference.getdata() if pixel != (0, 0, 0))
                    check.update(status='FAIL', changed_pixels=changed, bounds=list(box), difference=diff_name)
                else:
                    check.update(status='PASS', changed_pixels=0)
            result['checks'].append(check)
        result['status'] = 'FAIL' if mismatch else 'PASS'
        code = 1 if mismatch else 0
    (out/'results.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    return code, result


def capture(package: Path, browser_path: Path, output: Path, no_sandbox: bool = False) -> dict:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise RuntimeError('Playwright is unavailable; capture NOT RUN. No installation attempted.') from exc
    package = package.resolve()
    renderer_path = package/'skills/codebase-map/scripts/render_report.py'
    source = package/'skills/codebase-map/examples'
    if not browser_path.is_file() or not renderer_path.is_file() or not (source/'review.json').is_file():
        raise ValueError('Supply an existing Chromium executable and a trusted complete package.')
    out = new_output(output, (source,))
    spec = importlib.util.spec_from_file_location('visual_reference_renderer', renderer_path)
    renderer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(renderer)
    data = renderer.load_json(source/'review.json')
    content = renderer.render(data, source, source/'review.json')
    report = out/'capture.html'
    report.write_text(content, encoding='utf-8')
    manifest = {'schema_version': 1, 'kind': 'visual-capture', 'cases': [],
                'provenance': {'package_version': json.loads((package/'.claude-plugin/plugin.json').read_text())['version'],
                               'renderer_sha256': sha(renderer_path), 'input_sha256': sha(source/'review.json'),
                               'reference_authority': 'Capture only. Generation does not approve or replace a reference.'}}
    errors, requests = [], []
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=str(browser_path.resolve()), headless=True,
                                   args=['--no-sandbox'] if no_sandbox else [])
        context = browser.new_context(offline=True, viewport={'width':1440,'height':1100},
                                      device_scale_factor=1, locale='en-US', timezone_id='UTC',
                                      color_scheme='light', reduced_motion='reduce')
        page = context.new_page()
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.on('request', lambda req: requests.append(req.url))
        direct_file = True
        try:
            page.goto(report.as_uri(), wait_until='load', timeout=10000)
        except Exception:
            direct_file = False
            # Managed browser policies can reject file URLs. Identical bytes, still offline.
            page.close()
            page = context.new_page()
            page.on('pageerror', lambda e: errors.append(str(e)))
            page.on('request', lambda req: requests.append(req.url))
            page.set_content(content, wait_until='load')
        page.locator('#panel-proposed').wait_for(state='visible')
        page.evaluate('document.fonts.ready')
        # Rasterize the actual declared typefaces, rather than storing/shipping font files.
        font_probe = page.evaluate('''() => {
          const canvas=document.createElement('canvas'); canvas.width=1800;canvas.height=240;
          const ctx=canvas.getContext('2d');ctx.fillStyle='white';ctx.fillRect(0,0,1800,240);ctx.fillStyle='black';
          ['400 40px Georgia,serif',
           '600 18px "Geist","Inter","Segoe UI",system-ui,sans-serif',
           '400 13px "Geist","Inter","Segoe UI",system-ui,sans-serif',
           '400 10px "Geist Mono",ui-monospace,monospace'].forEach((font,index)=>{
            ctx.font=font;
            ctx.fillText('Workflow 0123456789 AaBbCc Wm@+-→',12,40+index*52);
          });return canvas.toDataURL();}''')
        manifest['environment'] = {'harness_version':1, 'system':platform.system(), 'machine':platform.machine(),
                'browser':browser.version, 'playwright':importlib.metadata.version('playwright'),
                'device_scale_factor':1, 'locale':'en-US', 'timezone':'UTC', 'headless':True,
                'color_scheme':'light', 'reduced_motion':'reduce', 'font_raster_sha256':hashlib.sha256(font_probe.encode()).hexdigest()}
        for name, view, width, height in CASES:
            page.set_viewport_size({'width':width, 'height':height})
            page.locator(f'label[for="view-{view}"]').click()
            page.locator('label[for="zoom-100"]').click()
            panel = page.locator(f'#panel-{view}')
            panel.wait_for(state='visible')
            page.evaluate('document.fonts.ready')
            # Let two animation frames complete layout and the viewer's entry-point centering.
            page.evaluate('() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))')
            canvas = panel.locator('.canvas')
            if width < 800:
                page.wait_for_function('''id => {const el=document.querySelector(`#panel-${id} .canvas`);
                  const n=document.getElementById(el.dataset.startId).getBoundingClientRect(),c=el.getBoundingClientRect();
                  return n.left<c.right && n.right>c.left;}''', arg=view)
            page.mouse.move(0,0)
            page.evaluate('document.activeElement?.blur()')
            region = page.locator('.review')
            first = region.screenshot(animations='disabled', caret='hide')
            second = region.screenshot(animations='disabled', caret='hide')
            if first != second:
                raise RuntimeError(f'Unstable consecutive screenshots: {name}; reference not captured.')
            png = out/f'{name}.png'
            png.write_bytes(second)
            # PNG IHDR dimensions avoid a Pillow dependency for capture.
            width_px = int.from_bytes(second[16:20], 'big')
            height_px = int.from_bytes(second[20:24], 'big')
            manifest['cases'].append({'name':name, 'file':png.name, 'width':width_px,'height':height_px,
                                      'sha256':sha(png), 'viewport':[width,height]})
        network = [url for url in requests if url.startswith(('http:', 'https:'))]
        browser.close()
    if network or errors:
        raise RuntimeError(f'Unexpected network requests/page errors: {network!r} {errors!r}')
    manifest['direct_file_navigation'] = direct_file
    manifest['external_requests'] = network
    manifest['page_errors'] = errors
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n', encoding='utf-8')
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    cap = sub.add_parser('capture', help='Capture a new reference candidate; does not approve it.')
    cap.add_argument('--package', type=Path, default=ROOT, help='Trusted package to execute, default this one.')
    cap.add_argument('--browser', type=Path, required=True)
    cap.add_argument('--output', type=Path, required=True)
    cap.add_argument('--no-sandbox', action='store_true', help='Trusted disposable container only.')
    comp = sub.add_parser('compare', help='Compare captures exactly; never rewrite either input.')
    comp.add_argument('--baseline', type=Path, required=True)
    comp.add_argument('--candidate', type=Path, required=True)
    comp.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == 'capture':
            result = capture(args.package, args.browser, args.output, args.no_sandbox)
            print(f'CAPTURED: {len(result["cases"])} cases. Review before adopting a reference; not an approval action.')
            return 0
        code, result = compare(args.baseline,args.candidate,args.output)
        print(f'{result["status"]}: {len(result["checks"])} comparisons; {args.output.resolve()}')
        return code
    except Exception as exc:  # A CLI failure must be explicit; never convert it into a passing capture.
        print(f'NOT VERIFIED: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
