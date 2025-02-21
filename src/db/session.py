import ormar
from databases import Database
from sqlalchemy import MetaData, create_engine

from ..core.config import settings

database = Database(settings.POSTGRES_URI, force_rollback=settings.TESTING)
metadata = MetaData()
engine = create_engine(settings.POSTGRES_URI)
base_ormar_config = ormar.OrmarConfig(database=database, metadata=metadata, engine=engine)
