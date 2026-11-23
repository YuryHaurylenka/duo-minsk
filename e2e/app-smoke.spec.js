import { test, expect } from '@playwright/test';

const licensedPlaces = [
  {
    id: 'library-fixture', slug: 'национальная-библиотека-беларуси-смотровая-площадка', city_slug: 'minsk',
    name: 'Национальная библиотека Беларуси — смотровая площадка', category: 'Видовые места',
    description: 'Панорама Минска со смотровой площадки.', address: 'пр-т Независимости, 116, Минск',
    rating: '4.8', reviews: '240', price_label: 'Уточнить стоимость',
    image_url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/91/View_of_Minsk_from_the_National_Library_of_Belarus_01.JPG/1280px-View_of_Minsk_from_the_National_Library_of_Belarus_01.JPG',
    image_source_url: 'https://commons.wikimedia.org/wiki/File:View_of_Minsk_from_the_National_Library_of_Belarus_01.JPG',
  },
  {
    id: 'museum-fixture', slug: 'музеи-истории-великои-отечественнои-воины', city_slug: 'minsk',
    name: 'Музей истории Великой Отечественной войны', category: 'Музеи и выставки',
    description: 'Музей истории войны и памятные экспозиции.', address: 'пр-т Победителей, 8, Минск',
    rating: '4.9', reviews: '900', price_label: 'Уточнить стоимость',
    image_url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/3/35/Museum_of_the_Great_Patriotic_War_-_Minsk_-_Belarus_%2827248715740%29.jpg/1280px-Museum_of_the_Great_Patriotic_War_-_Minsk_-_Belarus_%2827248715740%29.jpg',
    image_source_url: 'https://commons.wikimedia.org/wiki/File:Museum_of_the_Great_Patriotic_War_-_Minsk_-_Belarus_(27248715740).jpg',
  },
  {
    id: 'art-museum-fixture', slug: 'национальныи-художественныи-музеи', city_slug: 'minsk',
    name: 'Национальный художественный музей', category: 'Музеи и выставки',
    description: 'Коллекция белорусского и зарубежного искусства.', address: 'ул. Ленина, 20, Минск',
    rating: '4.4', reviews: '343', price_label: 'Уточнить стоимость',
    image_url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/0/0a/%D0%9D%D0%B0%D1%86%D1%8B%D1%8F%D0%BD%D0%B0%D0%BB%D1%8C%D0%BD%D1%8B_%D0%BC%D0%B0%D1%81%D1%82%D0%B0%D1%86%D0%BA%D1%96_%D0%BC%D1%83%D0%B7%D0%B5%D0%B9_%D0%A0%D1%8D%D1%81%D0%BF%D1%83%D0%B1%D0%BB%D1%96%D0%BA%D1%96_%D0%91%D0%B5%D0%BB%D0%B0%D1%80%D1%83%D1%81%D1%8C.jpg/1280px-%D0%9D%D0%B0%D1%86%D1%8B%D1%8F%D0%BD%D0%B0%D0%BB%D1%8C%D0%BD%D1%8B_%D0%BC%D0%B0%D1%81%D1%82%D0%B0%D1%86%D0%BA%D1%96_%D0%BC%D1%83%D0%B7%D0%B5%D0%B9_%D0%A0%D1%8D%D1%81%D0%BF%D1%83%D0%B1%D0%BB%D1%96%D0%BA%D1%96_%D0%91%D0%B5%D0%BB%D0%B0%D1%80%D1%83%D1%81%D1%8C.jpg',
    image_source_url: 'https://commons.wikimedia.org/wiki/File:Нацыянальны_мастацкі_музей_Рэспублікі_Беларусь.jpg',
  },
  {
    id: 'theatre-fixture', slug: 'большои-театр-беларуси', city_slug: 'minsk',
    name: 'Большой театр Беларуси', category: 'Театры и кино',
    description: 'Национальный академический театр оперы и балета.', address: 'пл. Парижской Коммуны, 1, Минск',
    rating: '4.7', reviews: '413', price_label: 'Уточнить стоимость',
    image_url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/3/38/Minsk_ParizhskoyKommuny1_001_4213.jpg/1280px-Minsk_ParizhskoyKommuny1_001_4213.jpg', image_source_url: 'https://commons.wikimedia.org/wiki/File:Minsk_ParizhskoyKommuny1_001_4213.jpg',
  },
  {
    id: 'trinity-fixture', slug: 'троицкое-предместье', city_slug: 'minsk',
    name: 'Троицкое предместье', category: 'Видовые места',
    description: 'Исторический квартал у Свислочи.', address: 'ул. Богдановича, Минск',
    rating: '4.8', reviews: '200', price_label: 'Бесплатно',
    image_url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/ec/Minsk_TrinityHill_001_3864.jpg/1280px-Minsk_TrinityHill_001_3864.jpg', image_source_url: 'https://commons.wikimedia.org/wiki/File:Minsk_TrinityHill_001_3864.jpg',
  },
  {
    id: 'island-fixture', slug: 'остров-слез', city_slug: 'minsk',
    name: 'Остров слёз', category: 'Видовые места',
    description: 'Мемориал на берегу Свислочи.', address: 'Старовиленский тракт, Минск',
    rating: '4.8', reviews: '120', price_label: 'Бесплатно',
    image_url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Minsk_TearsIsland_001_3847.jpg/1280px-Minsk_TearsIsland_001_3847.jpg',
    image_source_url: 'https://commons.wikimedia.org/wiki/File:Minsk_TearsIsland_001_3847.jpg',
  },
  {
    id: 'botanical-fixture', slug: 'центральныи-ботаническии-сад', city_slug: 'minsk',
    name: 'Центральный ботанический сад', category: 'Прогулки',
    description: 'Сад и прогулочные маршруты.', address: 'ул. Сурганова, 2В, Минск',
    rating: '0', reviews: '0', price_label: 'Уточнить стоимость',
    image_url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/bf/2026.06.26_%D0%91%D0%BE%D1%82%D0%B0%D0%BD%D0%B8%D1%87%D0%B5%D1%81%D0%BA%D0%B8%D0%B9_%D1%81%D0%B0%D0%B4_%D0%B2_%D0%9C%D0%B8%D0%BD%D1%81%D0%BA%D0%B5%2C_%D0%91%D0%B5%D0%BB%D0%B0%D1%80%D1%83%D1%81%D1%8C_22.jpg/1280px-2026.06.26_%D0%91%D0%BE%D1%82%D0%B0%D0%BD%D0%B8%D1%87%D0%B5%D1%81%D0%BA%D0%B8%D0%B9_%D1%81%D0%B0%D0%B4_%D0%B2_%D0%9C%D0%B8%D0%BD%D1%81%D0%BA%D0%B5%2C_%D0%91%D0%B5%D0%BB%D0%B0%D1%80%D1%83%D1%81%D1%8C_22.jpg',
    image_source_url: 'https://commons.wikimedia.org/wiki/File:2026.06.26_Ботанический_сад_в_Минске,_Беларусь_22.jpg',
  },
  {
    id: 'planetarium-fixture', slug: 'минскии-планетарии', city_slug: 'minsk',
    name: 'Минский планетарий', category: 'Музеи и выставки',
    description: 'Планетарий и обсерватория в парке Горького.', address: 'ул. Фрунзе, 2, Минск',
    rating: '4.7', reviews: '500', price_label: 'Уточнить стоимость',
    image_url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/77/Minsk_Planetarium.jpg/1280px-Minsk_Planetarium.jpg',
    image_source_url: 'https://commons.wikimedia.org/wiki/File:Minsk_Planetarium.jpg',
  },
  {
    id: 'zoo-fixture', slug: 'минскии-зоопарк', city_slug: 'minsk',
    name: 'Минский зоопарк', category: 'Парки развлечений',
    description: 'Зоопарк Минска.', address: 'ул. Ташкентская, 40, Минск',
    rating: '4.6', reviews: '700', price_label: 'Уточнить стоимость',
    image_url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/0/0c/%D0%9C%D0%B8%D0%BD%D1%81%D0%BA%D0%B8%D0%B9_%D0%B7%D0%BE%D0%BE%D0%BF%D0%B0%D1%80%D0%BA_-_%D0%BF%D0%B0%D0%B2%D0%BB%D0%B8%D0%BD.jpg/1280px-%D0%9C%D0%B8%D0%BD%D1%81%D0%BA%D0%B8%D0%B9_%D0%B7%D0%BE%D0%BE%D0%BF%D0%B0%D1%80%D0%BA_-_%D0%BF%D0%B0%D0%B2%D0%BB%D0%B8%D0%BD.jpg',
    image_source_url: 'https://commons.wikimedia.org/wiki/File:Минский_зоопарк_-_павлин.jpg',
  },
  {
    id: 'art-museum-fixture', slug: 'национальныи-художественныи-музеи', city_slug: 'minsk',
    name: 'Национальный художественный музей', category: 'Музеи и выставки',
    description: 'Национальный художественный музей Беларуси.', address: 'ул. Ленина, 20, Минск',
    rating: '4.8', reviews: '500', price_label: 'Уточнить стоимость',
    image_url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/0/0a/%D0%9D%D0%B0%D1%86%D1%8B%D1%8F%D0%BD%D0%B0%D0%BB%D1%8C%D0%BD%D1%8B_%D0%BC%D0%B0%D1%81%D1%82%D0%B0%D1%86%D0%BA%D1%96_%D0%BC%D1%83%D0%B7%D0%B5%D0%B9_%D0%A0%D1%8D%D1%81%D0%BF%D1%83%D0%B1%D0%BB%D1%96%D0%BA%D1%96_%D0%91%D0%B5%D0%BB%D0%B0%D1%80%D1%83%D1%81%D1%8C.jpg/1280px-%D0%9D%D0%B0%D1%86%D1%8B%D1%8F%D0%BD%D0%B0%D0%BB%D1%8C%D0%BD%D1%8B_%D0%BC%D0%B0%D1%81%D1%82%D0%B0%D1%86%D0%BA%D1%96_%D0%BC%D1%83%D0%B7%D0%B5%D0%B9_%D0%A0%D1%8D%D1%81%D0%BF%D1%83%D0%B1%D0%BB%D1%96%D0%BA%D1%96_%D0%91%D0%B5%D0%BB%D0%B0%D1%80%D1%83%D1%81%D1%8C.jpg',
    image_source_url: 'https://commons.wikimedia.org/wiki/File:Нацыянальны_мастацкі_музей_Рэспублікі_Беларусь.jpg',
  },
  {
    id: 'botanical-fixture', slug: 'центральныи-ботаническии-сад', city_slug: 'minsk',
    name: 'Центральный ботанический сад', category: 'Парки',
    description: 'Ботанический сад Минска.', address: 'ул. Сурганова, 2В, Минск',
    rating: '4.7', reviews: '300', price_label: 'Уточнить стоимость',
    image_url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/bf/2026.06.26_%D0%91%D0%BE%D1%82%D0%B0%D0%BD%D0%B8%D1%87%D0%B5%D1%81%D0%BA%D0%B8%D0%B9_%D1%81%D0%B0%D0%B4_%D0%B2_%D0%9C%D0%B8%D0%BD%D1%81%D0%BA%D0%B5%2C_%D0%91%D0%B5%D0%BB%D0%B0%D1%80%D1%83%D1%81%D1%8C_22.jpg/1280px-2026.06.26_%D0%91%D0%BE%D1%82%D0%B0%D0%BD%D0%B8%D1%87%D0%B5%D1%81%D0%BA%D0%B8%D0%B9_%D1%81%D0%B0%D0%B4_%D0%B2_%D0%9C%D0%B8%D0%BD%D1%81%D0%BA%D0%B5%2C_%D0%91%D0%B5%D0%BB%D0%B0%D1%80%D1%83%D1%81%D1%8C_22.jpg',
    image_source_url: 'https://commons.wikimedia.org/wiki/File:2026.06.26_Ботанический_сад_в_Минске,_Беларусь_22.jpg',
  },,
  {
    id: 'chizhovka-fixture', slug: 'чижовка-арена', city_slug: 'minsk',
    name: 'Чижовка-Арена', category: 'Лёд',
    description: 'Ледовая арена в Минске.', address: 'ул. Ташкентская, 19, Минск',
    rating: '5.0', reviews: '2927', price_label: 'Уточнить стоимость',
    image_url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/77/Chizhovka-Arena_inside_1.jpg/1280px-Chizhovka-Arena_inside_1.jpg',
    image_source_url: 'https://commons.wikimedia.org/wiki/File:Chizhovka-Arena_inside_1.jpg',
  },
];

