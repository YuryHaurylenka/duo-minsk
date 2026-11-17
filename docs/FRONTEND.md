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
