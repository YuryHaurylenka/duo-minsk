ALTER FUNCTION public.create_couple(text) SET SCHEMA private;
ALTER FUNCTION public.join_couple(text) SET SCHEMA private;

REVOKE ALL ON FUNCTION private.create_couple(text) FROM PUBLIC, anon;
REVOKE ALL ON FUNCTION private.join_couple(text) FROM PUBLIC, anon;
GRANT USAGE ON SCHEMA private TO authenticated, service_role;
GRANT EXECUTE ON FUNCTION private.create_couple(text) TO authenticated, service_role;
GRANT EXECUTE ON FUNCTION private.join_couple(text) TO authenticated, service_role;
