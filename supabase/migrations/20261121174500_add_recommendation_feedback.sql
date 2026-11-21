CREATE TABLE IF NOT EXISTS public.recommendation_feedback (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    place_slug varchar(180) NOT NULL REFERENCES public.places(slug) ON DELETE CASCADE,
    action varchar(20) NOT NULL DEFAULT 'dismiss' CHECK (action = 'dismiss'),
    created_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT recommendation_feedback_user_place_key UNIQUE (user_id, place_slug)
);

CREATE INDEX IF NOT EXISTS recommendation_feedback_user_id_idx
    ON public.recommendation_feedback(user_id);

ALTER TABLE public.recommendation_feedback ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS recommendation_feedback_select_own ON public.recommendation_feedback;
CREATE POLICY recommendation_feedback_select_own
    ON public.recommendation_feedback FOR SELECT TO authenticated
    USING ((SELECT auth.uid()) = user_id);

DROP POLICY IF EXISTS recommendation_feedback_insert_own ON public.recommendation_feedback;
CREATE POLICY recommendation_feedback_insert_own
    ON public.recommendation_feedback FOR INSERT TO authenticated
    WITH CHECK ((SELECT auth.uid()) = user_id);

DROP POLICY IF EXISTS recommendation_feedback_delete_own ON public.recommendation_feedback;
CREATE POLICY recommendation_feedback_delete_own
    ON public.recommendation_feedback FOR DELETE TO authenticated
    USING ((SELECT auth.uid()) = user_id);

GRANT SELECT, INSERT, DELETE ON public.recommendation_feedback TO authenticated;
GRANT ALL ON public.recommendation_feedback TO service_role;