async function mockCatalogApi(page) {
  await page.route('**/api/**', route => {
    const path = new URL(route.request().url()).pathname;
    if (path.endsWith('/cities')) {
      return route.fulfill({ json: [{ slug: 'minsk', name_localized: 'Минск', timezone: 'Europe/Minsk' }] });
    }
    if (path.endsWith('/places')) return route.fulfill({ json: licensedPlaces });
    if (path.endsWith('/events') || path.endsWith('/updates')) return route.fulfill({ json: [] });
    return route.fulfill({ json: [] });
  });
}

const routes = ['/', '/planner', '/map', '/analytics'];

async function openCatalogue(page) {
  await page.addInitScript(() => sessionStorage.setItem('duoEntrySeen', '1'));
  await page.goto('/places');
}


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
  await mockCatalogApi(page);
  await openCatalogue(page);
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
  await mockCatalogApi(page);
  await openCatalogue(page);
  for (const item of [
    { query: 'Национальная библиотека', author: 'Хомелка', license: 'https://creativecommons.org/licenses/by-sa/3.0/' },
    { query: 'Музей истории Великой Отечественной войны', author: 'Adam Jones', license: 'https://creativecommons.org/licenses/by-sa/2.0/' },
    { query: 'Национальный художественный музей', author: 'DBatura', license: 'https://creativecommons.org/publicdomain/zero/1.0/' },
    { query: 'Центральный ботанический сад', author: 'Mila Chibireva', license: 'https://creativecommons.org/licenses/by-sa/4.0/' },
    { query: 'Остров слёз', author: 'Ludvig14', license: 'https://creativecommons.org/licenses/by-sa/4.0/' },
    { query: 'Троицкое предместье', author: 'Ludvig14', license: 'https://creativecommons.org/licenses/by-sa/4.0/' },
    { query: 'Большой театр Беларуси', author: 'Ludvig14', license: 'https://creativecommons.org/licenses/by-sa/4.0/' },
    { query: 'Минский зоопарк', author: 'SStraySpirit', license: 'https://creativecommons.org/licenses/by-sa/4.0/' },
    { query: 'Минский планетарий', author: 'Minsk Planetarium', license: 'https://creativecommons.org/licenses/by-sa/2.0/' },
    { query: 'Чижовка-Арена', author: 'Homoatrox', license: 'https://creativecommons.org/licenses/by-sa/3.0/' },
  ]) {
    const card = page.locator('.place-card').filter({ hasText: item.query }).first();
    await expect(card).toBeVisible({ timeout: 15_000 });
    await card.click();
    const credits = page.locator('.detail-image .image-attribution a');
    await expect(credits).toHaveCount(2);
    await expect(credits.nth(0)).toContainText(item.author);
    await expect(credits.nth(1)).toHaveAttribute('href', item.license);
    const detailImage = page.locator('.detail-image .image-cover img');
    await expect.poll(() => detailImage.evaluate(image => image.complete && image.naturalWidth > 0), { timeout: 20_000 }).toBe(true);
    await page.getByRole('button', { name: 'Закрыть окно' }).click();
  }
});


test('broken venue photos fall back to an explicitly labelled category illustration', async ({ page }) => {
  await mockCatalogApi(page);
  await page.addInitScript(() => sessionStorage.setItem('duoEntrySeen', '1'));
  await page.route('https://upload.wikimedia.org/**', route => route.abort());
  await page.route('https://images.unsplash.com/**', route => route.fulfill({
    status: 200,
    contentType: 'image/svg+xml',
    body: '<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32"><rect width="32" height="32" fill="#777"/></svg>',
  }));
  await page.goto('/places');
  await expect(page.locator('.place-card').first()).toBeVisible({ timeout: 20_000 });
  const imageCover = page.locator('.place-card .image-cover').first();
  await expect(imageCover).toHaveAttribute('data-image-kind', 'category-illustration');
  await expect(imageCover.locator('.image-illustration-label')).toBeVisible();
  await expect(imageCover.locator('img')).toHaveAttribute('alt', /Иллюстрация категории/);
});
