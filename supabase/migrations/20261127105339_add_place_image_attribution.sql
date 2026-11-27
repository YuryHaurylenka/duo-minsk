-- Store image attribution alongside each place instead of keeping it in frontend-only constants.
ALTER TABLE public.places
  ADD COLUMN IF NOT EXISTS image_author text,
  ADD COLUMN IF NOT EXISTS image_license text,
  ADD COLUMN IF NOT EXISTS image_license_url text;

UPDATE public.places AS place
SET image_author = credit.author,
    image_license = credit.license,
    image_license_url = credit.license_url,
    updated_at = now()
FROM (VALUES
  ('национальная-библиотека-беларуси-смотровая-площадка', 'Хомелка', 'CC BY-SA 3.0', 'https://creativecommons.org/licenses/by-sa/3.0/'),
  ('верхнии-город-и-площадь-свободы', 'Hanna Zelenko', 'CC BY-SA 3.0', 'https://creativecommons.org/licenses/by-sa/3.0/'),
  ('чижовка-арена', 'Homoatrox', 'CC BY-SA 3.0', 'https://creativecommons.org/licenses/by-sa/3.0/'),
  ('музеи-истории-великои-отечественнои-воины', 'Adam Jones', 'CC BY-SA 2.0', 'https://creativecommons.org/licenses/by-sa/2.0/'),
  ('национальныи-художественныи-музеи', 'DBatura', 'CC0 1.0', 'https://creativecommons.org/publicdomain/zero/1.0/'),
  ('центральныи-ботаническии-сад', 'Mila Chibireva', 'CC BY-SA 4.0', 'https://creativecommons.org/licenses/by-sa/4.0/'),
  ('остров-слез', 'Ludvig14', 'CC BY-SA 4.0', 'https://creativecommons.org/licenses/by-sa/4.0/'),
  ('троицкое-предместье', 'Ludvig14', 'CC BY-SA 4.0', 'https://creativecommons.org/licenses/by-sa/4.0/'),
  ('минскии-зоопарк', 'SStraySpirit', 'CC BY-SA 4.0', 'https://creativecommons.org/licenses/by-sa/4.0/'),
  ('большои-театр-беларуси', 'Ludvig14', 'CC BY-SA 4.0', 'https://creativecommons.org/licenses/by-sa/4.0/'),
  ('минскии-планетарии', 'Minsk Planetarium', 'CC BY-SA 2.0', 'https://creativecommons.org/licenses/by-sa/2.0/'),
  ('национальныи-историческии-музеи', 'Tatiana Matlina', 'CC BY-SA 3.0', 'https://creativecommons.org/licenses/by-sa/3.0/'),
  ('галерея-арт-беларусь', 'Tatiana Markina', 'CC BY-SA 4.0', 'https://creativecommons.org/licenses/by-sa/4.0/'),
  ('лошицкии-парк', 'Dina Panayotis', 'CC BY-SA 4.0', 'https://creativecommons.org/licenses/by-sa/4.0/'),
  ('театр-имени-янки-купалы', 'Hanna Zelenko', 'CC BY-SA 3.0', 'https://creativecommons.org/licenses/by-sa/3.0/'),
  ('музеи-мастерская-заира-азгура', 'Andrej Hurynovič', 'CC BY-SA 4.0', 'https://creativecommons.org/licenses/by-sa/4.0/'),
  ('парк-горького', 'Gruszecki', 'CC0', 'https://creativecommons.org/publicdomain/zero/1.0/'),
  ('прогулка-по-парку-победы', 'Nigel’s Europe', 'CC BY-SA 2.0', 'https://creativecommons.org/licenses/by-sa/2.0/')
) AS credit(slug, author, license, license_url)
WHERE place.slug = credit.slug
  AND place.image_url IS NOT NULL
  AND btrim(place.image_url) <> '';

ALTER TABLE public.places
  ADD CONSTRAINT places_image_attribution_complete
  CHECK (
    (image_author IS NULL AND image_license IS NULL AND image_license_url IS NULL)
    OR (
      NULLIF(btrim(image_author), '') IS NOT NULL
      AND NULLIF(btrim(image_license), '') IS NOT NULL
      AND NULLIF(btrim(image_license_url), '') IS NOT NULL
    )
  );
