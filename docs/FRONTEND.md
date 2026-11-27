# DUO frontend

The production interface is a React 19 single-page app built with Vite.

## Stack

- React 19 + Vite
- Framer Motion for page and card transitions
- Recharts for couple analytics
- Lucide icons
- Supabase Auth and Realtime
- Existing FastAPI endpoints under `/api`

## Local development

1. Install Node.js 20.19+ (or 22.12+).
2. From the repository root run `npm ci`.
3. Start the API in a separate terminal using the existing Python setup.
4. Run `npm run dev` and open the local Vite address.

Vite proxies `/api` requests to `http://127.0.0.1:8000`. The dev server binds to loopback only.

## Production

Vercel keeps the FastAPI framework for API functions and runs `npm ci && npm run build` before deployment. Vite writes the SPA entry point and hashed static assets to `public/`; the existing Python API remains in `main.py` and `backend/`.

## Continuous integration

Every push and pull request targeting `main` runs three independent checks:

- **Backend tests:** install the pinned Python dependencies and run the Pytest suite.
- **Frontend production build:** install the lockfile-exact npm dependencies with `npm ci` and run `npm run build`.
- **Browser smoke tests:** install Chromium and exercise the main discovery flows, photo attribution and honest image fallbacks with Playwright.

PostgreSQL RLS isolation tests run when the optional `DUO_RLS_TEST_DATABASE_URL` GitHub secret is configured. The frontend build and browser smoke jobs do not need production credentials.

## Current interface areas

- Discovery: curated categories, city updates, events and place cards
- Date planner: date, mood, couple budget and event-aware suggestions
- Saved places: search, categories and favorites
- Couple analytics: favorites, visits, ratings and category preferences
- Couple space: invite code, shared plans and visit history
- Account: Supabase email/password registration, login and logout

## Data integrity notes

- City choices come only from active rows returned by `GET /api/cities`.
- Favorites, visits and ratings use canonical `place_slug` keys.
- Guest activity is stored locally and can be merged into a couple after sign-in.
- Couple activity and plans are loaded through authenticated FastAPI endpoints and refreshed with Supabase Realtime.
- Analytics are derived from saved activity. They are not synthetic sample metrics.
- Current place-card photos are category-level editorial imagery unless a place provides its own `image_url`; they should not be presented as verified venue photographs.

## Quality checks (2026-11-27)

- GitHub Actions passed all three jobs on the photo-attribution implementation: backend tests, frontend production build, and Chromium browser smoke tests.
- Live preview smoke checks returned HTTP 200 for health, database readiness, cities, places, events, updates, and the SPA entry point.
- Live catalog: 182 active places, 60 scheduled events (59 upcoming and 1 currently running), and 7 city updates.
- Catalog integrity: no empty descriptions or addresses, no missing place source URLs, no duplicate normalized active names, and no out-of-range coordinates. One active place still has no verified coordinates; it is intentionally not assigned an estimate.
- Pricing and official-site coverage remain editorial work: 157 places have no numeric cost and 116 have no website URL; 66 have an official website URL. Unknown values are labelled as needing confirmation rather than fabricated.
- Photo integrity: all 18 active venue photos have a stored source, author, license label, and license URL. Other places use the labelled category placeholder instead of unrelated stock photography.
- The API filters events by their end time. A maintenance pass also moved 12 already-ended Hubl sessions out of the `scheduled` state; they are no longer counted as upcoming.

### Development-toolchain advisory

The full development dependency audit still reports the upstream picomatch ReDoS advisory (GHSA-fc5q-39xc-vjpf) through Vite's build-time glob dependencies. As of 2026-11-18, the npm registry still serves picomatch 4.0.7 and has no 4.0.8 release; the upstream fix discussion remains open. This dependency is not part of the deployed browser bundle. The Vite development server is bound to loopback (`127.0.0.1`) and should not be exposed to untrusted networks. Re-run the full audit and upgrade picomatch as soon as an official fixed release is available.

References: [GitHub advisory](https://github.com/advisories/GHSA-fc5q-39xc-vjpf), [upstream issue](https://github.com/micromatch/picomatch/issues/247).

### Supavisor / Psycopg transaction-pooler fix

Production browser testing exposed intermittent HTTP 500 responses from database-backed endpoints. Vercel runtime logs showed Psycopg configured with prepare_threshold=0, causing immediate server-side prepared statements, followed by DuplicatePreparedStatement and InvalidSqlStatementName when Supavisor transaction mode reassigned backend sessions. The SQLAlchemy engine now passes prepare_threshold=None, which disables Psycopg prepared statements as required by Supavisor transaction mode. A regression test protects this setting. This follows the current [Supabase guidance for Psycopg](https://supabase.com/kb/troubleshooting/disabling-prepared-statements-qL8lEL) and [Psycopg connection documentation](https://www.psycopg.org/psycopg3/docs/advanced/prepare.html).
