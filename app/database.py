from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings

engine = create_engine(settings.DATABASE_URI)

new_session = sessionmaker(engine)


def get_session():
    with new_session() as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
