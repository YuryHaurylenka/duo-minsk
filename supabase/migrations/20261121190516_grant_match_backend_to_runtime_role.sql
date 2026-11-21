-- The restricted FastAPI login uses NOINHERIT and must explicitly be
-- granted membership so it can SET LOCAL ROLE for authenticated Match routes.
DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'duo_api') THEN
    EXECUTE 'GRANT duo_match_backend TO duo_api';
  END IF;
END
$$;
