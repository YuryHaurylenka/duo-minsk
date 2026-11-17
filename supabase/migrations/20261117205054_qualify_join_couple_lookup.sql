-- Avoid ambiguity with the RETURNS TABLE output column named invite_code.
CREATE OR REPLACE FUNCTION public.join_couple(code text)
RETURNS TABLE(id uuid, name text, invite_code text)
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path TO ''
AS $function$
DECLARE
  target public.couples%rowtype;
BEGIN
  IF auth.uid() IS NULL THEN
    RAISE EXCEPTION 'Authentication required';
  END IF;

  SELECT c.* INTO target
  FROM public.couples AS c
  WHERE c.invite_code = upper(trim(code))
  FOR UPDATE OF c;

  IF target.id IS NULL THEN
    RAISE EXCEPTION 'Неверный код приглашения';
  END IF;

  IF EXISTS (
    SELECT 1 FROM public.couple_members AS cm
    WHERE cm.user_id = auth.uid() AND cm.couple_id <> target.id
  ) THEN
    RAISE EXCEPTION 'User already belongs to another couple';
  END IF;

  IF (
    SELECT count(*) FROM public.couple_members AS cm WHERE cm.couple_id = target.id
  ) >= 2 AND NOT EXISTS (
    SELECT 1 FROM public.couple_members AS cm
    WHERE cm.couple_id = target.id AND cm.user_id = auth.uid()
  ) THEN
    RAISE EXCEPTION 'В паре уже два участника';
  END IF;

  BEGIN
    INSERT INTO public.couple_members(couple_id, user_id, role)
    VALUES (target.id, auth.uid(), 'member')
    ON CONFLICT (couple_id, user_id) DO NOTHING;
  EXCEPTION WHEN unique_violation THEN
    RAISE EXCEPTION 'User already belongs to another couple';
  END;

  RETURN QUERY
  SELECT c.id, c.name, c.invite_code
  FROM public.couples AS c
  WHERE c.id = target.id;
END;
$function$;
