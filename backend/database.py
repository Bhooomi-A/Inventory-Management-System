"""
database.py — Sets up SQLite database connection using SQLAlchemy.
SQLAlchemy is an ORM (Object Relational Mapper) — it lets us work
with database tables as Python classes instead of writing raw SQL.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLite file-based database — creates inventory.db in the same folder
DATABASE_URL = "sqlite:///./inventory.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # Required for SQLite with FastAPI
)

# Each request gets its own database session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# All models will inherit from this Base class
Base = declarative_base()


def get_db():
    """
    Dependency function — FastAPI calls this to get a DB session per request.
    The 'finally' block ensures the session is always closed after the request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
