-- Run against a Supabase PostgreSQL database with a privileged test connection.
-- All fixtures are transaction-scoped and rolled back at the end.
BEGIN;

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE schemaname='public' AND indexname='couple_members_user_id_key') THEN
    RAISE EXCEPTION 'One-couple-per-user unique index is missing';
  END IF;
  IF position('FOR UPDATE' IN pg_get_functiondef('private.join_couple(text)'::regprocedure)) = 0 THEN
    RAISE EXCEPTION 'join_couple must lock the couple row before counting members';
  END IF;

  IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'duo_api')
     AND NOT pg_has_role('duo_api', 'duo_match_backend', 'MEMBER') THEN
    RAISE EXCEPTION 'duo_api must be able to SET ROLE duo_match_backend for Match API requests';
  END IF;
  IF NOT pg_has_role('duo_match_backend', 'authenticated', 'MEMBER') THEN
    RAISE EXCEPTION 'Match backend role must inherit authenticated access for shared app tables';
  END IF;
  IF NOT has_table_privilege('authenticated', 'public.duo_match_sessions', 'SELECT')
     OR has_table_privilege('authenticated', 'public.duo_match_sessions', 'INSERT')
     OR has_table_privilege('authenticated', 'public.duo_match_sessions', 'UPDATE')
     OR has_table_privilege('authenticated', 'public.duo_match_sessions', 'DELETE') THEN
    RAISE EXCEPTION 'authenticated must have SELECT-only access to Match sessions';
  END IF;
  IF has_table_privilege('authenticated', 'public.duo_match_candidates', 'SELECT')
     OR has_table_privilege('authenticated', 'public.duo_match_candidates', 'INSERT')
     OR has_table_privilege('authenticated', 'public.duo_match_candidates', 'UPDATE')
     OR has_table_privilege('authenticated', 'public.duo_match_candidates', 'DELETE') THEN
    RAISE EXCEPTION 'authenticated must not access Match candidates directly';
  END IF;
  IF has_table_privilege('authenticated', 'public.duo_match_votes', 'SELECT')
     OR has_table_privilege('authenticated', 'public.duo_match_votes', 'INSERT')
     OR has_table_privilege('authenticated', 'public.duo_match_votes', 'UPDATE')
     OR has_table_privilege('authenticated', 'public.duo_match_votes', 'DELETE') THEN
    RAISE EXCEPTION 'authenticated must not access private Match votes directly';
  END IF;
  IF NOT has_table_privilege('duo_match_backend', 'public.duo_match_sessions', 'INSERT')
     OR NOT has_table_privilege('duo_match_backend', 'public.duo_match_candidates', 'INSERT')
     OR NOT has_table_privilege('duo_match_backend', 'public.duo_match_votes', 'INSERT') THEN
    RAISE EXCEPTION 'Match backend role must retain write access to Match tables';
  END IF;

  IF NOT has_table_privilege('anon', 'public.cities', 'SELECT') THEN
    RAISE EXCEPTION 'anon must be able to read active city metadata';
  END IF;
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
  IF has_function_privilege('anon', 'private.create_couple(text)', 'EXECUTE') THEN
    RAISE EXCEPTION 'anon must not execute private.create_couple';
  END IF;
  IF NOT has_function_privilege('authenticated', 'private.create_couple(text)', 'EXECUTE') THEN
    RAISE EXCEPTION 'authenticated must be able to execute private.create_couple';
  END IF;
  IF to_regprocedure('public.create_couple(text)') IS NOT NULL OR to_regprocedure('public.join_couple(text)') IS NOT NULL THEN
    RAISE EXCEPTION 'Couple RPCs must not remain in the exposed public schema';
  END IF;
END $$;

SELECT set_config('duo.test.user_a', gen_random_uuid()::text, true);
SELECT set_config('duo.test.user_b', gen_random_uuid()::text, true);
SELECT set_config('duo.test.user_c', gen_random_uuid()::text, true);
SELECT set_config('duo.test.user_d', gen_random_uuid()::text, true);
SELECT set_config('duo.test.user_e', gen_random_uuid()::text, true);
SELECT set_config('duo.test.user_f', gen_random_uuid()::text, true);
SELECT set_config('duo.test.couple_a', gen_random_uuid()::text, true);
SELECT set_config('duo.test.couple_b', gen_random_uuid()::text, true);
SELECT set_config('duo.test.couple_c', gen_random_uuid()::text, true);

