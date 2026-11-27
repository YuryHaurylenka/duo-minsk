-- Add the verified official website for Gorky Park in Minsk.
-- The venue page is listed by the park directory and independent local listings.
UPDATE public.places
SET website_url = 'https://parki.by/All-parks/1/history',
    source_name = 'Официальный сайт парка',
    source_url = 'https://parki.by/All-parks/1/history',
    updated_at = now()
WHERE city_slug = 'minsk'
  AND slug = 'парк-горького'
  AND COALESCE(website_url, '') = ''
  AND source_url = 'https://www.google.com/search?q=Парк+Горького+Минск+отзывы';
