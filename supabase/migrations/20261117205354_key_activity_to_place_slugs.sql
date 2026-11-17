ALTER TABLE public.place_activity
  ADD COLUMN place_slug text;

UPDATE public.place_activity AS activity
SET place_slug = places.slug
FROM public.places AS places
WHERE places.name = activity.place_name;

ALTER TABLE public.place_activity
  ALTER COLUMN place_slug SET NOT NULL;

ALTER TABLE public.place_activity
  ADD CONSTRAINT place_activity_place_slug_fkey
  FOREIGN KEY (place_slug) REFERENCES public.places(slug) ON DELETE CASCADE;

ALTER TABLE public.place_activity
  DROP CONSTRAINT place_activity_couple_id_place_name_key;

ALTER TABLE public.place_activity
  ADD CONSTRAINT place_activity_couple_id_place_slug_key
  UNIQUE (couple_id, place_slug);
