-- Keep the RLS membership helper outside Supabase's exposed API schemas.
CREATE SCHEMA IF NOT EXISTS private;
REVOKE ALL ON SCHEMA private FROM PUBLIC, anon;
GRANT USAGE ON SCHEMA private TO authenticated, service_role;

ALTER FUNCTION public.is_couple_member(uuid) SET SCHEMA private;
REVOKE ALL ON FUNCTION private.is_couple_member(uuid) FROM PUBLIC, anon, authenticated;
GRANT EXECUTE ON FUNCTION private.is_couple_member(uuid) TO authenticated, service_role;
