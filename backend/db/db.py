import asyncio

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    create_async_engine, 
    AsyncSession, 
    async_sessionmaker, 
    async_scoped_session
    )
from sqlalchemy import text
from db.model import Base
from config import (
    DATABASE_URL,
    POOL_SIZE,
    MAX_OVERFLOW,
    POOL_TIMEOUT,
    POOL_RECYCLE,
    DB_USER,
    DB_PASSWORD,
    DB_HOST,
    DB_PORT,
    DB_NAME
)

# 엔진 설정
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # SQL 로깅
    pool_size=POOL_SIZE,
    max_overflow=MAX_OVERFLOW,
    pool_timeout=POOL_TIMEOUT,
    pool_recycle=POOL_RECYCLE,
    pool_pre_ping=True  # 연결 상태 확인
)

# 세션 팩토리
session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)
async_session = async_scoped_session(session_factory, scopefunc=asyncio.current_task)

# 의존성 주입용 세션 제공자
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

# 데이터베이스 초기화 함수
async def init_db():
    # 기본 데이터베이스(postgres)로 연결하는 엔진 생성
    default_engine = create_async_engine(
        f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/postgres",
        isolation_level="AUTOCOMMIT"
    )

    try:
        # 데이터베이스 존재 여부 확인 및 생성
        async with default_engine.connect() as conn:
            # 데이터베이스 존재 여부 확인
            result = await conn.execute(
                text(f"SELECT 1 FROM pg_database WHERE datname = '{DB_NAME}'")
            )
            if not result.scalar():
                # 데이터베이스 생성
                await conn.execute(text(f"CREATE DATABASE {DB_NAME}"))
    finally:
        await default_engine.dispose()

    # 테이블 생성
    async with engine.begin() as conn:
        # 모든 모델의 테이블 생성
        await conn.run_sync(Base.metadata.create_all)