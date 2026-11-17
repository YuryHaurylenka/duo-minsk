# DUO API

The FastAPI service is deployed from the repository root via main.py.

## Development
- Runtime DB connection: restricted duo_api PostgreSQL role through the Supabase Transaction Pooler.
- Migration connection: trusted admin connection, used only from a trusted environment.
- Auth: Supabase JWT/JWKS verification.
- RLS: request-scoped role switching preserves PostgreSQL row-level policies.

See the root README and docs/ARCHITECTURE.md for current production topology.
