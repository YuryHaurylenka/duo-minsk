-- Add verified Commons photos for two exact Minsk venue matches.
UPDATE public.places
SET image_url = 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a8/2025.09.18_Loshitsky_Park%2C_Minsk.jpg/1280px-2025.09.18_Loshitsky_Park%2C_Minsk.jpg',
    image_source_url = 'https://commons.wikimedia.org/wiki/File:2025.09.18_Loshitsky_Park,_Minsk.jpg',
    updated_at = now()
WHERE slug = 'лошицкии-парк'
  AND (image_url IS NULL OR btrim(image_url) = '');

UPDATE public.places
SET image_url = 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/86/Belarus-Minsk-Yanka_Kupala_National_Academic_Theatre.jpg/1280px-Belarus-Minsk-Yanka_Kupala_National_Academic_Theatre.jpg',
    image_source_url = 'https://commons.wikimedia.org/wiki/File:Belarus-Minsk-Yanka_Kupala_National_Academic_Theatre.jpg',
    updated_at = now()
WHERE slug = 'театр-имени-янки-купалы'
  AND (image_url IS NULL OR btrim(image_url) = '');
