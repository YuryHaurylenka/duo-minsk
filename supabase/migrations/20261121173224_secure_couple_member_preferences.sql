CREATE OR REPLACE FUNCTION private.set_couple_member_preferences(
    target_couple uuid,
    target_preferences jsonb
)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = ''
AS $function$
DECLARE
    requesting_user uuid := (SELECT auth.uid());
BEGIN
    IF requesting_user IS NULL THEN
        RAISE EXCEPTION 'Authentication required' USING ERRCODE = '42501';
    END IF;

    IF jsonb_typeof(target_preferences) IS DISTINCT FROM 'object'
       OR jsonb_typeof(target_preferences -> 'interests') IS DISTINCT FROM 'array'
       OR jsonb_typeof(target_preferences -> 'avoid') IS DISTINCT FROM 'array'
       OR jsonb_array_length(target_preferences -> 'interests') > 7
       OR jsonb_array_length(target_preferences -> 'avoid') > 4
       OR target_preferences - ARRAY['interests', 'avoid'] <> '{}'::jsonb
    THEN
        RAISE EXCEPTION 'Invalid preference payload' USING ERRCODE = '22023';
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM public.couple_members
        WHERE couple_id = target_couple
          AND user_id = requesting_user
    ) THEN
        RAISE EXCEPTION 'User is not a member of this couple' USING ERRCODE = '42501';
    END IF;

    UPDATE public.couples
    SET preferences = jsonb_set(
        COALESCE(preferences, '{"members": {}}'::jsonb),
        ARRAY['members', requesting_user::text],
        target_preferences,
        true
    )
    WHERE id = target_couple;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Couple not found' USING ERRCODE = 'P0002';
    END IF;

    RETURN target_preferences;
END;
$function$;

REVOKE ALL ON FUNCTION private.set_couple_member_preferences(uuid, jsonb) FROM PUBLIC, anon;
GRANT EXECUTE ON FUNCTION private.set_couple_member_preferences(uuid, jsonb) TO authenticated;
