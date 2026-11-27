-- Old one-off listings must not remain in the upcoming feed just because a
-- source page advertises an artificially distant end date.
UPDATE public.duo_events
SET status = 'ended', updated_at = now()
WHERE status = 'scheduled'
  AND starts_at < now() - interval '365 days';
