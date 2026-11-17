from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from app.config import get_settings


class Base(DeclarativeBase):
    pass


settings = get_settings()
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_recycle=60,
    pool_size=1,
    max_overflow=0,
    pool_timeout=8,
    connect_args={"sslmode": "require", "prepare_threshold": 0, "connect_timeout": 10},
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
