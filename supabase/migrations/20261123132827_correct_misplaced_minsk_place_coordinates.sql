-- Correct several Minsk locations that were incorrectly assigned the same fallback point.
-- Pbaza has a verified street address but no safely confirmed entrance/field coordinate,
-- so it is intentionally omitted from the map until the exact venue point is confirmed.
UPDATE public.places
SET
  address = CASE slug
    WHEN 'f1-каток-у-дворца-спорта' THEN 'пр-т Победителей, 4А, у Дворца спорта, Минск'
    WHEN 'pbaza-пеинтбол-и-лазертаг' THEN 'ул. Карвата, 83А, микрорайон Степянка, Минск'
    WHEN 'r-park' THEN 'д. Гонолес, Ждановичский сельсовет, Минский район'
    WHEN 'r-парк-лазертаг-и-троллеи' THEN 'д. Гонолес, Ждановичский сельсовет, Минский район'
    WHEN 'квест-пила' THEN 'ул. Тимирязева, 44, Минск'
    WHEN 'квест-проклятие-эмили' THEN 'ул. Тимирязева, 9/12, Минск'
    WHEN 'прогулка-по-парку-победы' THEN 'Парк Победы, пр-т Победителей, Минск'
    WHEN 'художественная-студия-indigo' THEN 'пр-т Независимости, 95, корп. 16, Минск'
    ELSE address
  END,
  latitude = CASE slug
    WHEN 'f1-каток-у-дворца-спорта' THEN 53.9112083
    WHEN 'pbaza-пеинтбол-и-лазертаг' THEN NULL
    WHEN 'r-park' THEN 53.9818624
    WHEN 'r-парк-лазертаг-и-троллеи' THEN 53.9818624
    WHEN 'квест-пила' THEN 53.9159682
    WHEN 'квест-проклятие-эмили' THEN 53.907663
    WHEN 'прогулка-по-парку-победы' THEN 53.9225949
    WHEN 'художественная-студия-indigo' THEN 53.927416
    ELSE latitude
  END,
  longitude = CASE slug
    WHEN 'f1-каток-у-дворца-спорта' THEN 27.5507891
    WHEN 'pbaza-пеинтбол-и-лазертаг' THEN NULL
    WHEN 'r-park' THEN 27.3178178
    WHEN 'r-парк-лазертаг-и-троллеи' THEN 27.3178178
    WHEN 'квест-пила' THEN 27.5218188
    WHEN 'квест-проклятие-эмили' THEN 27.531127
    WHEN 'прогулка-по-парку-победы' THEN 27.5369616
    WHEN 'художественная-студия-indigo' THEN 27.615460
    ELSE longitude
  END,
  source_url = CASE slug
    WHEN 'f1-каток-у-дворца-спорта' THEN 'https://bestbelarus.by/events/news/katok-na-nemige-u-dvortsa-sporta-otkrylsya-tseny-i-vremya-raboty/'
    WHEN 'pbaza-пеинтбол-и-лазертаг' THEN 'https://spravka.by/zony-otdyxa/pejntbolnyj-klub-pbaza'
    WHEN 'r-park' THEN 'https://www.openstreetmap.org/?mlat=53.9818624&mlon=27.3178178#map=17/53.9818624/27.3178178'
    WHEN 'r-парк-лазертаг-и-троллеи' THEN 'https://www.openstreetmap.org/?mlat=53.9818624&mlon=27.3178178#map=17/53.9818624/27.3178178'
    WHEN 'квест-пила' THEN 'https://pandorabox.by/pila-driving-directions'
    WHEN 'квест-проклятие-эмили' THEN 'https://pandorabox.by/emily-driving-directions'
    WHEN 'прогулка-по-парку-победы' THEN 'https://www.openstreetmap.org/?mlat=53.9225949&mlon=27.5369616#map=17/53.9225949/27.5369616'
    WHEN 'художественная-студия-indigo' THEN 'https://yandex.by/maps/org/indigo/62689131071/'
    ELSE source_url
  END,
  location_verified_at = CASE WHEN slug = 'pbaza-пеинтбол-и-лазертаг' THEN NULL ELSE now() END,
  updated_at = now()
WHERE slug IN (
  'f1-каток-у-дворца-спорта', 'pbaza-пеинтбол-и-лазертаг', 'r-park',
  'r-парк-лазертаг-и-троллеи', 'квест-пила', 'квест-проклятие-эмили',
  'прогулка-по-парку-победы', 'художественная-студия-indigo'
);
