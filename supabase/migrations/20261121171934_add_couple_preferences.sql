ALTER TABLE public.couples ADD COLUMN IF NOT EXISTS preferences jsonb NOT NULL DEFAULT '{"members": {}}'::jsonb;
COMMENT ON COLUMN public.couples.preferences IS 'Per-member discovery preferences keyed by authenticated Supabase user UUID. Personal comfort/accessibility settings are not stored here.';
