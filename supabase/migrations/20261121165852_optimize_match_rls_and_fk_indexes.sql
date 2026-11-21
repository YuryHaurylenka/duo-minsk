-- Improve FK lookup performance and avoid per-row auth.uid() evaluation in DUO Match RLS.
-- Authorization semantics are intentionally unchanged.

CREATE INDEX IF NOT EXISTS duo_event_sync_runs_city_slug_idx
  ON public.duo_event_sync_runs (city_slug);

CREATE INDEX IF NOT EXISTS duo_match_candidates_place_slug_idx
  ON public.duo_match_candidates (place_slug);

CREATE INDEX IF NOT EXISTS duo_match_sessions_city_slug_idx
  ON public.duo_match_sessions (city_slug);

CREATE INDEX IF NOT EXISTS personal_place_activity_place_slug_idx
  ON public.personal_place_activity (place_slug);

CREATE INDEX IF NOT EXISTS place_activity_place_slug_idx
  ON public.place_activity (place_slug);

DROP POLICY IF EXISTS duo_match_sessions_member_access ON public.duo_match_sessions;
CREATE POLICY duo_match_sessions_member_access
  ON public.duo_match_sessions
  FOR ALL TO authenticated
  USING (
    EXISTS (
      SELECT 1
      FROM public.couple_members cm
      WHERE cm.couple_id = duo_match_sessions.couple_id
        AND cm.user_id = (SELECT auth.uid())
    )
  )
  WITH CHECK (
    EXISTS (
      SELECT 1
      FROM public.couple_members cm
      WHERE cm.couple_id = duo_match_sessions.couple_id
        AND cm.user_id = (SELECT auth.uid())
    )
  );

DROP POLICY IF EXISTS duo_match_candidates_member_access ON public.duo_match_candidates;
CREATE POLICY duo_match_candidates_member_access
  ON public.duo_match_candidates
  FOR ALL TO authenticated
  USING (
    EXISTS (
      SELECT 1
      FROM public.duo_match_sessions s
      JOIN public.couple_members cm ON cm.couple_id = s.couple_id
      WHERE s.id = duo_match_candidates.session_id
        AND cm.user_id = (SELECT auth.uid())
    )
  )
  WITH CHECK (
    EXISTS (
      SELECT 1
      FROM public.duo_match_sessions s
      JOIN public.couple_members cm ON cm.couple_id = s.couple_id
      WHERE s.id = duo_match_candidates.session_id
        AND cm.user_id = (SELECT auth.uid())
    )
  );

DROP POLICY IF EXISTS duo_match_votes_member_read ON public.duo_match_votes;
CREATE POLICY duo_match_votes_member_read
  ON public.duo_match_votes
  FOR SELECT TO authenticated
  USING (
    EXISTS (
      SELECT 1
      FROM public.duo_match_sessions s
      JOIN public.couple_members cm ON cm.couple_id = s.couple_id
      WHERE s.id = duo_match_votes.session_id
        AND cm.user_id = (SELECT auth.uid())
    )
  );

DROP POLICY IF EXISTS duo_match_votes_member_insert ON public.duo_match_votes;
CREATE POLICY duo_match_votes_member_insert
  ON public.duo_match_votes
  FOR INSERT TO authenticated
  WITH CHECK (
    user_id = (SELECT auth.uid())
    AND EXISTS (
      SELECT 1
      FROM public.duo_match_sessions s
      JOIN public.couple_members cm ON cm.couple_id = s.couple_id
      WHERE s.id = duo_match_votes.session_id
        AND cm.user_id = (SELECT auth.uid())
    )
  );

DROP POLICY IF EXISTS duo_match_votes_member_update ON public.duo_match_votes;
CREATE POLICY duo_match_votes_member_update
  ON public.duo_match_votes
  FOR UPDATE TO authenticated
  USING (
    user_id = (SELECT auth.uid())
    AND EXISTS (
      SELECT 1
      FROM public.duo_match_sessions s
      JOIN public.couple_members cm ON cm.couple_id = s.couple_id
      WHERE s.id = duo_match_votes.session_id
        AND cm.user_id = (SELECT auth.uid())
    )
  )
  WITH CHECK (
    user_id = (SELECT auth.uid())
    AND EXISTS (
      SELECT 1
      FROM public.duo_match_sessions s
      JOIN public.couple_members cm ON cm.couple_id = s.couple_id
      WHERE s.id = duo_match_votes.session_id
        AND cm.user_id = (SELECT auth.uid())
    )
  );

DROP POLICY IF EXISTS duo_match_votes_member_delete ON public.duo_match_votes;
CREATE POLICY duo_match_votes_member_delete
  ON public.duo_match_votes
  FOR DELETE TO authenticated
  USING (
    user_id = (SELECT auth.uid())
    AND EXISTS (
      SELECT 1
      FROM public.duo_match_sessions s
      JOIN public.couple_members cm ON cm.couple_id = s.couple_id
      WHERE s.id = duo_match_votes.session_id
        AND cm.user_id = (SELECT auth.uid())
    )
  );
