import { defineConfig, devices } from '@playwright/test';
import { hostResolverRule, runFolder, settings } from './guard';

const device = process.env.VERIFY_DEVICE;
if (device && device !== 'desktop' && device !== 'mobile') {
  throw new Error('verify guard: VERIFY_DEVICE must be desktop or mobile');
}
const mobile = device ? device === 'mobile' : settings.isMobile;
const size = /^(\d+)x(\d+)$/.exec(process.env.VERIFY_VIEWPORT ?? '');
if (process.env.VERIFY_VIEWPORT && !size) {
  throw new Error('verify guard: VERIFY_VIEWPORT must look like 1280x800');
}

export default defineConfig({
  testDir: settings.journeys,
  globalSetup: './global-setup.ts',
  outputDir: `${runFolder}/output`,
  snapshotPathTemplate: `${runFolder}/snapshots/{testFilePath}/{arg}{ext}`,
  timeout: 180_000,
  workers: 1,
  retries: 0,
  reporter: [['list']],
  use: {
    browserName: 'chromium',
    baseURL: settings.devServer,
    viewport: size
      ? { width: Number(size[1]), height: Number(size[2]) }
      : device ? devices[device === 'mobile' ? 'Pixel 7' : 'Desktop Chrome'].viewport : settings.viewport,
    isMobile: mobile,
    userAgent: mobile ? devices['Pixel 7'].userAgent : undefined,
    hasTouch: device ? device === 'mobile' : settings.hasTouch,
    serviceWorkers: 'block',
    video: 'on',
    screenshot: 'on',
    trace: 'off',
    launchOptions: { args: [hostResolverRule(), '--no-proxy-server'] },
  },
});
