import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@control_db:5432/postgres")


def get_engine(database_url: str = None):
    url = database_url or DATABASE_URL
    return create_async_engine(url, future=True)


Base = declarative_base()


def get_sessionmaker(engine=None):
    eng = engine or get_engine()
    return sessionmaker(eng, class_=AsyncSession, expire_on_commit=False)


async def init_db(engine=None):
    eng = engine or get_engine()
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

