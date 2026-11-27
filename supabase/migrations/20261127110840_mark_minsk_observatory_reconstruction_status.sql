-- Keep the Minsk Observatory listing honest while it is closed for reconstruction.
UPDATE public.places
SET description = 'Площадка Минского планетария для наблюдений за небом; по официальному сайту сейчас закрыта на реконструкцию.',
    tip = 'По официальному сайту обсерватория закрыта на реконструкцию. Перед планированием визита проверьте объявления о возобновлении наблюдений.',
    updated_at = now()
WHERE city_slug = 'minsk'
  AND slug = 'минская-обсерватория'
  AND website_url = 'https://observatory.planetarium.by/';
