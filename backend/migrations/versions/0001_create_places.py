"""Create normalized DUO places catalog."""
from alembic import op

revision = "0001_create_places"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
    CREATE TABLE IF NOT EXISTS public.places (
      id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
      slug varchar(180) NOT NULL UNIQUE,
      name varchar(255) NOT NULL,
      category varchar(120) NOT NULL,
      emoji varchar(16) NOT NULL DEFAULT '✨',
      description text NOT NULL DEFAULT '',
      address text NOT NULL DEFAULT '',
      rating varchar(32) NOT NULL DEFAULT '—',
      reviews varchar(32) NOT NULL DEFAULT '—',
      price_label text NOT NULL DEFAULT '',
      couple_price_label text NOT NULL DEFAULT '',
      level smallint NOT NULL DEFAULT 1 CHECK (level BETWEEN 1 AND 5),
      risk varchar(24) NOT NULL DEFAULT 'good' CHECK (risk IN ('good','caution','avoid')),
      tip text NOT NULL DEFAULT '',
      website_url text NOT NULL DEFAULT '',
      source_name varchar(120) NOT NULL DEFAULT '',
      source_url text NOT NULL DEFAULT '',
      cost numeric(10,2),
      is_active boolean NOT NULL DEFAULT true,
      created_at timestamptz NOT NULL DEFAULT now(),
      updated_at timestamptz NOT NULL DEFAULT now()
    )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS places_name_idx ON public.places(name)")
    op.execute("CREATE INDEX IF NOT EXISTS places_category_idx ON public.places(category)")
    op.execute("ALTER TABLE public.places ENABLE ROW LEVEL SECURITY")
    op.execute("""
    DO $$ BEGIN
      IF NOT EXISTS (
        SELECT 1 FROM pg_policies
        WHERE schemaname='public' AND tablename='places' AND policyname='places_public_read'
      ) THEN
        CREATE POLICY places_public_read ON public.places
        FOR SELECT TO anon, authenticated USING (is_active IS TRUE);
      END IF;
    END $$
    """)
    op.execute("GRANT SELECT ON public.places TO anon, authenticated")


def downgrade():
    op.execute("DROP TABLE IF EXISTS public.places")
