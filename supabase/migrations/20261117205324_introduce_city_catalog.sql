CREATE TABLE public.cities (
  slug text PRIMARY KEY,
  name text NOT NULL,
  country_code char(2) NOT NULL,
  country_name text NOT NULL,
  timezone text NOT NULL,
  currency_code char(3) NOT NULL,
  default_language text NOT NULL,
  is_active boolean NOT NULL DEFAULT false,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT cities_slug_format CHECK (slug ~ '^[a-z0-9]+(?:-[a-z0-9]+)*$'),
  CONSTRAINT cities_country_code_format CHECK (country_code ~ '^[A-Z]{2}$'),
  CONSTRAINT cities_currency_code_format CHECK (currency_code ~ '^[A-Z]{3}$')
);

INSERT INTO public.cities
  (slug, name, country_code, country_name, timezone, currency_code, default_language, is_active)
VALUES
  ('minsk', 'Minsk', 'BY', 'Belarus', 'Europe/Minsk', 'BYN', 'ru', true);

ALTER TABLE public.cities ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Public can read active cities"
  ON public.cities FOR SELECT TO anon, authenticated
  USING (is_active IS TRUE);
GRANT SELECT ON TABLE public.cities TO anon, authenticated;

ALTER TABLE public.places
  ADD COLUMN city_slug text NOT NULL DEFAULT 'minsk'
  REFERENCES public.cities(slug);
ALTER TABLE public.duo_events
  ADD COLUMN city_slug text NOT NULL DEFAULT 'minsk'
  REFERENCES public.cities(slug);
ALTER TABLE public.duo_place_updates
  ADD COLUMN city_slug text NOT NULL DEFAULT 'minsk'
  REFERENCES public.cities(slug);
ALTER TABLE public.duo_event_sources
  ADD COLUMN city_slug text NOT NULL DEFAULT 'minsk'
  REFERENCES public.cities(slug);
ALTER TABLE public.duo_event_sync_runs
  ADD COLUMN city_slug text NOT NULL DEFAULT 'minsk'
  REFERENCES public.cities(slug);

CREATE INDEX places_city_active_category_idx
  ON public.places (city_slug, is_active, category);
CREATE INDEX duo_events_city_starts_at_idx
  ON public.duo_events (city_slug, starts_at);
CREATE INDEX duo_place_updates_city_reported_on_idx
  ON public.duo_place_updates (city_slug, reported_on DESC);
CREATE INDEX duo_event_sources_city_enabled_idx
  ON public.duo_event_sources (city_slug, enabled);