SELECT set_config('duo.test.place_slug', (SELECT p.slug FROM public.places AS p WHERE p.city_slug='minsk' ORDER BY p.slug LIMIT 1), true);
SELECT set_config('duo.test.place_name', (SELECT p.name FROM public.places AS p WHERE p.slug=current_setting('duo.test.place_slug')), true);

INSERT INTO auth.users (id, aud, role, email, encrypted_password, email_confirmed_at,
                        raw_app_meta_data, raw_user_meta_data, created_at, updated_at)
VALUES
  (current_setting('duo.test.user_a')::uuid, 'authenticated', 'authenticated',
   current_setting('duo.test.user_a') || '@duo-rls.invalid', '', now(), '{}'::jsonb, '{}'::jsonb, now(), now()),
  (current_setting('duo.test.user_b')::uuid, 'authenticated', 'authenticated',
   current_setting('duo.test.user_b') || '@duo-rls.invalid', '', now(), '{}'::jsonb, '{}'::jsonb, now(), now()),
  (current_setting('duo.test.user_c')::uuid, 'authenticated', 'authenticated',
   current_setting('duo.test.user_c') || '@duo-rls.invalid', '', now(), '{}'::jsonb, '{}'::jsonb, now(), now()),
  (current_setting('duo.test.user_d')::uuid, 'authenticated', 'authenticated',
   current_setting('duo.test.user_d') || '@duo-rls.invalid', '', now(), '{}'::jsonb, '{}'::jsonb, now(), now()),
  (current_setting('duo.test.user_e')::uuid, 'authenticated', 'authenticated',
   current_setting('duo.test.user_e') || '@duo-rls.invalid', '', now(), '{}'::jsonb, '{}'::jsonb, now(), now()),
  (current_setting('duo.test.user_f')::uuid, 'authenticated', 'authenticated',
   current_setting('duo.test.user_f') || '@duo-rls.invalid', '', now(), '{}'::jsonb, '{}'::jsonb, now(), now());

INSERT INTO public.couples (id, name, created_by)
VALUES
  (current_setting('duo.test.couple_a')::uuid, 'RLS fixture A', current_setting('duo.test.user_a')::uuid),
  (current_setting('duo.test.couple_b')::uuid, 'RLS fixture B', current_setting('duo.test.user_b')::uuid),
  (current_setting('duo.test.couple_c')::uuid, 'RLS fixture C', current_setting('duo.test.user_c')::uuid);

SELECT set_config('duo.test.invite_b', (SELECT c.invite_code FROM public.couples AS c WHERE c.id=current_setting('duo.test.couple_b')::uuid), true);
SELECT set_config('duo.test.invite_c', (SELECT c.invite_code FROM public.couples AS c WHERE c.id=current_setting('duo.test.couple_c')::uuid), true);

INSERT INTO public.couple_members (couple_id, user_id, role)
VALUES
  (current_setting('duo.test.couple_a')::uuid, current_setting('duo.test.user_a')::uuid, 'owner'),
  (current_setting('duo.test.couple_b')::uuid, current_setting('duo.test.user_b')::uuid, 'owner'),
  (current_setting('duo.test.couple_c')::uuid, current_setting('duo.test.user_c')::uuid, 'owner'),
  (current_setting('duo.test.couple_a')::uuid, current_setting('duo.test.user_f')::uuid, 'member');

INSERT INTO public.duo_date_plans (couple_id, created_by, plan_date, title)
VALUES
  (current_setting('duo.test.couple_a')::uuid, current_setting('duo.test.user_a')::uuid, current_date, 'Fixture A'),
  (current_setting('duo.test.couple_b')::uuid, current_setting('duo.test.user_b')::uuid, current_date, 'Fixture B');

INSERT INTO public.place_activity (couple_id, place_slug, place_name, updated_by)
VALUES
  (current_setting('duo.test.couple_a')::uuid, current_setting('duo.test.place_slug'), current_setting('duo.test.place_name'), current_setting('duo.test.user_a')::uuid),
  (current_setting('duo.test.couple_b')::uuid, current_setting('duo.test.place_slug'), current_setting('duo.test.place_name'), current_setting('duo.test.user_b')::uuid);

SELECT set_config('duo.test.match_session_a', gen_random_uuid()::text, true);
SELECT set_config('duo.test.match_session_b', gen_random_uuid()::text, true);

