UPDATE public.places
SET image_url = NULL,
    image_source_url = NULL,
    updated_at = now()
WHERE slug IN ('burgerlab', 'ember', 'the-view')
  AND is_active;
