import { lookup } from 'node:dns/promises';
import { settings } from './guard';

const LOOPBACK = /^(127\.\d+\.\d+\.\d+|::1)$/;

export default async function globalSetup(): Promise<void> {
  if (!settings.pinBackendTo) {
    return;
  }
  const host = new URL(settings.backend).hostname;
  const addresses = await lookup(host, { all: true });
  const elsewhere = addresses.filter((entry) => !LOOPBACK.test(entry.address));
  if (addresses.length === 0 || elsewhere.length > 0) {
    throw new Error(
      `verify guard: backend ${host} does not resolve to this machine; refusing to start ` +
        `(resolved to ${addresses.map((entry) => entry.address).join(', ') || 'nothing'})`,
    );
  }
}
