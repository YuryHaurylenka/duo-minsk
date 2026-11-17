ALTER TABLE public.cities
  ADD COLUMN name_localized text,
  ADD COLUMN country_name_localized text;

UPDATE public.cities
SET name_localized = 'Минск',
    country_name_localized = 'Беларусь'
WHERE slug = 'minsk';

ALTER TABLE public.cities
  ALTER COLUMN name_localized SET NOT NULL,
  ALTER COLUMN country_name_localized SET NOT NULL;
