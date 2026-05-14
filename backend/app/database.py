"""Configuration base de donnees — SQLite (dev) / PostgreSQL (prod)."""
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Render fournit DATABASE_URL automatiquement
# Format : postgresql://user:password@host:port/database
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # Fallback SQLite pour dev local
    DATABASE_URL = "sqlite:///./foodexpress_ci.db"
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    # PostgreSQL pour production (Render)
    engine = create_engine(DATABASE_URL.replace("postgres://", "postgresql://"))

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
