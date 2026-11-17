![DUO CI](https://github.com/YuryHaurylenka/duo-minsk/actions/workflows/ci.yml/badge.svg)

# DUO — date planning for two

Production: https://minsk-date-ideas.vercel.app

DUO helps two people discover places and events, build date itineraries, keep a shared history and save plans together.

## Production stack
- Client: responsive HTML/CSS/JavaScript in public/.
- API: FastAPI + Pydantic + SQLAlchemy 2.
- Database: Supabase PostgreSQL, Frankfurt.
- Identity: Supabase Auth; FastAPI verifies JWTs against the project JWKS.
- Deployment: Vercel FastAPI, function region fra1.
- Migrations: Alembic for the API schema plus tracked Supabase SQL migrations for managed database security and indexes.
- Event ingestion: existing scheduled Supabase Edge Function.

## Repository layout
- public/index.html — DUO experience and initial fallback catalog.
- public/minsk-auth.js — Supabase Auth and FastAPI client.
- public/duo-features.js — events, city updates, date planner and saved plans.
- main.py — Vercel FastAPI entry point.
- backend/app/ — API, auth, ORM models, schemas and services.
- backend/seed/places.json — normalized source catalog.
- backend/migrations/ — Alembic migrations.
- docs/ — product strategy, architecture and security runbooks.
- supabase/migrations/ — tracked Supabase database security and performance migrations.
- supabase/tests/database/ — transaction-scoped PostgreSQL isolation checks.

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
- PostgreSQL RLS policies protect couple-scoped records; public API roles use least-privilege table grants and cannot TRUNCATE application tables.
- Transaction-scoped two-user RLS isolation checks live in `supabase/tests/database/rls_isolation.sql`; see `docs/SECURITY.md`.
- No Supabase service-role key is present in the client.
- Never commit .env files.

## Current status
- FastAPI is deployed to production in Frankfurt.
- Production PostgreSQL connectivity is verified through the public API.
- The live API returned places, events and editorial updates from PostgreSQL.
- 110 places, 65 current/upcoming events and 7 city updates were returned by the latest production API smoke test.
- A startup-order race between Auth and event loading was fixed.
- Public link audit: 203 unique place/source URLs; 115 returned HTTP 200, 84 returned HTTP 204 and 4 hosts blocked automated checks with 403; no 404/410 responses were found.
- Saved-plan and two-account end-to-end tests still require real test accounts.

## International expansion
Minsk is the first city, not a claim of global coverage. Read docs/GO_TO_MARKET.md before expanding to another market. The next milestones are English localization, a city data pipeline, privacy/legal readiness, payments/affiliate partnerships and retention validation.

## Delivery pipeline
- Private GitHub repository: https://github.com/YuryHaurylenka/duo-minsk
- Vercel is linked to the GitHub repository and automatically deploys `main` to production.
- GitHub Actions runs the backend test suite on pushes and pull requests.
- Keep database migrations reviewed and explicit; do not place production secrets in GitHub or the browser.
