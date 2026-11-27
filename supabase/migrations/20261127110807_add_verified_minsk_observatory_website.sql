-- Add the official observatory website linked by Minsk Planetarium.
UPDATE public.places
SET website_url = 'https://observatory.planetarium.by/',
    source_name = 'Официальный сайт Минского планетария',
    source_url = 'https://observatory.planetarium.by/',
    updated_at = now()
WHERE city_slug = 'minsk'
  AND slug = 'минская-обсерватория'
  AND COALESCE(website_url, '') = ''
  AND source_url LIKE 'https://www.google.com/maps/search/%';
