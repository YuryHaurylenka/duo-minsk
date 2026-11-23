-- Add exact-match Commons photographs for three Minsk places.
UPDATE public.places
SET image_url = 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/Memorial_Museum-Workshop_of_Zair_Isakavi%C4%8D_Azhur_03.jpg/1280px-Memorial_Museum-Workshop_of_Zair_Isakavi%C4%8D_Azhur_03.jpg',
    image_source_url = 'https://commons.wikimedia.org/wiki/File:Memorial_Museum-Workshop_of_Zair_Isakavi%C4%8D_Azhur_03.jpg',
    updated_at = now()
WHERE slug = 'музеи-мастерская-заира-азгура'
  AND (image_url IS NULL OR btrim(image_url) = '');

UPDATE public.places
SET image_url = 'https://upload.wikimedia.org/wikipedia/commons/5/57/Gorki_park%2C_Minsk1.JPG',
    image_source_url = 'https://commons.wikimedia.org/wiki/File:Gorki_park,_Minsk1.JPG',
    updated_at = now()
WHERE slug = 'парк-горького'
  AND (image_url IS NULL OR btrim(image_url) = '');

UPDATE public.places
SET image_url = 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/cd/View_of_Victory_Park_Minsk.jpg/1280px-View_of_Victory_Park_Minsk.jpg',
    image_source_url = 'https://commons.wikimedia.org/wiki/File:View_of_Victory_Park_Minsk.jpg',
    updated_at = now()
WHERE slug = 'прогулка-по-парку-победы'
  AND (image_url IS NULL OR btrim(image_url) = '');
