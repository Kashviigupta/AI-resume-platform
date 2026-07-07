from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import settings

# check_same_thread=False is required for SQLite when used with FastAPI,
# since FastAPI can handle a request in a different thread than the one
# that created the connection.
connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    FastAPI dependency — yields a DB session per-request and always closes it,
    even if the request raises an exception.
    Usage in a route: def my_route(db: Session = Depends(get_db)):
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Creates all tables from models that have been imported (imported models
    register themselves on Base.metadata). Called once on app startup.
    Milestone 4 will populate app/models/ with the real tables.
    """
    Base.metadata.create_all(bind=engine)
