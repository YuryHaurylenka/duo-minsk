from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from app.config import get_settings


class Base(DeclarativeBase):
    pass


settings = get_settings()
# Supavisor transaction mode does not support prepared statements.
# Psycopg uses None to disable preparation; 0 would prepare every statement immediately.
DATABASE_CONNECT_ARGS = {
    "sslmode": "require",
    "prepare_threshold": None,
    "connect_timeout": 10,
}
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_recycle=60,
    pool_size=1,
    max_overflow=0,
    pool_timeout=8,
    connect_args=DATABASE_CONNECT_ARGS,
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db():
    db = SessionLocal()
    try:
        # The connection login is private. Public endpoints run as anon;
        # authenticated endpoints switch to authenticated after JWT verification.
        db.execute(text("SET LOCAL ROLE anon"))
        yield db
    finally:
        db.close()
