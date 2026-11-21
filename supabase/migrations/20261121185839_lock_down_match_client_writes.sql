-- Keep browser clients read-only while the FastAPI Match endpoints retain
-- couple-scoped access through a dedicated non-login database role.
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'duo_match_backend') THEN
    CREATE ROLE duo_match_backend NOLOGIN INHERIT;
  END IF;
END
$$;
GRANT authenticated TO duo_match_backend;
GRANT USAGE ON SCHEMA public TO duo_match_backend;
GRANT SELECT, INSERT, UPDATE, DELETE
  ON public.duo_match_sessions, public.duo_match_candidates, public.duo_match_votes
  TO duo_match_backend;
REVOKE INSERT, UPDATE, DELETE ON public.duo_match_sessions FROM authenticated;
REVOKE ALL ON public.duo_match_candidates FROM authenticated;
REVOKE ALL ON public.duo_match_votes FROM authenticated;

DROP POLICY IF EXISTS duo_match_sessions_member_access ON public.duo_match_sessions;
CREATE POLICY duo_match_sessions_member_read
  ON public.duo_match_sessions FOR SELECT TO authenticated
  USING (EXISTS (SELECT 1 FROM public.couple_members cm
    WHERE cm.couple_id = duo_match_sessions.couple_id AND cm.user_id = (SELECT auth.uid())));
CREATE POLICY duo_match_sessions_backend_access
  ON public.duo_match_sessions FOR ALL TO duo_match_backend
  USING (EXISTS (SELECT 1 FROM public.couple_members cm
    WHERE cm.couple_id = duo_match_sessions.couple_id AND cm.user_id = (SELECT auth.uid())))
  WITH CHECK (EXISTS (SELECT 1 FROM public.couple_members cm
    WHERE cm.couple_id = duo_match_sessions.couple_id AND cm.user_id = (SELECT auth.uid())));

DROP POLICY IF EXISTS duo_match_candidates_member_access ON public.duo_match_candidates;
CREATE POLICY duo_match_candidates_backend_access
  ON public.duo_match_candidates FOR ALL TO duo_match_backend
  USING (EXISTS (SELECT 1 FROM public.duo_match_sessions s
    JOIN public.couple_members cm ON cm.couple_id = s.couple_id
    WHERE s.id = duo_match_candidates.session_id AND cm.user_id = (SELECT auth.uid())))
  WITH CHECK (EXISTS (SELECT 1 FROM public.duo_match_sessions s
    JOIN public.couple_members cm ON cm.couple_id = s.couple_id
    WHERE s.id = duo_match_candidates.session_id AND cm.user_id = (SELECT auth.uid())));

DROP POLICY IF EXISTS duo_match_votes_member_read ON public.duo_match_votes;
DROP POLICY IF EXISTS duo_match_votes_member_insert ON public.duo_match_votes;
DROP POLICY IF EXISTS duo_match_votes_member_update ON public.duo_match_votes;
DROP POLICY IF EXISTS duo_match_votes_member_delete ON public.duo_match_votes;
CREATE POLICY duo_match_votes_backend_read
  ON public.duo_match_votes FOR SELECT TO duo_match_backend
  USING (EXISTS (SELECT 1 FROM public.duo_match_sessions s
    JOIN public.couple_members cm ON cm.couple_id = s.couple_id
    WHERE s.id = duo_match_votes.session_id AND cm.user_id = (SELECT auth.uid())));
CREATE POLICY duo_match_votes_backend_insert
  ON public.duo_match_votes FOR INSERT TO duo_match_backend
  WITH CHECK (user_id = (SELECT auth.uid()) AND EXISTS (
    SELECT 1 FROM public.duo_match_sessions s JOIN public.couple_members cm ON cm.couple_id = s.couple_id
    WHERE s.id = duo_match_votes.session_id AND cm.user_id = (SELECT auth.uid())));
CREATE POLICY duo_match_votes_backend_update
  ON public.duo_match_votes FOR UPDATE TO duo_match_backend
  USING (user_id = (SELECT auth.uid()) AND EXISTS (
    SELECT 1 FROM public.duo_match_sessions s JOIN public.couple_members cm ON cm.couple_id = s.couple_id
    WHERE s.id = duo_match_votes.session_id AND cm.user_id = (SELECT auth.uid())))
  WITH CHECK (user_id = (SELECT auth.uid()) AND EXISTS (
    SELECT 1 FROM public.duo_match_sessions s JOIN public.couple_members cm ON cm.couple_id = s.couple_id
    WHERE s.id = duo_match_votes.session_id AND cm.user_id = (SELECT auth.uid())));
CREATE POLICY duo_match_votes_backend_delete
  ON public.duo_match_votes FOR DELETE TO duo_match_backend
  USING (user_id = (SELECT auth.uid()) AND EXISTS (
    SELECT 1 FROM public.duo_match_sessions s JOIN public.couple_members cm ON cm.couple_id = s.couple_id
    WHERE s.id = duo_match_votes.session_id AND cm.user_id = (SELECT auth.uid())));
