# DUO — date planning for two

Production: https://minsk-date-ideas.vercel.app

DUO helps two people discover places and events, build date itineraries, keep a shared history and save plans together.

## Production stack
- Client: responsive HTML/CSS/JavaScript in public/.
- API: FastAPI + Pydantic + SQLAlchemy 2.
- Database: Supabase PostgreSQL, Frankfurt.
- Identity: Supabase Auth; FastAPI verifies JWTs against the project JWKS.
- Deployment: Vercel FastAPI, function region fra1.
- Migrations: Alembic.
- Event ingestion: existing scheduled Supabase Edge Function.

## Repository layout
- public/index.html — DUO experience and initial fallback catalog.
- public/minsk-auth.js — Supabase Auth and FastAPI client.
- public/duo-features.js — events, city updates, date planner and saved plans.
- main.py — Vercel FastAPI entry point.
- backend/app/ — API, auth, ORM models, schemas and services.
- backend/seed/places.json — normalized source catalog.
- backend/migrations/ — Alembic migrations.
- docs/ — product strategy and architecture.

## API
Public:
- GET /api/health
- GET /api/places
- GET /api/places/{slug}
- GET /api/events
- GET /api/updates

Authenticated:
- GET /api/me
- POST /api/couples
- POST /api/couples/join
- GET /api/activity
- PUT /api/activity
- GET /api/plans
- POST /api/plans
- DELETE /api/plans/{id}

## Local development
1. Create a Python 3.12 virtual environment.
2. Install requirements.txt.
3. Copy backend/.env.example to backend/.env.
4. Set DATABASE_URL to the Supabase Transaction Pooler URL. Set MIGRATION_DATABASE_URL only for trusted migration runs.
5. Run alembic -c backend/alembic.ini upgrade head.
6. Run python backend/seed_places.py if initializing a fresh catalog.
7. Start uvicorn main:app --reload.

## Security
- DATABASE_URL is a sensitive Vercel environment variable, not stored in Git.
- Runtime DB role duo_api is NOINHERIT and NOBYPASSRLS; request handlers switch to anon or authenticated transaction-locally.
- Existing PostgreSQL RLS policies protect couple-scoped records.
- No Supabase service-role key is present in the client.
- Never commit .env files.

## Current status
- FastAPI is deployed to production in Frankfurt.
- Production PostgreSQL connectivity is verified through the public API.
- The live API returned places, events and editorial updates from PostgreSQL.
- 110 places, 32 current/upcoming events and 7 city updates were visible in the latest browser smoke test.
- A startup-order race between Auth and event loading was fixed.
- Public link audit: 203 unique place/source URLs; 115 returned HTTP 200, 84 returned HTTP 204 and 4 hosts blocked automated checks with 403; no 404/410 responses were found.
- Saved-plan and two-account end-to-end tests still require real test accounts.

## International expansion
Minsk is the first city, not a claim of global coverage. Read docs/GO_TO_MARKET.md before expanding to another market. The next milestones are English localization, a city data pipeline, privacy/legal readiness, payments/affiliate partnerships and retention validation.

## Important
The current Vercel deployment is deployed directly from source files. A private GitHub repository has been created; connect it to Vercel after the repository source is pushed and verified. Keep the working production deployment as the fallback until the Git-linked pipeline is proven.
