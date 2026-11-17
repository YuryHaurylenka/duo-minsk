alter table public.places
    add column if not exists latitude double precision,
    add column if not exists longitude double precision,
    add column if not exists location_verified_at timestamptz;

create index if not exists places_city_coordinates_idx
    on public.places (city_slug)
    where latitude is not null and longitude is not null;
