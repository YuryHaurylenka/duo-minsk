# DUO architecture

## Production topology
- Vercel serves the static client from public/ and the FastAPI application from main.py.
- FastAPI is deployed in fra1 (Frankfurt).
- PostgreSQL remains in Supabase Frankfurt.
- Supabase Auth provides identity; FastAPI validates JWTs using the project's JWKS endpoint.
- Runtime DB access uses the dedicated duo_api login with NOINHERIT and NOBYPASSRLS.
- The API switches transaction-locally to anon for public endpoints and to authenticated after JWT validation, setting Supabase request claims so existing RLS policies continue to apply.
- Public API roles have least-privilege grants: read-only public catalog access, no access to event-sync control tables, and no TRUNCATE/REFERENCES/TRIGGER privileges. Future objects created by postgres receive no broad API-role grants by default.
- The Supabase publishable key is used only by the browser Auth SDK; it is not a secret.
- The existing Supabase Edge Function continues to refresh the event catalog on its scheduled cadence.

## Data boundaries
- Public: active places, scheduled events, editorial city updates.
- Couple-private: memberships, shared activity, saved date plans.
- Private backend credentials: PostgreSQL login password and Supabase service-role material (not present in the browser or repository).

## Runtime routes
- GET /api/health
- GET /api/places, GET /api/places/{slug}
- GET /api/events, GET /api/updates
- Authenticated: /api/me, /api/couples, /api/couples/join, /api/activity, /api/plans

## Deployment
- main.py is the Vercel FastAPI entry point.
- Root requirements.txt pins Python dependencies.
- .python-version pins the deployment runtime to Python 3.12.
- Vercel environment variables must never be committed.
- Database migrations are applied by a trusted operator connection; runtime uses the restricted pooler login.

## Operational risks
- Vercel Hobby has limits and is not an assumption for high-traffic scale. Revisit hosting, background jobs and observability after real usage.
- Event ingestion currently relies on a small set of Minsk sources and structured event metadata. A missing structured feed can reduce coverage.
- City openings/closures are editorially curated; they are not yet fully automated.
- Couple realtime uses Supabase Realtime; SQL-level two-user RLS isolation is verified, but browser-level realtime behavior still needs two real accounts before calling the feature fully production-verified.
- See docs/SECURITY.md for database role boundaries, live security checks and the transaction-scoped RLS integration test.
