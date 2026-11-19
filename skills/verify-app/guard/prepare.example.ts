import type { Page } from '@playwright/test';
import type { Login } from '../guard';

export async function prepare(page: Page, login: Login): Promise<void> {
  await page.goto('/');
  void login;
}
