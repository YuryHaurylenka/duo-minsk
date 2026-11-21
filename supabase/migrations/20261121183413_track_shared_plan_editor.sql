ALTER TABLE public.duo_date_plans
    ADD COLUMN IF NOT EXISTS updated_by uuid REFERENCES auth.users(id) ON DELETE SET NULL;

UPDATE public.duo_date_plans
SET updated_by = created_by
WHERE updated_by IS NULL;