INSERT INTO public.duo_match_sessions (id, couple_id, city_slug, created_by)
VALUES
  (current_setting('duo.test.match_session_a')::uuid, current_setting('duo.test.couple_a')::uuid, 'minsk', current_setting('duo.test.user_a')::uuid),
  (current_setting('duo.test.match_session_b')::uuid, current_setting('duo.test.couple_b')::uuid, 'minsk', current_setting('duo.test.user_b')::uuid);

INSERT INTO public.duo_match_candidates (session_id, place_slug, position)
VALUES
  (current_setting('duo.test.match_session_a')::uuid, current_setting('duo.test.place_slug'), 1),
  (current_setting('duo.test.match_session_b')::uuid, current_setting('duo.test.place_slug'), 1);

INSERT INTO public.duo_match_votes (session_id, place_slug, user_id, liked)
VALUES
  (current_setting('duo.test.match_session_a')::uuid, current_setting('duo.test.place_slug'), current_setting('duo.test.user_a')::uuid, true),
  (current_setting('duo.test.match_session_a')::uuid, current_setting('duo.test.place_slug'), current_setting('duo.test.user_f')::uuid, false),
  (current_setting('duo.test.match_session_b')::uuid, current_setting('duo.test.place_slug'), current_setting('duo.test.user_b')::uuid, true);

SET LOCAL ROLE authenticated;
SELECT set_config('request.jwt.claim.sub', current_setting('duo.test.user_a'), true);
SELECT set_config('request.jwt.claims', json_build_object('sub', current_setting('duo.test.user_a'), 'role', 'authenticated')::text, true);

DO $$
DECLARE visible_count integer; affected integer;
BEGIN
  SELECT count(*) INTO visible_count FROM public.couples;
  IF visible_count <> 1 THEN RAISE EXCEPTION 'User A can see % couples; expected 1', visible_count; END IF;
  SELECT count(*) INTO visible_count FROM public.couple_members;
  IF visible_count <> 2 THEN RAISE EXCEPTION 'User A can see % memberships; expected 2', visible_count; END IF;
  SELECT count(*) INTO visible_count FROM public.duo_date_plans;
  IF visible_count <> 1 THEN RAISE EXCEPTION 'User A can see % plans; expected 1', visible_count; END IF;

  SELECT count(*) INTO visible_count FROM public.duo_match_sessions;
  IF visible_count <> 1 THEN RAISE EXCEPTION 'User A must only see their own Match session; found %', visible_count; END IF;
  BEGIN
    PERFORM count(*) FROM public.duo_match_votes;
    RAISE EXCEPTION 'authenticated unexpectedly read private Match votes';
  EXCEPTION WHEN insufficient_privilege THEN NULL;
  END;
  BEGIN
    UPDATE public.duo_match_sessions SET activity_version = activity_version + 1
      WHERE id = current_setting('duo.test.match_session_a')::uuid;
    RAISE EXCEPTION 'authenticated unexpectedly updated Match session metadata';
  EXCEPTION WHEN insufficient_privilege THEN NULL;
  END;
  SELECT count(*) INTO visible_count FROM public.place_activity;
  IF visible_count <> 1 THEN RAISE EXCEPTION 'User A can see % activity rows; expected 1', visible_count; END IF;

  UPDATE public.duo_date_plans SET title = 'CROSS-COUPLE HACK'
    WHERE couple_id = current_setting('duo.test.couple_b')::uuid;
  GET DIAGNOSTICS affected = ROW_COUNT;
  IF affected <> 0 THEN RAISE EXCEPTION 'User A modified % plans belonging to User B', affected; END IF;

  BEGIN
    UPDATE public.duo_date_plans
      SET updated_by = current_setting('duo.test.user_b')::uuid
      WHERE couple_id = current_setting('duo.test.couple_a')::uuid;
    RAISE EXCEPTION 'User A forged another member plan editor identity';
  EXCEPTION WHEN insufficient_privilege THEN NULL;
  END;

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


