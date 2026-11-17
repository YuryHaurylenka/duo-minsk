# DUO database security checks

## Access model

- `duo_api` is the private runtime login (`NOINHERIT`, `NOBYPASSRLS`). It is never shipped to the browser.
- Public catalog roles (`anon`, `authenticated`) have read-only access to `places`, `duo_events`, and `duo_place_updates`.
- Couple tables (`couples`, `couple_members`, `duo_date_plans`, `place_activity`) are available only to `authenticated`, with row access constrained by the couple-membership RLS policies.
- Event-ingestion control tables (`duo_event_sources`, `duo_event_sync_config`, `duo_event_sync_runs`) are not granted to `anon` or `authenticated`; the trusted ingestion runtime uses its privileged server-side credential.
- `TRUNCATE`, `REFERENCES`, and `TRIGGER` are revoked from API roles across the exposed `public` schema.
- The `is_couple_member` SECURITY DEFINER helper lives in the non-exposed `private` schema; only `authenticated` and `service_role` can use it. The two public SECURITY DEFINER RPCs remain intentionally callable only by `authenticated`.
- Default table, function, and sequence grants for objects created by `postgres` in `public` are restricted. New API-facing objects must receive explicit grants and RLS policies.

## Database tests

`supabase/tests/database/rls_isolation.sql` is a transaction-scoped integration test. It creates two synthetic Auth users, two couples, and private activity/plans, switches to the real `authenticated` and `anon` database roles, checks cross-couple isolation and privilege boundaries, then rolls everything back.

Run the entire SQL file using a trusted PostgreSQL connection in Supabase SQL Editor or a privileged test connection. Do not run it using the public API key or a normal end-user session. The test is designed to roll back all fixture rows.

GitHub Actions also supports this check when the repository secret `DUO_RLS_TEST_DATABASE_URL` is configured with a trusted connection to a dedicated staging database. The workflow skips the integration step when the secret is absent; never use a browser-facing or service-role API key as a database URL.

## Live verification (2026-11-17)

- All 10 tables in `public` have RLS enabled.
- Public catalog read access remains available to `anon` and `authenticated`.
- No `anon` access remains on couple data or event-ingestion control tables.
- `authenticated` no longer has `TRUNCATE`, `REFERENCES`, or `TRIGGER` privileges; it retains only the DML required by the API and couple policies.
- The transaction-scoped two-user isolation script completed successfully against the live database and rolled back its fixtures.
- Supabase Security Advisor reports two expected `SECURITY DEFINER` RPCs (`create_couple`, `join_couple`). They are intentionally callable only by `authenticated`; both check `auth.uid()`, use an empty `search_path`, and have no `anon`/`PUBLIC` execute grant. The RLS helper was moved to the non-exposed `private` schema, removing it from the public RPC surface.
- Leaked-password protection remains a dashboard-level Auth setting and still needs to be enabled by an authorized project administrator.

## Operational note

Supabase's `supabase_admin` default privileges are managed by the platform and could not be changed by the project SQL role. The migration restricts default privileges for objects created by `postgres`, the role used for the committed project migrations. If a future workflow creates public objects as `supabase_admin`, explicitly set grants and RLS in that migration.
