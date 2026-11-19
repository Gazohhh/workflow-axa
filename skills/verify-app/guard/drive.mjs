import { spawnSync } from 'node:child_process';
import { existsSync, readFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import { dirname, join, resolve } from 'node:path';
import { cleanCliFolder, cutQueries } from './redact.mjs';

const ALLOWED = new Set([
  'attach', 'detach', 'snapshot', 'find', 'eval', 'screenshot',
  'click', 'dblclick', 'fill', 'type', 'press', 'keydown', 'keyup', 'hover', 'select', 'check', 'uncheck', 'drag',
  'mousemove', 'mousedown', 'mouseup', 'mousewheel', 'resize', 'dialog-accept', 'dialog-dismiss',
  'goto', 'go-back', 'go-forward', 'reload', 'tab-list', 'tab-select',
]);

const [run, command, ...rest] = process.argv.slice(2);
const fail = (message) => {
  console.error(`verify driver: ${message}`);
  process.exit(2);
};

if (!run || !command) {
  fail('usage: node <verify skill>/drive.mjs <run name> <command> [arguments]');
}
if (!/^(?!\.{1,2}$)[A-Za-z0-9._-]+$/.test(run)) {
  fail(`"${run}" is not a run name`);
}
if (!ALLOWED.has(command)) {
  fail(`"${command}" is not allowed through the verify driver; it only takes screen actions and read-only looks (${[...ALLOWED].join(', ')})`);
}
if (rest.some((arg) => arg.startsWith('-'))) {
  fail('options are not allowed through the verify driver (no --config, session, output file or other flags)');
}
if (command === 'goto' && !/^https?:\/\//i.test(rest[0] ?? '')) {
  fail('goto only takes an http or https address');
}
const settingsPath = process.env.VERIFY_SETTINGS;
if (!settingsPath || !existsSync(settingsPath)) {
  fail('VERIFY_SETTINGS must point at the verify skill settings.json');
}
const settings = JSON.parse(readFileSync(settingsPath, 'utf8'));
const runFolder = resolve(settings.artifacts ?? '.artifacts/verify', run);
if (!existsSync(join(runFolder, 'explore.md'))) {
  fail(`no explore session was started for "${run}" (missing ${join(runFolder, 'explore.md')})`);
}
if (existsSync(join(runFolder, 'explore-result.md')) || existsSync(join(runFolder, 'stop'))) {
  fail(`the explore session for "${run}" has ended; start a new run`);
}
const sessionLine = /^Session: (\S+)$/m.exec(readFileSync(join(runFolder, 'explore.md'), 'utf8'));
if (!sessionLine) {
  fail(`explore.md for "${run}" names no session`);
}
const session = sessionLine[1];
const testPackage = resolve('node_modules', '@playwright', 'test', 'package.json');
const cli = existsSync(testPackage)
  ? join(dirname(createRequire(testPackage).resolve('playwright/package.json')), 'cli.js')
  : resolve('node_modules', 'playwright', 'cli.js');
cleanCliFolder(runFolder);
const result = spawnSync(process.execPath, [cli, 'cli', `-s=${session}`, command, ...(command === 'attach' ? [session] : []), ...rest], {
  cwd: runFolder,
  stdio: ['inherit', 'pipe', 'pipe'],
  encoding: 'utf8',
  maxBuffer: 64 * 1024 * 1024,
});
cleanCliFolder(runFolder);
process.stdout.write(cutQueries(result.stdout ?? ''));
process.stderr.write(cutQueries(result.stderr ?? ''));
process.exitCode = result.status ?? 1;
