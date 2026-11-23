-- Add exact-match Wikimedia Commons photographs with their source pages.
-- Only fill empty image fields so manually curated photos are never overwritten.
UPDATE public.places
SET image_url = 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/79/Belarus-Minsk-National_museum_of_history_and_culture_of_Belarus-Exterior.jpg/1280px-Belarus-Minsk-National_museum_of_history_and_culture_of_Belarus-Exterior.jpg',
    image_source_url = 'https://commons.wikimedia.org/wiki/File:Belarus-Minsk-National_museum_of_history_and_culture_of_Belarus-Exterior.jpg',
    updated_at = now()
WHERE slug = 'национальныи-историческии-музеи'
  AND (image_url IS NULL OR btrim(image_url) = '');

UPDATE public.places
SET image_url = 'https://upload.wikimedia.org/wikipedia/commons/thumb/d/d6/Yury_Yakovenko_23.10.2014_Palace_of_Art_Minsk.jpg/1280px-Yury_Yakovenko_23.10.2014_Palace_of_Art_Minsk.jpg',
    image_source_url = 'https://commons.wikimedia.org/wiki/File:Yury_Yakovenko_23.10.2014_Palace_of_Art_Minsk.jpg',
    updated_at = now()
WHERE slug = 'галерея-арт-беларусь'
  AND (image_url IS NULL OR btrim(image_url) = '');
