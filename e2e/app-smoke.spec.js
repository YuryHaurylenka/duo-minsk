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


test('catalogue cards and detail modal fit desktop and mobile viewports', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('button', { name: 'Открыть DUO' }).click();
  const firstCard = page.locator('.place-card').first();
  await expect(firstCard).toBeVisible({ timeout: 20_000 });

  const checkNoHorizontalOverflow = async () => {
    const metrics = await page.evaluate(() => ({
      viewport: document.documentElement.clientWidth,
      document: document.documentElement.scrollWidth,
      cardRight: document.querySelector('.place-card')?.getBoundingClientRect().right ?? 0,
    }));
    expect(metrics.document, 'page should not scroll horizontally').toBeLessThanOrEqual(metrics.viewport + 1);
    expect(metrics.cardRight, 'catalogue card should stay inside viewport').toBeLessThanOrEqual(metrics.viewport + 1);
  };

  await checkNoHorizontalOverflow();
  const imageAltTexts = await page.locator('.place-card .image-cover img').evaluateAll(images => images.map(image => image.alt.trim()));
  expect(imageAltTexts.every(Boolean), 'catalogue images should have descriptive alt text').toBeTruthy();

  await page.setViewportSize({ width: 390, height: 844 });
  await checkNoHorizontalOverflow();
  await firstCard.click();
  const detail = page.getByRole('dialog', { name: 'Окно DUO' });
  await expect(detail).toBeVisible();
  const modalBounds = await detail.boundingBox();
  expect(modalBounds).not.toBeNull();
  expect(modalBounds.x).toBeGreaterThanOrEqual(0);
  expect(modalBounds.x + modalBounds.width).toBeLessThanOrEqual(391);
});


test('licensed catalogue photos show author and direct license links', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('button', { name: 'Открыть DUO' }).click();
  await page.getByRole('button', { name: 'Смотреть места' }).click();
  const search = page.locator('input[aria-label="Поиск по местам"]');

  for (const item of [
    { query: 'Национальная библиотека', author: 'Хомелка', license: 'https://creativecommons.org/licenses/by-sa/3.0/' },
    { query: 'Музей истории Великой Отечественной войны', author: 'Adam Jones', license: 'https://creativecommons.org/licenses/by-sa/2.0/' },
  ]) {
    await search.fill(item.query);
    const card = page.locator('.place-card').filter({ hasText: item.query }).first();
    await expect(card).toBeVisible({ timeout: 15_000 });
    await card.click();
    const credits = page.locator('.detail-image .image-attribution a');
    await expect(credits).toHaveCount(2);
    await expect(credits.nth(0)).toContainText(item.author);
    await expect(credits.nth(1)).toHaveAttribute('href', item.license);
    await page.getByRole('button', { name: 'Закрыть окно' }).click();
  }
});
