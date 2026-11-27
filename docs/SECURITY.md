# DUO database security checks

## Access model

- `duo_api` is the private runtime login (`NOINHERIT`, `NOBYPASSRLS`). It is never shipped to the browser.
- `duo_match_backend` is a non-login, `NOBYPASSRLS` role that `duo_api` can assume only for Match API requests. It inherits the authenticated access model for other shared tables and has explicit couple-scoped RLS policies for Match data.
- Public catalog roles (`anon`, `authenticated`) have read-only access to active `cities` and to `places`, `duo_events`, and `duo_place_updates` scoped by city. City rows are visible only while `is_active = true`.
- Couple tables (`couples`, `couple_members`, `duo_date_plans`, `place_activity`) are available only to `authenticated`, with row access constrained by the couple-membership RLS policies. A unique index guarantees one couple per user; invite joins lock the couple row before checking its two-member limit.
- Event-ingestion control tables (`duo_event_sources`, `duo_event_sync_config`, `duo_event_sync_runs`) are not granted to `anon` or `authenticated`; the trusted ingestion runtime uses its privileged server-side credential.
- Match browser access is read-only: `authenticated` can only SELECT couple-scoped session metadata for Realtime. It has no direct grants on Match candidates or votes. The FastAPI-only `duo_match_backend` role handles Match reads/writes; raw partner votes are never exposed through the browser Data API.
- `TRUNCATE`, `REFERENCES`, and `TRIGGER` are revoked from API roles across the exposed `public` schema.
- All couple SECURITY DEFINER functions (`is_couple_member`, `create_couple`, `join_couple`) live in the non-exposed `private` schema. Only `authenticated` and `service_role` can execute them; the create/join functions are invoked through FastAPI, not exposed as PostgREST RPCs.
- Default table, function, and sequence grants for objects created by `postgres` in `public` are restricted. New API-facing objects must receive explicit grants and RLS policies.

## Database tests

`supabase/tests/database/rls_isolation.sql` is a transaction-scoped integration test. It creates six synthetic Auth users, three couples, private activity/plans, and two Match rounds. It switches between the real `authenticated`, `anon`, and `duo_match_backend` database roles to check cross-couple isolation, invite limits, Match session/vote isolation, each partner's ability to cast their own vote, mutual-like detection, and privilege boundaries, then rolls everything back.

Run the entire SQL file using a trusted PostgreSQL connection in Supabase SQL Editor or a privileged test connection. Do not run it using the public API key or a normal end-user session. The test is designed to roll back all fixture rows.

GitHub Actions also supports this check when the repository secret `DUO_RLS_TEST_DATABASE_URL` is configured with a trusted connection to a dedicated staging database. The workflow skips the integration step when the secret is absent; never use a browser-facing or service-role API key as a database URL.

## Live verification (2026-11-21)

- All 11 tables in `public` have RLS enabled.
- Public catalog read access remains available to `anon` and `authenticated`.
- No `anon` access remains on couple data or event-ingestion control tables.
- `authenticated` no longer has `TRUNCATE`, `REFERENCES`, or `TRIGGER` privileges. Match access is restricted to SELECT on session metadata; candidates and votes have no direct authenticated grants.
- The live `duo_match_backend` role is non-login, inherits `authenticated`, and does not bypass RLS. The `duo_api` runtime login can assume it for Match endpoints.
- The transaction-scoped multi-user isolation script completed successfully against the live database and rolled back all five synthetic users and all three fixture couples. It also checks that public city metadata is readable and private activity is keyed by place slug.
- Supabase Security Advisor no longer reports exposed authenticated `SECURITY DEFINER` functions: all three couple functions are in the non-exposed `private` schema, use an empty `search_path`, and are executable only by `authenticated`/`service_role`.
- Leaked-password protection remains a dashboard-level Auth setting and still needs to be enabled by an authorized project administrator.

## Match lifecycle integration coverage (2026-11-27)

- The transaction-scoped RLS suite now models two distinct members in the same couple voting on the same candidate. It verifies each member can update their own vote, the backend role can calculate the mutual result only after both likes exist, and a member cannot modify the partner's vote.
- This is database-level integration coverage; it does not replace a browser-level registration/invitation flow or prove that the hosted Auth UI works end to end.

## Latest live privilege check (2026-11-27)

- All 16 current tables in the exposed `public` schema have RLS enabled.
- Public read access is limited to the intended catalog tables: `cities`, `places`, `duo_events`, and `duo_place_updates`.
- Couple and personal activity tables are not readable by `anon`; authenticated reads remain subject to their existing RLS policies.
- Event-ingestion control tables (`duo_event_sources`, `duo_event_sync_config`, `duo_event_sync_runs`) have no SELECT grants for either `anon` or `authenticated`. Their RLS-enabled/no-policy advisor notices are intentional: access is reserved for the trusted ingestion runtime.
- Match candidates and votes have no direct SELECT grants for browser roles; Match sessions are visible only to authenticated users under couple-scoped RLS.
- The photo-attribution migration adds nullable content metadata to `places`; it does not change grants or RLS policies.
- Supabase Security Advisor still reports leaked-password protection as disabled. This is an Auth dashboard setting and remains an administrator action; it is not silently changed by a database migration.

## City expansion

The city directory currently exposes only Minsk. Places, events, updates, event sources, and sync-run records now carry a `city_slug`; event ingestion resolves each source against active city metadata (localized name, country, time zone and currency). A new city must not be activated until its venue catalog and event sources are verified.

## Operational note

Supabase's `supabase_admin` default privileges are managed by the platform and could not be changed by the project SQL role. The migration restricts default privileges for objects created by `postgres`, the role used for the committed project migrations. If a future workflow creates public objects as `supabase_admin`, explicitly set grants and RLS in that migration.
