import os
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
import redis.asyncio as redis
from contextlib import asynccontextmanager

# Database URLs from environment
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://admin:smartcity123@localhost:27017")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://smart_city:smartcity123@localhost:5432/smart_city_db")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# MongoDB client
mongodb_client: Optional[AsyncIOMotorClient] = None
mongodb = None

# PostgreSQL
engine = None
async_session = None
Base = declarative_base()

# Redis client
redis_client: Optional[redis.Redis] = None

async def init_databases():
    """Initialize all database connections"""
    global mongodb_client, mongodb, engine, async_session, redis_client
    
    # MongoDB
    mongodb_client = AsyncIOMotorClient(MONGODB_URL)
    mongodb = mongodb_client.smart_city
    
    # PostgreSQL
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Redis
    redis_client = await redis.from_url(REDIS_URL, decode_responses=True)
    
    print("All databases connected successfully")

async def close_databases():
    """Close all database connections"""
    global mongodb_client, redis_client
    
    if mongodb_client:
        mongodb_client.close()
    
    if redis_client:
        await redis_client.close()
    
    if engine:
        await engine.dispose()

# Dependency to get MongoDB database
async def get_mongodb():
    return mongodb

# Dependency to get PostgreSQL session
async def get_db():
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()

# Dependency to get Redis client
async def get_redis():
    return redis_client

# Context manager for MongoDB operations
@asynccontextmanager
async def mongodb_context():
    yield mongodb

# Context manager for PostgreSQL operations
@asynccontextmanager
async def postgres_context():
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# Context manager for Redis operations
@asynccontextmanager
async def redis_context():
    yield redis_client
