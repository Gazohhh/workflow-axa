import { spawnSync } from 'node:child_process';
import { existsSync, writeFileSync } from 'node:fs';
import { join, relative } from 'node:path';
import { runFolder, settings, skillFolder, test } from '../guard';
import { prepare } from './prepare';

const MINUTES = Number(process.env.VERIFY_EXPLORE_MINUTES ?? '30');

test.afterEach(() => {
  if (!existsSync(join(runFolder, 'explore-result.md'))) {
    writeFileSync(join(runFolder, 'explore-result.md'), 'ended: setup failed\n');
  }
});

test('explore: a guarded, logged-in browser shared for step-by-step driving', async ({ browser, page, login }) => {
  if (!Number.isInteger(MINUTES) || MINUTES < 1 || MINUTES > 120) {
    throw new Error('VERIFY_EXPLORE_MINUTES must be a whole number from 1 to 120');
  }
  test.setTimeout((MINUTES + 4) * 60_000);
  const stopFile = join(runFolder, 'stop');
  const session = `${settings.run}-${process.pid}-${Date.now()}`;
  let ended = 'setup failed';
  let bound = false;
  try {
    await prepare(page, login);
    const shared = await browser.bind(session, { workspaceDir: runFolder });
    bound = true;
    const driver = relative(process.cwd(), join(skillFolder, 'drive.mjs'));
    writeFileSync(
      join(runFolder, 'explore.md'),
      [
        `Run: ${settings.run}`,
        `Session: ${session}`,
        `Shared browser: ${shared.endpoint}`,
        `From the repository root, with VERIFY_SETTINGS set as for the run:`,
        `  node ${driver} ${settings.run} attach`,
        `  node ${driver} ${settings.run} snapshot`,
        `  node ${driver} ${settings.run} click <ref>`,
        `  node ${driver} ${settings.run} screenshot`,
        'One action at a time; the driver refuses anything but screen actions and read-only looks.',
        `Stop: create the file ${stopFile}`,
        '',
      ].join('\n'),
    );
    const deadline = Date.now() + MINUTES * 60_000;
    while (!existsSync(stopFile) && Date.now() < deadline && !page.isClosed()) {
      await new Promise((resolve) => setTimeout(resolve, 1000));
    }
    if (page.isClosed()) {
      ended = 'lost its page';
    } else if (existsSync(stopFile)) {
      ended = 'stopped';
    } else {
      ended = 'expired';
    }
  } finally {
    if (bound) {
      try {
        await browser.unbind();
      } catch {
        ended = 'could not unbind the shared browser';
      }
    }
    const redacted = spawnSync(process.execPath, [join(skillFolder, 'redact.mjs'), runFolder], { stdio: 'inherit' });
    if (redacted.status !== 0) {
      ended = 'could not clean the CLI files';
    }
    writeFileSync(join(runFolder, 'explore-result.md'), `ended: ${ended}\n`);
  }
  if (ended !== 'stopped') {
    throw new Error(`explore session ${ended} before the stop file was created`);
  }
});
