#!/usr/bin/env python3
"""Check source-bound report details with synthetic local fixtures and an installed browser.

Does not run a project, install a catalogue, authenticate approval, or make network requests.
Screenshots depict grey test pixels, not an application design.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--browser', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--no-sandbox', action='store_true', help='Trusted disposable container only.')
    args = parser.parse_args()
    if args.output.exists() or args.output.is_symlink():
        parser.error('Choose a fresh output directory; existing evidence stays unchanged.')
    if not args.browser.is_file():
        parser.error('Supply an already installed Chromium executable.')
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print('NOT RUN: Playwright unavailable. No installation attempted.', file=sys.stderr)
        return 2
    renderer = load('kit_smoke_renderer', ROOT/'skills/codebase-map/scripts/render_report.py')
    fixture = load('kit_smoke_fixture', ROOT/'tests/kit_fixture.py')
    args.output.mkdir(parents=True)
    checks, errors, requests = [], [], []
    result = {'status': 'NOT_VERIFIED', 'checks': checks, 'limits': [
        'Synthetic catalogue, approval declarations and grey PNG bytes only; no real UI design or consent.',
        'No project, toolkit runtime, live agent, Windows profile or operating-system opener tested.',
        'Source matching is a freshness check; it does not prove the pixels were rendered by these components.']}
    try:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            data, _ = fixture.fixture(root)
            first = data['ui_review']['screens'][0]
            first['markers'] = [{'element': 'E1', 'position': [.5, .5]}]
            inp = root/'review-input.json'
            inp.write_text(json.dumps(data), encoding='utf-8')
            content = renderer.render(data, root, inp)
            output = args.output/'synthetic-kit-review.html'
            output.write_text(content, encoding='utf-8', newline='\n')
            assert renderer.check_report(output, root) == []
            checks.append('Report source/input/declared kit fingerprints match the synthetic fixture')
            with sync_playwright() as p:
                browser = p.chromium.launch(executable_path=str(args.browser), headless=True,
                    args=['--no-sandbox'] if args.no_sandbox else [])
                result['browser'] = browser.version
                context = browser.new_context(offline=True, viewport={'width': 1440, 'height': 1100})
                def instrument(page):
                    page.on('pageerror', lambda error: errors.append(str(error)))
                    page.on('request', lambda request: requests.append(request.url))
                    return page
                page = instrument(context.new_page())
                try:
                    page.goto(output.resolve().as_uri(), wait_until='load', timeout=15000)
                    result['direct_file_navigation'] = True
                except Exception as exc:
                    result['direct_file_navigation'] = False
                    result['limits'].append('file:// navigation blocked: '+str(exc).splitlines()[0]+'. Identical content tested offline.')
                    page.close(); page = instrument(context.new_page())
                    page.set_content(content, wait_until='load')
                page.locator('label[for="view-ui-preview"]').click()
                assert page.locator('#panel-ui-preview').is_visible()
                for label in ('What changes', 'What will not change', 'How completion will be checked', 'Technical evidence and task details'):
                    assert label in page.locator('body').inner_text()
                checks.append('Existing full report remains present with the additive source-bound screen view')
                assert page.locator('.ui-screen-node image').count() == 4
                assert not page.locator('.ui-review form,.ui-review input,.ui-review button,.ui-review iframe').count()
                checks.append('Capture screens are inert images, not injected app markup or approval controls')
                page.locator('.ui-screen-node a[aria-label="Inspect kit element E1"]').click()
                detail = page.locator('.ui-screen-detail').first
                assert detail.is_visible() and detail.get_attribute('open') is not None
                assert page.locator('.ui-screen-index').get_attribute('open') is not None
                row = detail.locator('tbody tr').first
                assert row.is_visible() and 'Save action' in row.inner_text()
                checks.append('Numbered element marker opens its exact component table without approving anything')
                text = detail.inner_text()
                for value in ('primary', 'component', 'settings', 'pattern', 'default / normal', 'src/Button.tsx', 'src/kit.stories.ts', 'Data and event wiring only.'):
                    assert value in text, value
                assert 'do not authenticate consent' in text
                checks.append('Exact IDs, component/pattern roles, variants, states, examples and source limits are visible')
                link = detail.locator('a').filter(has_text='src/Button.tsx').first
                target = link.get_attribute('href')
                link.click()
                assert page.locator(target).is_visible()
                checks.append('Component source links reveal matching snapshot records, including transitive inputs')
                page.locator('label[for="view-ui-preview"]').click()
                page.locator('.ui-inspect').first.click()
                page.set_viewport_size({'width': 390, 'height': 844})
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
                table = detail.locator('.table-scroll')
                assert table.evaluate('e=>e.scrollWidth>e.clientWidth')
                table.scroll_into_view_if_needed()
                page.screenshot(path=str(args.output/'mobile-kit-details.png'))
                checks.append('Mobile component details scroll inside their table without whole-page overflow')
                nojs_context = browser.new_context(offline=True, java_script_enabled=False, viewport={'width': 390, 'height': 844})
                nojs = instrument(nojs_context.new_page()); nojs.set_content(content, wait_until='load')
                nojs.locator('label[for="view-ui-preview"]').click()
                nojs.locator('.ui-screen-index>summary').click()
                nojs.locator('.ui-screen-detail>summary').first.click()
                assert nojs.locator('.ui-elements').first.is_visible()
                assert nojs.evaluate('document.documentElement.scrollWidth <= innerWidth')
                checks.append('Native disclosures and component references remain readable without JavaScript')
                nojs_context.close()
                assert not errors, errors
                assert not [x for x in requests if x.startswith(('http:', 'https:', 'ws:', 'wss:'))]
                checks.append('No network traffic, uploads or script exceptions')
                browser.close()
            original = output.read_bytes()
            (root/'src/Button.tsx').unlink()
            stale = renderer.check_report(output, root)
            assert stale and any('Button.tsx' in str(x) for x in stale)
            try:
                renderer.render(data, root, inp)
                raise AssertionError('Removed source unexpectedly accepted')
            except ValueError as exc:
                assert 'blocked' in str(exc).lower() or 'source' in str(exc).lower()
            assert original == output.read_bytes()
            checks.append('Deleted component blocks regeneration and flags freshness; historical HTML is unchanged')
        result['status'] = 'PASS'
        code = 0
        print(f'PASS: {len(checks)} source-bound kit/report checks; real application rendering and approval NOT TESTED.')
    except Exception as exc:
        result.update(status='FAIL', error=str(exc), error_type=type(exc).__name__)
        print('FAIL: '+repr(exc), file=sys.stderr)
        code = 1
    result['page_errors'] = errors
    (args.output/'results.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    return code


if __name__ == '__main__':
    raise SystemExit(main())
