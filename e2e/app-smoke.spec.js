import { test, expect } from '@playwright/test';

const routes = ['/', '/planner', '/map', '/analytics'];

for (const route of routes) {
  test(`renders DUO without a blank screen at ${route}`, async ({ page }) => {
    const pageErrors = [];
    const failedLocalAssets = [];

    page.on('pageerror', error => pageErrors.push(error.message));
    page.on('response', response => {
      const request = response.request();
      const isAppAsset = new URL(response.url()).origin === 'http://127.0.0.1:4173'
        && ['script', 'stylesheet'].includes(request.resourceType());
      if (isAppAsset && response.status() >= 400) {
        failedLocalAssets.push(`${response.status()} ${response.url()}`);
      }
    });

    const response = await page.goto(route, { waitUntil: 'domcontentloaded' });
    expect(response?.status(), 'document should load successfully').toBe(200);
    await expect(page.locator('#root')).toBeVisible();
    await expect.poll(async () => {
      return page.locator('#root').evaluate(root => root.innerText.trim().length);
    }, { message: 'React should render visible application content', timeout: 20_000 }).toBeGreaterThan(0);

    await expect(page).toHaveTitle(/DUO/);
    expect(pageErrors, 'browser JavaScript errors').toEqual([]);
    expect(failedLocalAssets, 'failed JavaScript or CSS assets').toEqual([]);
  });
}

test('welcome experience is accessible on first visit', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByRole('dialog', { name: 'Добро пожаловать в DUO' })).toBeVisible();
  await expect(page.getByRole('heading', { name: /Не просто.*Создать момент/ })).toBeVisible();
});