-- The API-only role can inspect both votes inside the current couple, but
-- cannot read another couple's session or change the partner's vote.
RESET ROLE;
SET LOCAL ROLE duo_match_backend;
SELECT set_config('request.jwt.claim.sub', current_setting('duo.test.user_a'), true);
SELECT set_config('request.jwt.claims', json_build_object('sub', current_setting('duo.test.user_a'), 'role', 'authenticated')::text, true);
DO $$
DECLARE visible_count integer; affected integer;
BEGIN
  SELECT count(*) INTO visible_count FROM public.duo_match_sessions;
  IF visible_count <> 1 THEN RAISE EXCEPTION 'Match backend saw % sessions for User A; expected 1', visible_count; END IF;
  SELECT count(*) INTO visible_count FROM public.duo_match_candidates;
  IF visible_count <> 1 THEN RAISE EXCEPTION 'Match backend saw % candidates for User A; expected 1', visible_count; END IF;
  SELECT count(*) INTO visible_count FROM public.duo_match_votes;
  IF visible_count <> 2 THEN RAISE EXCEPTION 'Match backend saw % couple votes; expected 2', visible_count; END IF;

  UPDATE public.duo_match_votes SET liked = true
    WHERE session_id = current_setting('duo.test.match_session_a')::uuid
      AND user_id = current_setting('duo.test.user_f')::uuid;
  GET DIAGNOSTICS affected = ROW_COUNT;
  IF affected <> 0 THEN RAISE EXCEPTION 'Match backend changed the partner vote'; END IF;

  UPDATE public.duo_match_votes SET liked = false
    WHERE session_id = current_setting('duo.test.match_session_a')::uuid
      AND user_id = current_setting('duo.test.user_a')::uuid;
  GET DIAGNOSTICS affected = ROW_COUNT;
  IF affected <> 1 THEN RAISE EXCEPTION 'Match backend could not update the current user vote'; END IF;

  UPDATE public.duo_match_sessions SET activity_version = activity_version + 1
    WHERE id = current_setting('duo.test.match_session_a')::uuid;
  GET DIAGNOSTICS affected = ROW_COUNT;
  IF affected <> 1 THEN RAISE EXCEPTION 'Match backend could not update its couple session'; END IF;
END $$;

RESET ROLE;
SET LOCAL ROLE authenticated;
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

-- A user who already belongs to a couple cannot join another one.
SELECT set_config('request.jwt.claim.sub', current_setting('duo.test.user_a'), true);
SELECT set_config('request.jwt.claims', json_build_object('sub', current_setting('duo.test.user_a'), 'role', 'authenticated')::text, true);
DO $$
DECLARE invite text; blocked boolean := false;
BEGIN
  invite := current_setting('duo.test.invite_b');
  BEGIN
    PERFORM * FROM private.join_couple(invite);
  EXCEPTION WHEN raise_exception THEN
    IF SQLERRM = 'User already belongs to another couple' THEN blocked := true; ELSE RAISE; END IF;
  END;
  IF NOT blocked THEN RAISE EXCEPTION 'A user joined a second couple'; END IF;
END $$;

-- The second member can join; a third member must be rejected.
SELECT set_config('request.jwt.claim.sub', current_setting('duo.test.user_d'), true);
SELECT set_config('request.jwt.claims', json_build_object('sub', current_setting('duo.test.user_d'), 'role', 'authenticated')::text, true);
DO $$
DECLARE invite text; member_count integer; blocked boolean := false;
BEGIN
  invite := current_setting('duo.test.invite_c');
  PERFORM * FROM private.join_couple(invite);
  SELECT count(*) INTO member_count FROM public.couple_members WHERE couple_id=current_setting('duo.test.couple_c')::uuid;
  IF member_count <> 2 THEN RAISE EXCEPTION 'Expected two members after valid invite, found %', member_count; END IF;
END $$;

SELECT set_config('request.jwt.claim.sub', current_setting('duo.test.user_e'), true);
SELECT set_config('request.jwt.claims', json_build_object('sub', current_setting('duo.test.user_e'), 'role', 'authenticated')::text, true);
DO $$
DECLARE invite text; blocked boolean := false;
BEGIN
  invite := current_setting('duo.test.invite_c');
  BEGIN
    PERFORM * FROM private.join_couple(invite);
  EXCEPTION WHEN raise_exception THEN
    IF SQLERRM = 'В паре уже два участника' THEN blocked := true; ELSE RAISE; END IF;
  END;
  IF NOT blocked THEN RAISE EXCEPTION 'A third member joined a full couple'; END IF;
END $$;

RESET ROLE;
SET LOCAL ROLE anon;
DO $$
DECLARE city_count integer;
BEGIN
  SELECT count(*) INTO city_count FROM public.cities;
  IF city_count <> 1 THEN RAISE EXCEPTION 'Expected one active city, found %', city_count; END IF;
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
