import { spawnSync } from 'node:child_process';
import { existsSync } from 'node:fs';
import { dirname, join, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const fail = (message) => {
  console.error(`verify runner: ${message}`);
  process.exit(2);
};

const args = process.argv.slice(2);
const settingsPath = process.env.VERIFY_SETTINGS;
if (!settingsPath || !existsSync(settingsPath)) {
  fail('VERIFY_SETTINGS must point at the verify skill settings.json');
}
const ALLOWED = new Set(['--grep', '-g', '--grep-invert', '--list', '--repeat-each', '--headed', '--max-failures', '-x', '--timeout']);
for (const arg of args) {
  if (arg.startsWith('-') && !ALLOWED.has(arg.split('=')[0])) {
    fail(`"${arg}" is not allowed through the verify runner; it takes only journey files and ${[...ALLOWED].join(', ')} (the skill's config fixes the browser, reporter, output folder and snapshots)`);
  }
}
const skillFolder = dirname(fileURLToPath(import.meta.url));
const config = relative(process.cwd(), join(skillFolder, 'playwright.config.ts'));
const cli = resolve('node_modules', '@playwright', 'test', 'cli.js');
const env = Object.fromEntries(Object.entries(process.env)
  .filter(([key]) => !/^(https?_proxy|all_proxy|node_use_env_proxy|global_agent_.*|pw_test_connect_.*)$/i.test(key)));
const result = spawnSync(process.execPath, [cli, 'test', '--config', config, ...args], {
  stdio: 'inherit',
  env: { ...env, VERIFY_SKILL: skillFolder },
});
if (result.error) {
  fail(`could not start Playwright: ${result.error.message}`);
}
process.exitCode = result.status ?? 1;
