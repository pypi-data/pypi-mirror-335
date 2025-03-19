"""Module provides functions to initialize and manage the DuckDB."""

from contextlib import contextmanager
from typing import Generator

from sqlmodel import Session, SQLModel, create_engine

import lightly_purple.server.models  # noqa: F401, required for SQLModel to work properly


class DatabaseManager:
    """Manages database connections and ensures proper resource handling."""

    _instance = None

    def __new__(cls, db_file: str = "purple.db"):
        """Create a new instance of the DatabaseManager."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            # File-based DuckDB
            cls._instance.engine = create_engine(f"duckdb:///{db_file}")
            # Initialize tables
            SQLModel.metadata.create_all(cls._instance.engine)
        return cls._instance

    @contextmanager
    def session(self) -> Generator[Session, None, None]:
        """Create a new database session."""
        session = Session(self.engine)
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


# Global instance
db_manager = DatabaseManager()


# For FastAPI dependency injection
def get_session():
    """Yield a new session for database operations."""
    with db_manager.session() as session:
        yield session
