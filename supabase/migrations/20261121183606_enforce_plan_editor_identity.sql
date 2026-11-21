DROP POLICY IF EXISTS "Couple members can create date plans" ON public.duo_date_plans;
CREATE POLICY "Couple members can create date plans"
    ON public.duo_date_plans
    FOR INSERT TO authenticated
    WITH CHECK (
        private.is_couple_member(couple_id)
        AND created_by = (SELECT auth.uid())
        AND updated_by = (SELECT auth.uid())
    );

DROP POLICY IF EXISTS "Couple members can update date plans" ON public.duo_date_plans;
CREATE POLICY "Couple members can update date plans"
    ON public.duo_date_plans
    FOR UPDATE TO authenticated
    USING (private.is_couple_member(couple_id))
    WITH CHECK (
        private.is_couple_member(couple_id)
        AND updated_by = (SELECT auth.uid())
    );
