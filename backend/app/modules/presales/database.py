"""Database connection — PostgreSQL with SQLite fallback for dev."""
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session
import os

# Default to SQLite for dev, override with DATABASE_URL for production
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///" + os.path.join(os.path.dirname(__file__), "..", "..", "data", "presales.db")
)

IS_SQLITE = DATABASE_URL.startswith("sqlite")

if IS_SQLITE:
    os.makedirs(os.path.dirname(DATABASE_URL.replace("sqlite:///", "")), exist_ok=True)
    engine = create_engine(
        DATABASE_URL, echo=False,
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(
        DATABASE_URL, echo=False,
        pool_size=10, max_overflow=20,
        pool_pre_ping=True, pool_recycle=3600,
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
