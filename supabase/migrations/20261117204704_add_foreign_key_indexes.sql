-- Cover foreign keys used by ownership and audit lookups.
CREATE INDEX IF NOT EXISTS idx_couples_created_by
  ON public.couples (created_by);

CREATE INDEX IF NOT EXISTS idx_duo_date_plans_created_by
  ON public.duo_date_plans (created_by);

CREATE INDEX IF NOT EXISTS idx_place_activity_updated_by
  ON public.place_activity (updated_by);
