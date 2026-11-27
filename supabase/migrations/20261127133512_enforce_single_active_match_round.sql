-- Prevent two concurrent requests from creating duplicate active rounds for one couple/city.
-- The API handles this conflict by returning the winner's active session.
CREATE UNIQUE INDEX IF NOT EXISTS duo_match_sessions_one_active_per_couple_city_idx
  ON public.duo_match_sessions (couple_id, city_slug)
  WHERE status = 'active';
