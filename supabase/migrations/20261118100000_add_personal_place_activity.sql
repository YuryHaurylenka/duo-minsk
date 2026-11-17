CREATE TABLE public.personal_place_activity (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  place_slug varchar(180) NOT NULL REFERENCES public.places(slug) ON DELETE CASCADE,
  place_name text NOT NULL,
  is_favorite boolean NOT NULL DEFAULT false,
  visited_at timestamptz,
  rating smallint CHECK (rating BETWEEN 1 AND 5),
  note text NOT NULL DEFAULT '',
  updated_at timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT personal_place_activity_user_place_key UNIQUE (user_id, place_slug)
);
CREATE INDEX personal_place_activity_user_updated_idx
  ON public.personal_place_activity (user_id, updated_at DESC);
ALTER TABLE public.personal_place_activity ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users manage their own personal place activity"
  ON public.personal_place_activity FOR ALL TO authenticated
  USING ((select auth.uid()) = user_id)
  WITH CHECK ((select auth.uid()) = user_id);
GRANT SELECT, INSERT, UPDATE, DELETE ON public.personal_place_activity TO authenticated;
