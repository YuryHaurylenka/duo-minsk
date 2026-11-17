-- The unique index on user_id also covers the membership foreign key lookup.
DROP INDEX IF EXISTS public.couple_members_user_idx;
