-- Run against a Supabase PostgreSQL database with a privileged test connection.
-- All fixtures are transaction-scoped and rolled back at the end.
BEGIN;

DO $$
BEGIN
  IF has_table_privilege('anon', 'public.couples', 'SELECT') THEN
    RAISE EXCEPTION 'anon must not read couples';
  END IF;
  IF has_table_privilege('anon', 'public.place_activity', 'SELECT') THEN
    RAISE EXCEPTION 'anon must not read private activity';
  END IF;
  IF has_table_privilege('authenticated', 'public.couples', 'TRUNCATE') THEN
    RAISE EXCEPTION 'authenticated must not truncate couples';
  END IF;
  IF has_table_privilege('authenticated', 'public.duo_event_sync_config', 'SELECT') THEN
    RAISE EXCEPTION 'authenticated must not read internal event sync config';
  END IF;
  IF has_function_privilege('anon', 'public.create_couple(text)', 'EXECUTE') THEN
    RAISE EXCEPTION 'anon must not execute create_couple';
  END IF;
  IF NOT has_function_privilege('authenticated', 'public.create_couple(text)', 'EXECUTE') THEN
    RAISE EXCEPTION 'authenticated must be able to execute create_couple';
  END IF;
END $$;

SELECT set_config('duo.test.user_a', gen_random_uuid()::text, true);
SELECT set_config('duo.test.user_b', gen_random_uuid()::text, true);
SELECT set_config('duo.test.couple_a', gen_random_uuid()::text, true);
SELECT set_config('duo.test.couple_b', gen_random_uuid()::text, true);

INSERT INTO auth.users (id, aud, role, email, encrypted_password, email_confirmed_at,
                        raw_app_meta_data, raw_user_meta_data, created_at, updated_at)
VALUES
  (current_setting('duo.test.user_a')::uuid, 'authenticated', 'authenticated',
   current_setting('duo.test.user_a') || '@duo-rls.invalid', '', now(), '{}'::jsonb, '{}'::jsonb, now(), now()),
  (current_setting('duo.test.user_b')::uuid, 'authenticated', 'authenticated',
   current_setting('duo.test.user_b') || '@duo-rls.invalid', '', now(), '{}'::jsonb, '{}'::jsonb, now(), now());

INSERT INTO public.couples (id, name, created_by)
VALUES
  (current_setting('duo.test.couple_a')::uuid, 'RLS fixture A', current_setting('duo.test.user_a')::uuid),
  (current_setting('duo.test.couple_b')::uuid, 'RLS fixture B', current_setting('duo.test.user_b')::uuid);

INSERT INTO public.couple_members (couple_id, user_id, role)
VALUES
  (current_setting('duo.test.couple_a')::uuid, current_setting('duo.test.user_a')::uuid, 'owner'),
  (current_setting('duo.test.couple_b')::uuid, current_setting('duo.test.user_b')::uuid, 'owner');

INSERT INTO public.duo_date_plans (couple_id, created_by, plan_date, title)
VALUES
  (current_setting('duo.test.couple_a')::uuid, current_setting('duo.test.user_a')::uuid, current_date, 'Fixture A'),
  (current_setting('duo.test.couple_b')::uuid, current_setting('duo.test.user_b')::uuid, current_date, 'Fixture B');

INSERT INTO public.place_activity (couple_id, place_name, updated_by)
VALUES
  (current_setting('duo.test.couple_a')::uuid, 'RLS fixture place A', current_setting('duo.test.user_a')::uuid),
  (current_setting('duo.test.couple_b')::uuid, 'RLS fixture place B', current_setting('duo.test.user_b')::uuid);

SET LOCAL ROLE authenticated;
SELECT set_config('request.jwt.claim.sub', current_setting('duo.test.user_a'), true);
SELECT set_config('request.jwt.claims', json_build_object('sub', current_setting('duo.test.user_a'), 'role', 'authenticated')::text, true);

