-- Run once in Supabase SQL Editor as the project database owner.
-- Replace the password with a unique random value and store it only in Vercel's
-- encrypted DATABASE_URL environment variable.
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'duo_api') THEN
    CREATE ROLE duo_api LOGIN NOINHERIT NOBYPASSRLS PASSWORD 'REPLACE_WITH_A_LONG_RANDOM_PASSWORD';
  ELSE
    ALTER ROLE duo_api WITH LOGIN NOINHERIT NOBYPASSRLS PASSWORD 'REPLACE_WITH_A_LONG_RANDOM_PASSWORD';
  END IF;
END
$$;

-- The backend explicitly switches to anon for public requests and authenticated
-- for verified user requests. This preserves the existing PostgreSQL RLS rules.
GRANT anon, authenticated TO duo_api;
GRANT duo_match_backend TO duo_api;
GRANT CONNECT ON DATABASE postgres TO duo_api;
