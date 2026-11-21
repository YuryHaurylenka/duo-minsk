-- Expose only the shared session metadata as a safe Realtime change signal.
-- Partner votes remain in duo_match_votes and are never sent over this channel.
ALTER TABLE public.duo_match_sessions
    ADD COLUMN activity_version bigint NOT NULL DEFAULT 0;

ALTER PUBLICATION supabase_realtime
    ADD TABLE public.duo_match_sessions;