DO $$
DECLARE visible_count integer; affected integer;
BEGIN
  SELECT count(*) INTO visible_count FROM public.couples;
  IF visible_count <> 1 THEN RAISE EXCEPTION 'User A can see % couples; expected 1', visible_count; END IF;
  SELECT count(*) INTO visible_count FROM public.couple_members;
  IF visible_count <> 1 THEN RAISE EXCEPTION 'User A can see % memberships; expected 1', visible_count; END IF;
  SELECT count(*) INTO visible_count FROM public.duo_date_plans;
  IF visible_count <> 1 THEN RAISE EXCEPTION 'User A can see % plans; expected 1', visible_count; END IF;
  SELECT count(*) INTO visible_count FROM public.place_activity;
  IF visible_count <> 1 THEN RAISE EXCEPTION 'User A can see % activity rows; expected 1', visible_count; END IF;

  UPDATE public.duo_date_plans SET title = 'CROSS-COUPLE HACK'
    WHERE couple_id = current_setting('duo.test.couple_b')::uuid;
  GET DIAGNOSTICS affected = ROW_COUNT;
  IF affected <> 0 THEN RAISE EXCEPTION 'User A modified % plans belonging to User B', affected; END IF;

  DELETE FROM public.place_activity WHERE couple_id = current_setting('duo.test.couple_b')::uuid;
  GET DIAGNOSTICS affected = ROW_COUNT;
  IF affected <> 0 THEN RAISE EXCEPTION 'User A deleted % activity rows belonging to User B', affected; END IF;

  BEGIN
    INSERT INTO public.duo_date_plans (couple_id, created_by, plan_date, title)
    VALUES (current_setting('duo.test.couple_b')::uuid, current_setting('duo.test.user_a')::uuid, current_date, 'Cross-couple insert');
    RAISE EXCEPTION 'User A inserted a plan into User B couple';
  EXCEPTION WHEN insufficient_privilege THEN NULL;
  END;

  BEGIN
    EXECUTE 'TRUNCATE TABLE public.couples';
    RAISE EXCEPTION 'Authenticated role unexpectedly has TRUNCATE privilege';
  EXCEPTION WHEN insufficient_privilege THEN NULL;
  END;
END $$;

SELECT set_config('request.jwt.claim.sub', current_setting('duo.test.user_b'), true);
SELECT set_config('request.jwt.claims', json_build_object('sub', current_setting('duo.test.user_b'), 'role', 'authenticated')::text, true);
DO $$
DECLARE visible_count integer;
BEGIN
  SELECT count(*) INTO visible_count FROM public.couples;
  IF visible_count <> 1 THEN RAISE EXCEPTION 'User B can see % couples; expected 1', visible_count; END IF;
  SELECT count(*) INTO visible_count FROM public.duo_date_plans;
  IF visible_count <> 1 THEN RAISE EXCEPTION 'User B can see % plans; expected 1', visible_count; END IF;
  IF EXISTS (SELECT 1 FROM public.duo_date_plans WHERE title = 'CROSS-COUPLE HACK') THEN
    RAISE EXCEPTION 'Cross-couple update changed User B data';
  END IF;
END $$;

RESET ROLE;
SET LOCAL ROLE anon;
DO $$
BEGIN
  BEGIN
    PERFORM count(*) FROM public.couples;
    RAISE EXCEPTION 'anon unexpectedly has access to couples';
  EXCEPTION WHEN insufficient_privilege THEN NULL;
  END;
  BEGIN
    PERFORM count(*) FROM public.duo_event_sync_config;
    RAISE EXCEPTION 'anon unexpectedly has access to event sync config';
  EXCEPTION WHEN insufficient_privilege THEN NULL;
  END;
  BEGIN
    EXECUTE 'TRUNCATE TABLE public.places';
    RAISE EXCEPTION 'anon unexpectedly has TRUNCATE privilege';
  EXCEPTION WHEN insufficient_privilege THEN NULL;
  END;
END $$;

ROLLBACK;
