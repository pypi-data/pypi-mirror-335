from .base import Base

def init_db(engine):
    """Creates the database tables."""
    Base.metadata.create_all(engine)