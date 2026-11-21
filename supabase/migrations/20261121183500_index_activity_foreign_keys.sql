CREATE INDEX IF NOT EXISTS duo_date_plans_updated_by_idx
    ON public.duo_date_plans(updated_by);

CREATE INDEX IF NOT EXISTS recommendation_feedback_place_slug_idx
    ON public.recommendation_feedback(place_slug);
