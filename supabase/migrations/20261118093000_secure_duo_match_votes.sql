DROP POLICY IF EXISTS duo_match_votes_member_update ON public.duo_match_votes;
CREATE POLICY duo_match_votes_member_update ON public.duo_match_votes FOR UPDATE TO authenticated
USING (user_id=auth.uid() AND EXISTS (SELECT 1 FROM public.duo_match_sessions s JOIN public.couple_members cm ON cm.couple_id=s.couple_id WHERE s.id=duo_match_votes.session_id AND cm.user_id=auth.uid()))
WITH CHECK (user_id=auth.uid() AND EXISTS (SELECT 1 FROM public.duo_match_sessions s JOIN public.couple_members cm ON cm.couple_id=s.couple_id WHERE s.id=duo_match_votes.session_id AND cm.user_id=auth.uid()));
