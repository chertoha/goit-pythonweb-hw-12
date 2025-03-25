"""
Database session management module.

This module defines the `DatabaseSessionManager` class responsible for managing database connections
and sessions using SQLAlchemy's asynchronous features. It also provides a `get_db` function for dependency injection.

Classes:
    - DatabaseSessionManager: Class that manages database sessions, including context manager for handling sessions.

Functions:
    - get_db: Dependency function that provides an asynchronous database session.
"""

import contextlib

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
)

from src.conf.config import settings

class DatabaseSessionManager:
    """
        Manages asynchronous database sessions using SQLAlchemy.

        Attributes:
            _engine (AsyncEngine | None): The SQLAlchemy engine for connecting to the database.
            _session_maker (async_sessionmaker): The session maker for creating database sessions.

        Methods:
            __init__(self, url: str): Initializes the engine and session maker with the provided database URL.
            session(self): Asynchronous context manager for handling database sessions, including committing or rolling back transactions.
    """
    def __init__(self, url: str):
        """
            Initializes the database engine and session maker with the provided database URL.

            Args:
                url (str): The database connection URL.
        """
        self._engine: AsyncEngine | None = create_async_engine(url)
        self._session_maker: async_sessionmaker = async_sessionmaker(
            autoflush=False, autocommit=False, bind=self._engine
        )

    @contextlib.asynccontextmanager
    async def session(self):
        """
            Asynchronous context manager for handling database sessions.

            This method creates a session, yields it to the caller, and handles transaction management,
            including rollback in case of an error.

            Yields:
                session (AsyncSession): The database session object.

            Raises:
                SQLAlchemyError: If any database error occurs during the transaction.
        """
        if self._session_maker is None:
            raise Exception("Database session is not initialized")
        session = self._session_maker()
        try:
            yield session
        except SQLAlchemyError as e:
            await session.rollback()
            raise  # Re-raise the original error
        finally:
            await session.close()

sessionmanager = DatabaseSessionManager(settings.DB_URL)

async def get_db():
    async with sessionmanager.session() as session:
        yield session
