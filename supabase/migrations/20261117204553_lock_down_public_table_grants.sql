-- Lock down existing grants and future default privileges for objects created by postgres.
-- Public catalog endpoints remain read-only for anon/authenticated.
-- Couple data is available only to authenticated members through RLS.

REVOKE ALL PRIVILEGES ON ALL TABLES IN SCHEMA public FROM anon;
REVOKE INSERT, UPDATE, DELETE, TRUNCATE, REFERENCES, TRIGGER
  ON ALL TABLES IN SCHEMA public FROM authenticated;

GRANT SELECT ON TABLE public.places, public.duo_events, public.duo_place_updates
  TO anon, authenticated;

REVOKE ALL PRIVILEGES ON TABLE
  public.couples,
  public.couple_members,
  public.duo_date_plans,
  public.place_activity
  FROM anon;

GRANT SELECT ON TABLE public.couples, public.couple_members TO authenticated;
GRANT DELETE ON TABLE public.couple_members TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE
  ON TABLE public.duo_date_plans, public.place_activity
  TO authenticated;

REVOKE ALL PRIVILEGES ON TABLE
  public.duo_event_sources,
  public.duo_event_sync_config,
  public.duo_event_sync_runs
  FROM anon, authenticated;

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public
  REVOKE ALL ON TABLES FROM anon, authenticated;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public
  REVOKE EXECUTE ON FUNCTIONS FROM PUBLIC, anon, authenticated;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public
  REVOKE ALL ON SEQUENCES FROM anon, authenticated;
