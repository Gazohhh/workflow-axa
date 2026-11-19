import { test as base, expect } from '@playwright/test';
import type { Browser, BrowserContext } from '@playwright/test';
import { appendFileSync, existsSync, mkdirSync, readFileSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';

export type Settings = {
  localFile: string;
  devServer: string;
  backend: string;
  blockedHosts: string[];
  rewrite: Record<string, string>;
  alsoAllow: string[];
  loginFile: string;
  loginKeys: { user: string; password: string };
  viewport: { width: number; height: number };
  isMobile: boolean;
  hasTouch: boolean;
  pinBackendTo: string;
  artifacts: string;
  run: string;
  journeys: string;
};

export type Login = { user: string; password: string };

const LOCAL_HOSTS = ['localhost', '127.0.0.1', '[::1]'];
const LOOPBACK = /^(127\.\d+\.\d+\.\d+|::1)$/;

function hostOf(address: string, label: string): string {
  try {
    return new URL(address).hostname.toLowerCase().replace(/\.$/, '');
  } catch {
    throw new Error(`verify guard: ${label} "${address}" is not a full address such as http://localhost:8000`);
  }
}

function readKeyValues(file: string): Record<string, string> {
  const values: Record<string, string> = {};
  for (const line of readFileSync(file, 'utf8').split(/\r?\n/)) {
    const match = /^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*?)\s*$/.exec(line);
    if (match) {
      values[match[1]] = match[2].replace(/^(['"])(.*)\1$/, '$2');
    }
  }
  return values;
}

function originOf(address: string, label: string): string {
  hostOf(address, label);
  return new URL(address).origin;
}

export function loadSettings(path = process.env.VERIFY_SETTINGS): Settings {
  if (!path) {
    throw new Error('verify guard: VERIFY_SETTINGS is not set; point it at the verify skill settings.json');
  }
  const file = resolve(path);
  if (!existsSync(file)) {
    throw new Error(`verify guard: settings file ${file} does not exist`);
  }
  const raw = JSON.parse(readFileSync(file, 'utf8')) as Omit<Partial<Settings>, 'rewrite'> & { rewrite?: unknown };
  if (!raw.localFile) {
    throw new Error('verify guard: the settings need a localFile: an ignored file with this machine\'s VERIFY_BACKEND (machine values never go in the committed settings)');
  }
  const localPath = resolve(raw.localFile);
  if (!existsSync(localPath)) {
    throw new Error(`verify guard: the local settings file ${localPath} is missing; copy verify.local.example from the verify-app guard to it and fill VERIFY_BACKEND (and VERIFY_PIN_BACKEND_TO, VERIFY_DEV_SERVER when needed) for this machine`);
  }
  const local = readKeyValues(localPath);
  raw.backend = local.VERIFY_BACKEND ?? '';
  raw.pinBackendTo = local.VERIFY_PIN_BACKEND_TO ?? '';
  raw.devServer = local.VERIFY_DEV_SERVER || raw.devServer;
  const blockedHosts = (raw.blockedHosts ?? []).map((host) => host.toLowerCase().replace(/\.$/, ''));
  if (!raw.backend) {
    throw new Error('verify guard: no backend is set; refusing to start');
  }
  if (blockedHosts.length === 0 && !raw.pinBackendTo) {
    throw new Error('verify guard: blockedHosts is empty; list the production hosts so they can be refused (it may stay empty only when the backend is pinned and is the app\'s only production name)');
  }
  const backendHost = hostOf(raw.backend, 'backend');
  if (blockedHosts.includes(backendHost)) {
    throw new Error(`verify guard: backend ${backendHost} is a production host; refusing to start`);
  }
  const devHost = hostOf(raw.devServer ?? '', 'devServer');
  if (!LOCAL_HOSTS.includes(devHost)) {
    throw new Error(`verify guard: devServer must run on this machine, not ${devHost}`);
  }
  const backend = originOf(raw.backend, 'backend');
  const pinBackendTo = raw.pinBackendTo ?? '';
  if (pinBackendTo && !LOOPBACK.test(pinBackendTo)) {
    throw new Error(`verify guard: pinBackendTo must be a loopback address such as 127.0.0.1, not ${pinBackendTo}`);
  }
  if (raw.rewrite !== undefined && !(Array.isArray(raw.rewrite) && raw.rewrite.every((item) => typeof item === 'string'))) {
    throw new Error('verify guard: rewrite is a list of origins the app calls; each is sent to this machine\'s backend from the local file');
  }
  const rewrite: Record<string, string> = {};
  for (const from of (raw.rewrite as string[] | undefined) ?? []) {
    rewrite[originOf(from, 'rewrite source')] = backend;
  }
  const alsoAllow = (raw.alsoAllow ?? []).map((address) => originOf(address, 'alsoAllow'));
  for (const origin of alsoAllow) {
    if (!LOCAL_HOSTS.includes(hostOf(origin, 'alsoAllow'))) {
      throw new Error(`verify guard: alsoAllow takes only addresses on this machine (localhost, 127.0.0.1, [::1]), not ${origin}`);
    }
  }
  if (!raw.loginFile || !raw.loginKeys) {
    throw new Error('verify guard: loginFile and loginKeys are required');
  }
  if (!pinBackendTo && !LOCAL_HOSTS.includes(backendHost)) {
    throw new Error(`verify guard: backend ${backendHost} is a name, not this machine; it needs VERIFY_PIN_BACKEND_TO (127.0.0.1 or ::1) so the browser can only reach it here`);
  }
  if (pinBackendTo && Object.keys(rewrite).length > 0) {
    throw new Error('verify guard: a pinned backend cannot be combined with rewrite; Playwright would resolve the rewritten host again outside the browser');
  }
  const run = process.env.VERIFY_RUN;
  if (!run || !/^(?!\.{1,2}$)[A-Za-z0-9._-]+$/.test(run)) {
    throw new Error('verify guard: VERIFY_RUN must name this run (letters, digits, dot, dash, underscore; not "." or "..")');
  }
  if (/^(worktrees|journeys)(\.md)?$/i.test(run)) {
    throw new Error(`verify guard: the run name "${run}" is kept for the artifacts folder's shared worktrees and journeys; give this run another name`);
  }
  const inRunner = process.env.TEST_WORKER_INDEX === undefined;
  if (inRunner) {
    const artifactsRoot = resolve(raw.artifacts ?? '.artifacts/verify');
    mkdirSync(artifactsRoot, { recursive: true });
    const claimed = join(artifactsRoot, run);
    try {
      mkdirSync(claimed, { recursive: false });
    } catch {
      throw new Error(`verify guard: run folder ${claimed} already exists; give this run a new VERIFY_RUN name`);
    }
  }
  return {
    localFile: raw.localFile ?? '',
    devServer: originOf(raw.devServer as string, 'devServer'),
    backend,
    blockedHosts,
    rewrite,
    alsoAllow,
    loginFile: raw.loginFile,
    loginKeys: raw.loginKeys,
    viewport: raw.viewport ?? { width: 390, height: 844 },
    isMobile: raw.isMobile ?? true,
    hasTouch: raw.hasTouch ?? true,
    pinBackendTo,
    artifacts: resolve(raw.artifacts ?? '.artifacts/verify'),
    run,
    journeys: resolve(process.env.VERIFY_JOURNEYS ?? join(raw.artifacts ?? '.artifacts/verify', 'journeys', run)),
  };
}

export const settings = loadSettings();

export const runFolder = join(settings.artifacts, settings.run);

export const skillFolder = process.env.VERIFY_SKILL || dirname(resolve(process.env.VERIFY_SETTINGS ?? ''));

export function hostResolverRule(): string {
  const reachable = new Set([
    ...LOCAL_HOSTS,
    ...(settings.pinBackendTo ? [] : [new URL(settings.backend).hostname]),
    ...settings.alsoAllow.map((origin) => new URL(origin).hostname),
  ]);
  if (settings.pinBackendTo) {
    reachable.delete(new URL(settings.backend).hostname);
  }
  const pinTarget = settings.pinBackendTo.includes(':') ? `[${settings.pinBackendTo}]` : settings.pinBackendTo;
  const pin = settings.pinBackendTo ? `MAP ${new URL(settings.backend).hostname} ${pinTarget}, ` : '';
  return `--host-resolver-rules=${pin}MAP * ~NOTFOUND, ${[...reachable].map((host) => `EXCLUDE ${host}`).join(', ')}`;
}

function log(kind: 'rewritten' | 'blocked' | 'escaped' | 'failed', detail: string): void {
  mkdirSync(runFolder, { recursive: true });
  appendFileSync(join(runFolder, 'network.log'), `${new Date().toISOString()} ${kind} ${detail}\n`);
}

export function readLogin(): Login {
  const file = resolve(settings.loginFile);
  if (!existsSync(file)) {
    throw new Error(`verify guard: login file ${file} does not exist; the owner puts the test login there`);
  }
  const values = readKeyValues(file);
  const user = values[settings.loginKeys.user];
  const password = values[settings.loginKeys.password];
  if (!user || !password) {
    throw new Error(`verify guard: ${settings.loginKeys.user} or ${settings.loginKeys.password} is missing in the login file`);
  }
  return { user, password };
}

let escapedThisTest: string[] = [];
const guardedContexts = new WeakSet<BrowserContext>();
const guardedBrowsers = new WeakSet<Browser>();

const REQUEST_METHODS = ['fetch', 'get', 'post', 'put', 'patch', 'delete', 'head'] as const;

export function guardRequests(api: Record<(typeof REQUEST_METHODS)[number], (url: unknown, options?: Record<string, unknown>) => Promise<unknown>>): void {
  const open = new Set([settings.devServer, settings.backend, ...settings.alsoAllow]);
  for (const method of REQUEST_METHODS) {
    const original = api[method].bind(api);
    api[method] = async (url: unknown, options?: Record<string, unknown>) => {
      const request = typeof url === 'string' ? null : url as { url: () => string; method: () => string; headers: () => Record<string, string>; postDataBuffer: () => Buffer | null };
      const address = new URL(request ? request.url() : url as string, settings.devServer);
      const ownBody = options && ['data', 'form', 'multipart'].some((key) => options[key] !== undefined);
      const carried = request
        ? { method: request.method(), headers: request.headers(), ...(ownBody ? {} : { data: request.postDataBuffer() ?? undefined }) }
        : {};
      const target = open.has(address.origin) ? address.origin : settings.rewrite[address.origin];
      if (!target) {
        log('blocked', `REQUEST ${method.toUpperCase()} ${address.origin}`);
        throw new Error(`verify guard: ${address.origin} is not an allowed origin for a request from the test`);
      }
      if (target !== address.origin) {
        log('rewritten', `REQUEST ${method.toUpperCase()} ${address.origin} -> ${target}`);
      }
      try {
        return await original(`${target}${address.pathname}${address.search}`, { ...carried, ...options, maxRedirects: 0 });
      } catch (error) {
        log('failed', `REQUEST ${method.toUpperCase()} ${target}`);
        throw error;
      }
    };
  }
}

async function guardContext(context: BrowserContext): Promise<void> {
  if (guardedContexts.has(context)) {
    return;
  }
  guardedContexts.add(context);
  guardRequests(context.request as unknown as Parameters<typeof guardRequests>[0]);
  const open = new Set([settings.devServer, settings.backend, ...settings.alsoAllow]);
  context.on('requestfailed', (request) => {
    const url = new URL(request.url());
    const reason = request.failure()?.errorText ?? '';
    if (!['net::ERR_BLOCKED_BY_CLIENT', 'net::ERR_ABORTED'].includes(reason) && url.protocol.startsWith('http')) {
      log('failed', `${request.method()} ${url.origin}`);
    }
  });
  context.on('request', (request) => {
    if (!request.redirectedFrom()) {
      return;
    }
    const url = new URL(request.url());
    if (!open.has(url.origin) && url.protocol !== 'data:' && url.protocol !== 'blob:') {
      log('escaped', `${request.method()} ${url.origin} (redirect hop, not checked by the route)`);
      escapedThisTest.push(url.origin);
    }
  });
  await context.routeWebSocket(/.*/, (socket) => {
    const url = new URL(socket.url());
    const httpOrigin = `${url.protocol === 'wss:' ? 'https:' : 'http:'}//${url.host}`;
    if (open.has(httpOrigin)) {
      socket.connectToServer();
      return;
    }
    log('blocked', `WEBSOCKET ${httpOrigin}`);
    socket.close({ code: 1008, reason: 'blocked by the verify guard' });
  });
  await context.route('**/*', async (route) => {
    const url = new URL(route.request().url());
    if (url.protocol === 'data:' || url.protocol === 'blob:') {
      return route.continue();
    }
    if (open.has(url.origin)) {
      return route.continue();
    }
    const target = settings.rewrite[url.origin];
    if (target) {
      const rewritten = `${target}${url.pathname}${url.search}`;
      log('rewritten', `${route.request().method()} ${url.origin} -> ${target}`);
      let response;
      try {
        response = await route.fetch({ url: rewritten, maxRedirects: 0 });
      } catch {
        log('failed', `${route.request().method()} ${url.origin} -> ${target}`);
        return route.abort('failed');
      }
      return route.fulfill({ response });
    }
    log('blocked', `${route.request().method()} ${url.origin}`);
    return route.abort('blockedbyclient');
  });
}

function guardBrowser(browser: Browser): void {
  if (guardedBrowsers.has(browser)) {
    return;
  }
  guardedBrowsers.add(browser);
  const newContext = browser.newContext.bind(browser);
  browser.newContext = async (options) => {
    const made = await newContext({ ...options, serviceWorkers: 'block' });
    await guardContext(made);
    return made;
  };
  browser.newPage = async (options) => {
    const made = await browser.newContext(options);
    const page = await made.newPage();
    page.on('close', () => { void made.close(); });
    return page;
  };
}

export const test = base.extend<{ login: Login; verifyGuard: void }>({
  browser: [async ({ browser }, use) => {
    guardBrowser(browser);
    await use(browser);
  }, { scope: 'worker' }],
  verifyGuard: [async ({}, use) => {
    escapedThisTest = [];
    await use();
    if (escapedThisTest.length > 0) {
      throw new Error(`verify guard: a redirect reached ${escapedThisTest[0]} outside the allowed origins; this run's evidence does not count`);
    }
  }, { auto: true }],
  request: async ({ request }, use) => {
    guardRequests(request as unknown as Parameters<typeof guardRequests>[0]);
    await use(request);
  },
  context: async ({ context }, use) => {
    await guardContext(context);
    await use(context);
  },
  login: async ({}, use) => {
    await use(readLogin());
  },
});

export { expect };
