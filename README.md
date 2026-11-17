<!-- DUO README | Product-first, backend-focused -->

<div align="center">

# DUO
### Make time together count.

**A shared space for discovering places, choosing what to do, and planning experiences together.**

[Open DUO](https://minsk-date-ideas.vercel.app) · [Report an issue](https://github.com/YuryHaurylenka/duo-minsk/issues)

<br/>

![CI](https://github.com/YuryHaurylenka/duo-minsk/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/API-FastAPI-009688?logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-4169E1?logo=postgresql&logoColor=white)
![Status](https://img.shields.io/badge/Status-Active%20development-8B5CF6)

</div>

---

## The idea

Choosing a place or planning a date should feel easy.

DUO helps couples and friends discover things to do, make decisions together, save ideas, and turn them into shared plans. Minsk is the first city in the catalog; the product is being built with a foundation for expanding to other cities and activity categories.

## What you can do

| Discover | Decide together | Keep the memories |
|:--|:--|:--|
| Explore places and local events | Create a shared couple space | Save favorites and plans |
| Search by category and district | Compare preferences and votes | Keep a shared activity history |
| View places on an interactive map | Find ideas that work for both | Rate places and add personal notes |
| Build an evening plan | Coordinate a date itinerary | Return to ideas you liked |

> The product is evolving. Some collaborative flows still need end-to-end verification with two real user accounts.

## Product preview

<div align="center">

[**Explore the live application →**](https://minsk-date-ideas.vercel.app)

</div>

## Engineering

DUO is built around a Python backend, a relational data model, and explicit access boundaries for shared data.

```text
                         ┌─────────────────────┐
                         │     Web client      │
                         │  responsive UI      │
                         └──────────┬──────────┘
                                    │ HTTPS / JWT
                                    ▼
                         ┌─────────────────────┐
                         │     FastAPI         │
                         │ routes · schemas    │
                         │ services · auth     │
                         └──────────┬──────────┘
                                    │ SQLAlchemy 2
                                    ▼
                         ┌─────────────────────┐
                         │  PostgreSQL         │
                         │  Supabase           │
                         │  RLS · migrations   │
                         └─────────────────────┘
```

### Core stack

| Area | Technology |
|---|---|
| Backend | **Python 3.12, FastAPI, Pydantic** |
| ORM & database access | **SQLAlchemy 2** |
| Database | **PostgreSQL (Supabase)** |
| Authentication | Supabase Auth, JWT verification via JWKS |
| Schema migrations | Alembic + versioned Supabase SQL migrations |
| Frontend | React + Vite |
| Deployment | Vercel (API and web client) |
| Quality | Pytest, GitHub Actions, PostgreSQL isolation checks |

## Architecture at a glance

- **API-first backend** — request handling, validation, authentication, and business logic are separated into focused modules.
- **Typed data layer** — SQLAlchemy 2 models and Pydantic schemas define the application contracts.
- **User-scoped access** — JWT identity is verified by the API; PostgreSQL Row-Level Security protects couple-related records.
- **Explicit migrations** — application schema changes and database security changes are version-controlled.
- **Multi-city foundation** — city-aware endpoints make it possible to add locations without mixing unverified catalog data.
- **Automated checks** — backend tests run in GitHub Actions on pushes and pull requests.

## API

Interactive API documentation is available when running the backend locally:

- Swagger UI: `/docs`
- ReDoc: `/redoc`

A few key routes:

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/health` | Service health |
| GET | `/api/cities` | Active cities |
| GET | `/api/places` | Discover places |
| GET | `/api/places/{slug}` | Place details |
| GET | `/api/events` | Local events |
| GET | `/api/activity` | User activity |
| PUT | `/api/activity` | Update activity |
| GET | `/api/plans` | Saved plans |
| POST | `/api/plans` | Create a plan |

Authenticated routes require a valid Supabase access token.

## Run locally

### Requirements

- Python 3.12
- Node.js and npm
- A Supabase project (PostgreSQL + Auth)

### Backend

```bash
git clone https://github.com/YuryHaurylenka/duo-minsk.git
cd duo-minsk

python3.12 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
cp backend/.env.example backend/.env
```

Configure the environment variables in `backend/.env`. Set `DATABASE_URL` to the Supabase Transaction Pooler connection string. Use `MIGRATION_DATABASE_URL` only for trusted migration operations.

Apply migrations and start the API:

```bash
alembic -c backend/alembic.ini upgrade head
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

### Frontend

The frontend source and scripts are maintained separately. See [docs/FRONTEND.md](docs/FRONTEND.md) for the current build, local development, and deployment instructions.

## Security principles

- Secrets belong in environment variables, never in source control.
- The Supabase service-role key must never be exposed to the browser.
- Couple data is protected with PostgreSQL RLS policies.
- The API verifies user identity before accessing protected operations.
- Database permissions follow least-privilege principles.
- Never commit `.env` files or production credentials.

For implementation details, see [SECURITY.md](docs/SECURITY.md).

## Project structure

```text
.
├── backend/
│   ├── app/                 # API, auth, models, schemas and services
│   ├── migrations/          # Alembic migrations
│   └── seed/                # Catalog source data
├── public/                  # Web application assets and entry point
├── supabase/
│   ├── migrations/          # Database security and performance SQL
│   ├── tests/               # PostgreSQL isolation checks
│   └── functions/           # Scheduled event ingestion
├── docs/                    # Architecture, frontend and security docs
├── main.py                  # FastAPI application entry point
└── requirements.txt
```

## Roadmap

- [ ] Strengthen end-to-end coverage for authentication and shared couple flows
- [ ] Improve collaborative planning and date recommendations
- [ ] Expand verified places and event coverage
- [ ] Add more cities with localized catalogs
- [ ] Explore additional shared-interest categories: movies, food, games, and trips
- [ ] Introduce AI-assisted recommendations grounded in real catalog data

## Documentation

- [Frontend guide](docs/FRONTEND.md)
- [Security notes](docs/SECURITY.md)
- [Product and market direction](docs/GO_TO_MARKET.md)

---

<div align="center">

**Built with Python, FastAPI, PostgreSQL, and a lot of care.**

[Live application](https://minsk-date-ideas.vercel.app) · [GitHub repository](https://github.com/YuryHaurylenka/duo-minsk)

</div>
