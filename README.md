# DUO — Minsk date planner

Production frontend: https://minsk-date-ideas.vercel.app

DUO helps two people discover places and events in Minsk, plan dates, save favorites, track visits and share ratings.

## Current architecture (migration to 2.0)
- Frontend: static HTML/CSS/JavaScript hosted on Vercel.
- API: FastAPI + Pydantic + SQLAlchemy 2.
- Database: PostgreSQL 17 hosted in the existing Supabase project (Frankfurt).
- Identity: Supabase Auth; FastAPI validates access tokens using the project's JWKS endpoint.
- Migrations: Alembic.
- Events: structured JSON-LD scraper in backend/app/services/event_sync.py. The existing scheduled Supabase Edge Function remains active until the FastAPI endpoint is configured and verified.

## Repository layout
- public/index.html — DUO frontend and 110-place fallback catalog.
- public/minsk-auth.js — Supabase Auth only; all application data requests go through FastAPI.
- public/duo-features.js — events, city updates and date planner via FastAPI.
- backend/app — FastAPI application, ORM models, auth and event importer.
- backend/seed/places.json — normalized public catalog source.
- backend/migrations — Alembic schema migration.
- main.py — Vercel FastAPI entry point.
- public/ — static frontend assets served by Vercel CDN.

## Local backend setup
1. Create a Python virtual environment.
2. Install root requirements.txt.
3. Copy backend/.env.example to backend/.env. Create the restricted runtime role using backend/role.sql, then set DATABASE_URL from the Supabase Transaction Pooler URI and MIGRATION_DATABASE_URL for trusted migrations.
4. From the project root, run: alembic -c backend/alembic.ini upgrade head using MIGRATION_DATABASE_URL (trusted admin connection).
5. From the project root, run: python backend/seed_places.py.
6. Run uvicorn main:app --reload from the project root.

Open /docs for Swagger UI and /api/health for the health check.

## API routes
- Public: GET /api/health, GET /api/places, GET /api/places/{slug}, GET /api/events, GET /api/updates.
- Authenticated: GET /api/me, GET /api/activity, PUT /api/activity, GET /api/plans, POST /api/plans, DELETE /api/plans/{id}.
- Couple management: POST /api/couples, POST /api/couples/join.
- Event refresh is still performed by the existing scheduled Supabase Edge Function during the API cutover.

## Security notes
- Supabase publishable key is used only for Auth client initialization; it is not a database admin key.
- No service-role key or database password belongs in frontend code or Git. The runtime DB role should be a dedicated NOINHERIT login granted membership in anon and authenticated; API requests switch roles transaction-locally so PostgreSQL RLS continues to protect couple data.
- All couple-scoped reads/writes resolve membership on the API server.
- Existing RLS policies remain enabled as defense in depth.
- Never commit .env files.

## Migration status
The places table and 110-place seed have already been applied to Supabase PostgreSQL. The local Alembic migration is idempotent for new environments. The API and frontend adapters are scaffolded; production cutover is not complete until the runtime PostgreSQL connection is configured, API endpoints are tested against the live database, and a Vercel deployment is verified end-to-end. The current production site remains the fallback during this migration.
