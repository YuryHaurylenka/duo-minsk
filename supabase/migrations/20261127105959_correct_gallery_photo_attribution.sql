-- Correct the photographer credit to match the Wikimedia Commons file page.
UPDATE public.places
SET image_author = 'Tatiana Matlina',
    updated_at = now()
WHERE slug = 'галерея-арт-беларусь'
  AND image_author = 'Tatiana Markina'
  AND image_license = 'CC BY-SA 4.0'
  AND image_source_url = 'https://commons.wikimedia.org/wiki/File:Yury_Yakovenko_23.10.2014_Palace_of_Art_Minsk.jpg';
