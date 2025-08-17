import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.orm import declarative_base

# super class for all ORM models
Base = declarative_base()

# Reading configuration from env 
DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", os.getenv("DB_NAME", "app"))
DB_USER = os.getenv("POSTGRES_USER", os.getenv("DB_USER", "app_user"))
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", os.getenv("DB_PASSWORD", "app_pw"))

# Optional parameters for the pool
POOL_SIZE = int(os.getenv("DB_POOL_SIZE", 5))            
MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", 10))     
POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", 30))     
POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", 1800))

# to log or not SQL-queries
ECHO = os.getenv("SQL_ECHO", "0") == "1"

DATABASE_URL = (
    f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_async_engine(
    DATABASE_URL,
    echo=ECHO,
    pool_size=POOL_SIZE,
    max_overflow=MAX_OVERFLOW,
    pool_timeout=POOL_TIMEOUT,
    pool_recycle=POOL_RECYCLE
)

# Session factory
SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autoflush=False,
    expire_on_commit=False,
)

# Dependency для FastAPI: getting session from the pool
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session
