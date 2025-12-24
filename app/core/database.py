from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

engine = create_engine(settings.DATABASE_URI, echo=True)

new_session = sessionmaker(engine)


def get_session():
    with new_session() as session:
        yield session
