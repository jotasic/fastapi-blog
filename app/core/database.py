from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.config import get_setting

settings = get_setting()

async_engine = create_async_engine(settings.DATABASE_URI)

async_session = async_sessionmaker(async_engine, expire_on_commit=False)


async def get_session():
    async with async_session() as session:
        yield session
