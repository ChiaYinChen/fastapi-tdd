"""Database session management and configuration.

This module initializes the database connection, metadata, SQLAlchemy engine,
and a base Ormar configuration object using settings from the application's
configuration. These global instances are used throughout the application
for database interactions.

Attributes:
    database (databases.Database): An asynchronous database connection instance.
        Configured for rollback in testing mode.
    metadata (sqlalchemy.MetaData): SQLAlchemy MetaData instance for schema definition.
    engine (sqlalchemy.Engine): SQLAlchemy Engine instance for database connectivity.
    base_ormar_config (ormar.OrmarConfig): Base Ormar configuration object,
        linking the database, metadata, and engine for Ormar models.
"""
import ormar
from databases import Database
from sqlalchemy import MetaData, create_engine

from ..core.config import settings

database = Database(settings.POSTGRES_URI, force_rollback=settings.TESTING)
metadata = MetaData()
engine = create_engine(settings.POSTGRES_URI)
base_ormar_config = ormar.OrmarConfig(database=database, metadata=metadata, engine=engine)
