import { test, expect } from '@playwright/test';

const licensedPlaces = [
  {
    id: 'library-fixture', slug: 'национальная-библиотека-беларуси-смотровая-площадка', city_slug: 'minsk',
    name: 'Национальная библиотека Беларуси — смотровая площадка', category: 'Видовые места',
    description: 'Панорама Минска со смотровой площадки.', address: 'пр-т Независимости, 116, Минск',
    rating: '4.8', reviews: '240', price_label: 'Уточнить стоимость',
    website_url: 'https://www.google.com/search?q=National+Library+of+Belarus',
    source_url: 'https://www.google.com/maps/search/?api=1&query=National+Library+of+Belarus',
    latitude: 53.9315, longitude: 27.6465, location_verified_at: '2026-11-20T10:00:00Z', district: 'Первомайский',
    image_url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/91/View_of_Minsk_from_the_National_Library_of_Belarus_01.JPG/1280px-View_of_Minsk_from_the_National_Library_of_Belarus_01.JPG',
    image_source_url: 'https://commons.wikimedia.org/wiki/File:View_of_Minsk_from_the_National_Library_of_Belarus_01.JPG',
  },
  {
    id: 'museum-fixture', slug: 'музеи-истории-великои-отечественнои-воины', city_slug: 'minsk',
    name: 'Музей истории Великой Отечественной войны', category: 'Музеи и выставки',
    description: 'Музей истории войны и памятные экспозиции.', address: 'пр-т Победителей, 8, Минск',
    rating: '4.9', reviews: '900', price_label: 'Уточнить стоимость',
    website_url: 'https://yandex.by/maps/?ll=27.5362%2C53.9352',
    latitude: 53.9352, longitude: 27.5362, location_verified_at: '2026-11-20T10:00:00Z', district: 'Центральный',
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
    id: 'upper-town-fixture', slug: 'верхнии-город-и-площадь-свободы', city_slug: 'minsk',
    name: 'Верхний город', category: 'Видовые места', description: 'Исторический центр Минска.', address: 'пл. Свободы, Минск',
    image_url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/1d/Belarus-Minsk-Upper_Town-1.jpg/1280px-Belarus-Minsk-Upper_Town-1.jpg',
    image_source_url: 'https://commons.wikimedia.org/wiki/File:Belarus-Minsk-Upper_Town-1.jpg',
  },
  {
    id: 'chizhovka-fixture', slug: 'чижовка-арена', city_slug: 'minsk',
    name: 'Чижовка-Арена', category: 'Лёд', description: 'Ледовая арена Минска.', address: 'ул. Ташкентская, 19, Минск',
    image_url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/77/Chizhovka-Arena_inside_1.jpg/1280px-Chizhovka-Arena_inside_1.jpg',
    image_source_url: 'https://commons.wikimedia.org/wiki/File:Chizhovka-Arena_inside_1.jpg',
  },
  {
    id: 'azgur-fixture', slug: 'музеи-мастерская-заира-азгура', city_slug: 'minsk',
    name: 'Музей-мастерская Заира Азгура', category: 'Музеи и выставки', description: 'Мемориальный музей-мастерская скульптора.', address: 'ул. Азгура, 8, Минск',
    image_url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/Memorial_Museum-Workshop_of_Zair_Isakavi%C4%8D_Azhur_03.jpg/1280px-Memorial_Museum-Workshop_of_Zair_Isakavi%C4%8D_Azhur_03.jpg',
    image_source_url: 'https://commons.wikimedia.org/wiki/File:Memorial_Museum-Workshop_of_Zair_Isakavi%C4%8D_Azhur_03.jpg',
  },
  {
    id: 'gorky-fixture', slug: 'парк-горького', city_slug: 'minsk',
    name: 'Парк Горького', category: 'Прогулки', description: 'Центральный парк культуры и отдыха.', address: 'ул. Фрунзе, 2, Минск',
    image_url: 'https://upload.wikimedia.org/wikipedia/commons/5/57/Gorki_park%2C_Minsk1.JPG',
    image_source_url: 'https://commons.wikimedia.org/wiki/File:Gorki_park,_Minsk1.JPG',
  },
  {
    id: 'victory-park-fixture', slug: 'прогулка-по-парку-победы', city_slug: 'minsk',
    name: 'Прогулка по парку Победы', category: 'Прогулки', description: 'Парк Победы и виды на Комсомольское озеро.', address: 'пр-т Победителей, Минск',
    image_url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/cd/View_of_Victory_Park_Minsk.jpg/1280px-View_of_Victory_Park_Minsk.jpg',
    image_source_url: 'https://commons.wikimedia.org/wiki/File:View_of_Victory_Park_Minsk.jpg',
  },
  {
    id: 'loshitsky-fixture', slug: 'лошицкии-парк', city_slug: 'minsk',
    name: 'Лошицкий парк', category: 'Прогулки', description: 'Усадебный парк и исторические постройки.', address: 'Лошицкий парк, Минск',
    image_url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a8/2025.09.18_Loshitsky_Park%2C_Minsk.jpg/1280px-2025.09.18_Loshitsky_Park%2C_Minsk.jpg',
    image_source_url: 'https://commons.wikimedia.org/wiki/File:2025.09.18_Loshitsky_Park,_Minsk.jpg',
  },
  {
    id: 'kupala-theatre-fixture', slug: 'театр-имени-янки-купалы', city_slug: 'minsk',
    name: 'Театр имени Янки Купалы', category: 'Театры и кино', description: 'Национальный академический театр.', address: 'ул. Энгельса, 7, Минск',
    image_url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/86/Belarus-Minsk-Yanka_Kupala_National_Academic_Theatre.jpg/1280px-Belarus-Minsk-Yanka_Kupala_National_Academic_Theatre.jpg',
    image_source_url: 'https://commons.wikimedia.org/wiki/File:Belarus-Minsk-Yanka_Kupala_National_Academic_Theatre.jpg',
  },
  {
    id: 'national-history-fixture', slug: 'национальныи-историческии-музеи', city_slug: 'minsk',
    name: 'Национальный исторический музей', category: 'Музеи и выставки',
    description: 'Национальный исторический музей Беларуси.', address: 'ул. Карла Маркса, 12, Минск',
    image_url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/79/Belarus-Minsk-National_museum_of_history_and_culture_of_Belarus-Exterior.jpg/1280px-Belarus-Minsk-National_museum_of_history_and_culture_of_Belarus-Exterior.jpg',
    image_source_url: 'https://commons.wikimedia.org/wiki/File:Belarus-Minsk-National_museum_of_history_and_culture_of_Belarus-Exterior.jpg',
  },
  {
    id: 'art-belarus-fixture', slug: 'галерея-арт-беларусь', city_slug: 'minsk',
    name: 'Галерея «Арт-Беларусь»', category: 'Музеи и выставки',
    description: 'Выставочное пространство Дворца искусств.', address: 'ул. Козлова, 3, Минск',
    image_url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/d/d6/Yury_Yakovenko_23.10.2014_Palace_of_Art_Minsk.jpg/1280px-Yury_Yakovenko_23.10.2014_Palace_of_Art_Minsk.jpg',
    image_source_url: 'https://commons.wikimedia.org/wiki/File:Yury_Yakovenko_23.10.2014_Palace_of_Art_Minsk.jpg',
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

];

const fixturePhotoCredits = {
  'национальная-библиотека-беларуси-смотровая-площадка': ['Хомелка', 'CC BY-SA 3.0', 'https://creativecommons.org/licenses/by-sa/3.0/'],
  'верхнии-город-и-площадь-свободы': ['Hanna Zelenko', 'CC BY-SA 3.0', 'https://creativecommons.org/licenses/by-sa/3.0/'],
  'чижовка-арена': ['Homoatrox', 'CC BY-SA 3.0', 'https://creativecommons.org/licenses/by-sa/3.0/'],
  'музеи-истории-великои-отечественнои-воины': ['Adam Jones', 'CC BY-SA 2.0', 'https://creativecommons.org/licenses/by-sa/2.0/'],
  'национальныи-художественныи-музеи': ['DBatura', 'CC0 1.0', 'https://creativecommons.org/publicdomain/zero/1.0/'],
  'центральныи-ботаническии-сад': ['Mila Chibireva', 'CC BY-SA 4.0', 'https://creativecommons.org/licenses/by-sa/4.0/'],
  'остров-слез': ['Ludvig14', 'CC BY-SA 4.0', 'https://creativecommons.org/licenses/by-sa/4.0/'],
  'троицкое-предместье': ['Ludvig14', 'CC BY-SA 4.0', 'https://creativecommons.org/licenses/by-sa/4.0/'],
  'минскии-зоопарк': ['SStraySpirit', 'CC BY-SA 4.0', 'https://creativecommons.org/licenses/by-sa/4.0/'],
  'большои-театр-беларуси': ['Ludvig14', 'CC BY-SA 4.0', 'https://creativecommons.org/licenses/by-sa/4.0/'],
  'минскии-планетарии': ['Minsk Planetarium', 'CC BY-SA 2.0', 'https://creativecommons.org/licenses/by-sa/2.0/'],
  'национальныи-историческии-музеи': ['Tatiana Matlina', 'CC BY-SA 3.0', 'https://creativecommons.org/licenses/by-sa/3.0/'],
  'галерея-арт-беларусь': ['Tatiana Matlina', 'CC BY-SA 4.0', 'https://creativecommons.org/licenses/by-sa/4.0/'],
  'лошицкии-парк': ['Dina Panayotis', 'CC BY-SA 4.0', 'https://creativecommons.org/licenses/by-sa/4.0/'],
  'театр-имени-янки-купалы': ['Hanna Zelenko', 'CC BY-SA 3.0', 'https://creativecommons.org/licenses/by-sa/3.0/'],
  'музеи-мастерская-заира-азгура': ['Andrej Hurynovič', 'CC BY-SA 4.0', 'https://creativecommons.org/licenses/by-sa/4.0/'],
  'парк-горького': ['Gruszecki', 'CC0', 'https://creativecommons.org/publicdomain/zero/1.0/'],
  'прогулка-по-парку-победы': ['Nigel’s Europe', 'CC BY-SA 2.0', 'https://creativecommons.org/licenses/by-sa/2.0/'],
};
for (const place of licensedPlaces) {
  const credit = fixturePhotoCredits[place.slug];
  if (credit) {
    [place.image_author, place.image_license, place.image_license_url] = credit;
  }
}

async function mockCatalogApi(page) {
  await page.route('**/api/cities*', route => route.fulfill({ json: [{ slug: 'minsk', name_localized: 'Минск', timezone: 'Europe/Minsk' }] }));
  await page.route('**/api/places*', route => route.fulfill({ json: licensedPlaces }));
  await page.route('**/api/events*', route => route.fulfill({ json: [] }));
  await page.route('**/api/updates*', route => route.fulfill({ json: [] }));
}

const routes = ['/', '/planner', '/map', '/analytics'];

async function openCatalogue(page) {
  await page.addInitScript(() => sessionStorage.setItem('duoEntrySeen', '1'));
  await page.goto('/places');
}

test('Wikimedia photo cards show creator and license attribution, failed photos use labeled fallback', async ({ page }) => {
  const imagePixel = Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/pWQAAAAASUVORK5CYII=', 'base64');
  await page.route('**/api/cities*', route => route.fulfill({ json: [{ slug: 'minsk', name_localized: 'Минск', timezone: 'Europe/Minsk' }] }));
  await page.route('**/api/places*', route => route.fulfill({ json: [
    { id: 'upper-town', slug: 'верхнии-город-и-площадь-свободы', city_slug: 'minsk', name: 'Верхний город', category: 'Видовые места', description: 'Исторический центр Минска.', address: 'Минск', image_url: 'https://images.example.test/upper-town.png', image_source_url: 'https://commons.wikimedia.org/wiki/File:Belarus-Minsk-Upper_Town-1.jpg', image_author: 'Hanna Zelenko', image_license: 'CC BY-SA 3.0', image_license_url: 'https://creativecommons.org/licenses/by-sa/3.0/' },
    { id: 'arena', slug: 'чижовка-арена', city_slug: 'minsk', name: 'Чижовка-Арена', category: 'Спорт', description: 'Спортивная арена.', address: 'Минск', image_url: 'https://images.example.test/arena.png', image_source_url: 'https://commons.wikimedia.org/wiki/File:Chizhovka-Arena_inside_1.jpg', image_author: 'Homoatrox', image_license: 'CC BY-SA 3.0', image_license_url: 'https://creativecommons.org/licenses/by-sa/3.0/' },
    { id: 'broken-photo', slug: 'broken-photo', city_slug: 'minsk', name: 'Место без фото', category: 'Квесты', description: 'Карточка без доступной фотографии.', address: 'Минск', image_url: 'https://images.example.test/broken.jpg' },
  ] }));
  await page.route('https://images.example.test/**', route => route.request().url().endsWith('/broken.jpg')
    ? route.fulfill({ status: 404, contentType: 'image/jpeg', body: '' })
    : route.fulfill({ status: 200, contentType: 'image/png', body: imagePixel }));
  await page.route('**/api/events*', route => route.fulfill({ json: [] }));
  await page.route('**/api/updates*', route => route.fulfill({ json: [] }));
  await openCatalogue(page);

  const upper = page.locator('.place-card').filter({ hasText: 'Верхний город' });
  const arena = page.locator('.place-card').filter({ hasText: 'Чижовка-Арена' });
  await expect(upper.locator('.image-attribution')).toContainText('Hanna Zelenko');
  await expect(upper.locator('.image-attribution')).toContainText('CC BY-SA 3.0');
  await expect(upper.locator('.image-attribution a').first()).toHaveAttribute('href', /commons\.wikimedia\.org/);
  await expect(upper.locator('.image-attribution a').last()).toHaveAttribute('href', 'https://creativecommons.org/licenses/by-sa/3.0/');
  await expect(arena.locator('.image-attribution')).toContainText('Homoatrox');
  await expect(arena.locator('.image-attribution a').last()).toHaveAttribute('href', 'https://creativecommons.org/licenses/by-sa/3.0/');

  const broken = page.locator('.place-card').filter({ hasText: 'Место без фото' });
  await broken.scrollIntoViewIfNeeded();
  await expect(broken.locator('.image-cover')).toHaveAttribute('data-image-kind', 'category-placeholder');
  await expect(broken.locator('.image-cover-placeholder')).toBeVisible();
  await expect(broken.locator('.image-cover-placeholder small')).toHaveText('ФОТО НЕ ДОБАВЛЕНО');
});


for (const route of routes) {
  test(`renders DUO without a blank screen at ${route}`, async ({ page }) => {
    await mockCatalogApi(page);
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
  await mockCatalogApi(page);
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
  await page.setViewportSize({ width: 390, height: 844 });
  await checkNoHorizontalOverflow();
  const mobileLayout = await page.evaluate(() => {
    const input = document.querySelector('input[aria-label="Поиск по местам"]');
    const searchBox = input?.parentElement;
    const content = document.querySelector('.page-content');
    const bounds = element => {
      const rect = element?.getBoundingClientRect();
      return rect ? { left: rect.left, right: rect.right } : null;
    };
    return { searchBox: bounds(searchBox), input: bounds(input), content: bounds(content) };
  });
  expect(mobileLayout.searchBox).not.toBeNull();
  expect(mobileLayout.input).not.toBeNull();
  expect(mobileLayout.content).not.toBeNull();
  expect(mobileLayout.searchBox.right).toBeLessThanOrEqual(mobileLayout.content.right + 1);
  expect(mobileLayout.input.right).toBeLessThanOrEqual(mobileLayout.searchBox.right + 1);
  const imageAltTexts = await page.locator('.place-card .image-cover img').evaluateAll(images => images.map(image => image.alt.trim()));
  expect(imageAltTexts.every(Boolean), 'catalogue images should have descriptive alt text').toBeTruthy();

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
  const search = page.locator('input[aria-label="Поиск по местам"]');

  for (const item of [
    { query: 'Национальная библиотека', author: 'Хомелка', license: 'https://creativecommons.org/licenses/by-sa/3.0/' },
    { query: 'Музей истории Великой Отечественной войны', author: 'Adam Jones', license: 'https://creativecommons.org/licenses/by-sa/2.0/' },
    { query: 'Национальный художественный музей', author: 'DBatura', license: 'https://creativecommons.org/publicdomain/zero/1.0/' },
    { query: 'Центральный ботанический сад', author: 'Mila Chibireva', license: 'https://creativecommons.org/licenses/by-sa/4.0/' },
    { query: 'Остров слёз', author: 'Ludvig14', license: 'https://creativecommons.org/licenses/by-sa/4.0/' },
    { query: 'Троицкое предместье', author: 'Ludvig14', license: 'https://creativecommons.org/licenses/by-sa/4.0/' },
    { query: 'Большой театр Беларуси', author: 'Ludvig14', license: 'https://creativecommons.org/licenses/by-sa/4.0/' },
    { query: 'Верхний город', author: 'Hanna Zelenko', license: 'https://creativecommons.org/licenses/by-sa/3.0/' },
    { query: 'Чижовка-Арена', author: 'Homoatrox', license: 'https://creativecommons.org/licenses/by-sa/3.0/' },
    { query: 'Минский зоопарк', author: 'SStraySpirit', license: 'https://creativecommons.org/licenses/by-sa/4.0/' },
    { query: 'Минский планетарий', author: 'Minsk Planetarium', license: 'https://creativecommons.org/licenses/by-sa/2.0/' },
    { query: 'Национальный исторический музей', author: 'Tatiana Matlina', license: 'https://creativecommons.org/licenses/by-sa/3.0/' },
    { query: 'Галерея «Арт-Беларусь»', author: 'Tatiana Matlina', license: 'https://creativecommons.org/licenses/by-sa/4.0/' },
    { query: 'Лошицкий парк', author: 'Dina Panayotis', license: 'https://creativecommons.org/licenses/by-sa/4.0/' },
    { query: 'Театр имени Янки Купалы', author: 'Hanna Zelenko', license: 'https://creativecommons.org/licenses/by-sa/3.0/' },
    { query: 'Музей-мастерская Заира Азгура', author: 'Andrej Hurynovič', license: 'https://creativecommons.org/licenses/by-sa/4.0/' },
    { query: 'Парк Горького', author: 'Gruszecki', license: 'https://creativecommons.org/publicdomain/zero/1.0/' },
    { query: 'Прогулка по парку Победы', author: 'Nigel’s Europe', license: 'https://creativecommons.org/licenses/by-sa/2.0/' },
  ]) {
    await search.fill(item.query);
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


test('verified venue websites are exposed as direct site links in place details', async ({ page }) => {
  await page.route('**/api/cities*', route => route.fulfill({ json: [{ slug: 'minsk', name_localized: 'Минск', timezone: 'Europe/Minsk' }] }));
  await page.route('**/api/places*', route => route.fulfill({ json: [{
    id: 'neurobox', slug: 'neurobox', city_slug: 'minsk', name: 'Neurobox', category: 'VR и игры',
    description: 'Парк виртуальной реальности.', address: 'пр-т Дзержинского, 104, Минск',
    website_url: 'https://neurobox.by/', source_url: 'https://zabava.by/razvlecheniya',
  }] }));
  await page.route('**/api/events*', route => route.fulfill({ json: [] }));
  await page.route('**/api/updates*', route => route.fulfill({ json: [] }));
  await openCatalogue(page);
  await page.locator('.place-card').filter({ hasText: 'Neurobox' }).click();
  const detail = page.getByRole('dialog', { name: 'Окно DUO' });
  await expect(detail.getByRole('link', { name: 'Сайт / меню' })).toHaveAttribute('href', 'https://neurobox.by/');
  await expect(detail.getByRole('link', { name: 'Источник данных' })).toHaveAttribute('href', 'https://zabava.by/razvlecheniya');
});


test('planner never stores generic search pages as venue websites', async ({ page }) => {
  await mockCatalogApi(page);
  await page.route('**/api/places*', route => route.fulfill({ json: [{ ...licensedPlaces[0], category: 'Кофейни', level: 1, risk: 'low', cost: 15, price_label: '15 BYN' }] }));
  await page.addInitScript(() => sessionStorage.setItem('duoEntrySeen', '1'));
  await page.goto('/planner');
  await page.getByRole('button', { name: /Создать план/ }).click();
  await expect(page.getByRole('heading', { name: 'План-сюрприз' })).toBeVisible();
  await page.getByRole('button', { name: /Сохранить план/ }).click();
  const saved = await page.evaluate(() => JSON.parse(localStorage.getItem('duoGuestPlans') || '[]'));
  expect(saved[0].items.length).toBeGreaterThan(0);
  expect(saved[0].items.every(item => item.url === '')).toBeTruthy();
});


test('Google search and map URLs are not presented as official venue websites', async ({ page }) => {
  await mockCatalogApi(page);
  await openCatalogue(page);
  const search = page.locator('input[aria-label="Поиск по местам"]');
  await search.fill('Национальная библиотека');
  await page.locator('.place-card').filter({ hasText: 'Национальная библиотека' }).first().click();

  const detail = page.getByRole('dialog', { name: 'Окно DUO' });
  await expect(detail).toBeVisible();
  await expect(detail.getByRole('link', { name: 'Сайт / меню' })).toHaveCount(0);
  await expect(detail.getByRole('link', { name: 'Открыть на карте' })).toBeVisible();
  await expect(detail.getByRole('link', { name: 'Поиск источника' })).toBeVisible();
  await expect(detail.getByRole('link', { name: 'Источник данных' })).toHaveCount(0);

  await page.getByRole('button', { name: 'Закрыть окно' }).click();
  await search.fill('Музей истории Великой Отечественной войны');
  await page.locator('.place-card').filter({ hasText: 'Музей истории Великой Отечественной войны' }).first().click();
  const yandexDetail = page.getByRole('dialog', { name: 'Окно DUO' });
  await expect(yandexDetail.getByRole('link', { name: 'Сайт / меню' })).toHaveCount(0);
  await expect(yandexDetail.getByRole('link', { name: 'Открыть на карте' })).toBeVisible();
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
  const imageCover = page.locator('.place-card .image-cover').first();
  await expect(imageCover).toHaveAttribute('data-image-kind', 'category-placeholder');
  await expect(imageCover.locator('.image-cover-placeholder')).toBeVisible();
  await expect(imageCover.locator('.image-cover-placeholder small')).toHaveText('ФОТО НЕ ДОБАВЛЕНО');
});


test('DUO Match explains the sign-in requirement to guests and fits mobile screens', async ({ page }) => {
  await mockCatalogApi(page);
  await page.addInitScript(() => sessionStorage.setItem('duoEntrySeen', '1'));
  await page.goto('/');
  await page.getByRole('button', { name: /DUO Match/ }).click();

  await expect(page.getByRole('heading', { name: /Два мнения/ })).toBeVisible();
  await expect(page.getByText(/Войдите в аккаунт, создайте пространство пары/)).toBeVisible();
  await expect(page.getByRole('button', { name: /Войти в DUO/ })).toBeVisible();

  await page.setViewportSize({ width: 390, height: 844 });
  const dimensions = await page.evaluate(() => ({
    viewport: document.documentElement.clientWidth,
    document: document.documentElement.scrollWidth,
  }));
  expect(dimensions.document, 'DUO Match should not overflow horizontally on mobile')
    .toBeLessThanOrEqual(dimensions.viewport + 1);
});


test('catalogue category filters keep karting out of culture and consolidate duplicates', async ({ page }) => {
  await mockCatalogApi(page);
  await page.route('**/api/places*', route => route.fulfill({ json: [...licensedPlaces, {
    id: 'karting-fixture', slug: 'karting-fixture', city_slug: 'minsk', name: 'Картинг', category: 'Картинг и гонки',
    description: 'Картинг и гоночная трасса.', address: 'Минск', level: 1, risk: 'good', cost: 25,
  }] }));
  await openCatalogue(page);

  const filters = page.locator('.sub-category-scroll button');
  await expect(filters).toHaveCount(6);
  await expect(filters.filter({ hasText: 'Культура' })).toBeVisible();
  await expect(filters.filter({ hasText: 'Видовые места' })).toBeVisible();

  await page.locator('.category-pills button').filter({ hasText: 'Культура' }).click();
  await expect(page.locator('.place-card').filter({ hasText: 'Картинг' })).toHaveCount(0);
  await page.locator('.category-pills button').filter({ hasText: 'Все' }).click();
  await filters.filter({ hasText: 'Культура' }).click();
  await expect(page.locator('.catalog-count')).toContainText('мест найдено');
  const labels = await page.locator('.place-card .image-category').allTextContents();
  expect(labels.length).toBeGreaterThan(0);
  expect(labels.every(label => /музеи|выставки|театр|кино/i.test(label))).toBeTruthy();

  await filters.filter({ hasText: 'Все направления' }).click();
  await expect(page.locator('.place-card')).toHaveCount(19);
});


test('catalogue and favourites have distinct navigation labels and empty states', async ({ page }) => {
  await mockCatalogApi(page);
  await openCatalogue(page);

  await expect(page.locator('.breadcrumb')).toContainText('Каталог мест');
  await expect(page.getByRole('button', { name: /Каталог мест/ })).toBeVisible();
  await expect(page.locator('.catalog-count')).toContainText('18 мест найдено');

  await page.getByRole('button', { name: /Каталог мест/ }).click();
  await expect(page.locator('.breadcrumb')).toContainText('Избранное');
  await expect(page.getByRole('heading', { name: 'Ваше избранное.' })).toBeVisible();
  await expect(page.locator('.catalog-count')).toContainText('0 мест найдено');
  await expect(page.getByRole('heading', { name: 'Самое время найти любимые места.' })).toBeVisible();

  await page.getByRole('button', { name: /Найти, что добавить/ }).click();
  await expect(page.locator('.breadcrumb')).toContainText('Каталог мест');
  await expect(page.locator('.catalog-count')).toContainText('18 мест найдено');
});


test('map renders real locations and its search filters both map results and place selection', async ({ page }) => {
  await mockCatalogApi(page);
  await page.addInitScript(() => sessionStorage.setItem('duoEntrySeen', '1'));
  await page.goto('/map');

  const map = page.locator('.duo-leaflet-map');
  await expect(map).toBeVisible();
  await expect(map.locator('canvas')).toHaveCount(1);
  await expect(page.locator('.map-result')).toHaveCount(2);
  await expect(page.locator('.map-counter')).toContainText('2');

  const search = page.locator('input[placeholder="Найти место или улицу"]');
  await search.fill('Национальная библиотека');
  await expect(page.locator('.map-result')).toHaveCount(1);
  await expect(page.locator('.map-result').first()).toContainText('Национальная библиотека');

  await page.locator('.map-result-main').click();
  await expect(page.getByRole('dialog', { name: 'Окно DUO' })).toBeVisible();
  await page.setViewportSize({ width: 390, height: 844 });
  const dimensions = await page.evaluate(() => ({
    viewport: document.documentElement.clientWidth,
    document: document.documentElement.scrollWidth,
  }));
  expect(dimensions.document, 'map should not overflow horizontally on mobile')
    .toBeLessThanOrEqual(dimensions.viewport + 1);
});
