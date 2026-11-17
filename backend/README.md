# DUO API

FastAPI backend for DUO. PostgreSQL is the source of truth for places, events, couple activity and saved date plans. Existing Supabase Auth remains the identity provider so current accounts are preserved; the API validates Supabase access tokens using the project's JWKS endpoint.

## Stack
- FastAPI + Pydantic v2
- SQLAlchemy 2 + psycopg 3
- PostgreSQL (existing Supabase Postgres project)
- Alembic migrations
- Supabase Auth JWT verification (no service-role key in the browser)

## Run locally
1. Create a virtual environment and install requirements.txt.
2. From the repository root, copy backend/.env.example to backend/.env. Set DATABASE_URL to the Supabase Transaction Pooler URI and MIGRATION_DATABASE_URL to a trusted admin connection. Set the Supabase URL and publishable key.
3. Run role.sql once in Supabase SQL Editor after replacing the password placeholder. Then run alembic -c backend/alembic.ini upgrade head from the repository root.
4. Run python backend/seed_places.py from the repository root.
5. Run uvicorn main:app --reload from the repository root.

Swagger UI: /docs; health: /api/health.

## API
- Public: GET /api/health, /api/places, /api/places/{slug}, /api/events, /api/updates
- Authenticated: GET /api/me, /api/activity, PUT /api/activity, GET /api/plans, POST /api/plans, DELETE /api/plans/{id}
- Couple: POST /api/couples, POST /api/couples/join
- Scheduled event refresh: the existing Supabase Edge Function remains active during the backend cutover; the FastAPI scraper module is ready for a later secured migration.

## Security
- Access tokens are verified against Supabase Auth JWKS; expired or invalid tokens are rejected.
- Couple-scoped reads and writes always resolve membership server-side.
- Never commit .env, database passwords, JWT secrets, or service-role keys.
- Existing Supabase RLS policies remain enabled as defense in depth. The runtime login should be a dedicated NOINHERIT role granted membership in anon and authenticated so requests can SET LOCAL ROLE and let PostgreSQL enforce RLS.

## Data
seed/places.json contains the 110 public catalog entries migrated from the previous DUO frontend. User-specific activity and saved plans remain in their existing PostgreSQL tables.
app/models/entities.py maps the existing Supabase tables and the new places catalog table.
migrations/versions/0001_create_places.py creates the normalized catalog table.
seed_places.py imports the catalog idempotently.
app/services/event_sync.py parses JSON-LD Event objects from allow-listed city event sources; it is not exposed as a public route until a separate, least-privilege scheduled-job database role is configured.
