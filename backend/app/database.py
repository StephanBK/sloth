"""
Database connection and session management.

LEARNING NOTE:
This file sets up the SQLAlchemy "engine" and "session" which are core concepts:
- Engine: The connection to your database (like a phone line)
- Session: A conversation with the database (like a phone call)
- Base: The parent class all your models inherit from

TUTORIALS:
- SQLAlchemy ORM: https://docs.sqlalchemy.org/en/20/tutorial/
- FastAPI + SQLAlchemy: https://fastapi.tiangolo.com/tutorial/sql-databases/
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config import get_settings

settings = get_settings()

# Create the database engine
# LEARNING NOTE:
# - echo=True prints all SQL queries to console (helpful for learning!)
# - pool_pre_ping=True checks if connection is alive before using it
engine = create_engine(
    settings.database_url,
    echo=settings.debug,  # Print SQL queries when in debug mode
    pool_pre_ping=True,
)

# Create a session factory
# LEARNING NOTE:
# - autocommit=False means you control when changes are saved
# - autoflush=False means SQLAlchemy won't auto-sync with DB
# - This gives you explicit control (safer for learning)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# Base class for all models
# LEARNING NOTE:
# All your database models (User, MealPlan, etc.) will inherit from this.
# SQLAlchemy uses this to track all your tables.
class Base(DeclarativeBase):
    pass


def get_db():
    """
    Dependency that provides a database session.

    LEARNING NOTE:
    This is a "dependency" in FastAPI terms. It:
    1. Creates a new database session
    2. Yields it to your route handler
    3. Automatically closes it when the request is done

    Usage in routes:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            # use db here
            pass

    TUTORIAL: https://fastapi.tiangolo.com/tutorial/dependencies/
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
