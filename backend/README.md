# DUO API

The FastAPI service is deployed from the repository root via main.py.

## Development
- Runtime DB connection: restricted duo_api PostgreSQL role through the Supabase Transaction Pooler.
- Migration connection: trusted admin connection, used only from a trusted environment.
- Auth: Supabase JWT/JWKS verification.
- RLS: request-scoped role switching preserves PostgreSQL row-level policies.

See the root README and docs/ARCHITECTURE.md for current production topology.

## Discovery API
- `GET /api/cities` returns active city metadata, including localized names, time zone, currency and default language.
- `GET /api/places?city=minsk`, `GET /api/events?city=minsk`, and `GET /api/updates?city=minsk` are city-scoped. The city parameter defaults to `minsk`.
- A city must be inserted and marked active only after its venue catalog and event sources pass the data-quality launch gate.
- Couple creation and invite functions live in the non-exposed `private` schema and are invoked only by the authenticated FastAPI service.
- Couple activity uses the stable `place_slug` key; venue display names are not identifiers.
