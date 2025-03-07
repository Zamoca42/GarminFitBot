import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from core.config import (
    DATABASE_URL,
    MAX_OVERFLOW,
    POOL_RECYCLE,
    POOL_SIZE,
    POOL_TIMEOUT,
)
from core.db import Base

logger = logging.getLogger(__name__)

# 엔진 설정
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    pool_size=POOL_SIZE,
    max_overflow=MAX_OVERFLOW,
    pool_timeout=POOL_TIMEOUT,
    pool_recycle=POOL_RECYCLE,
    pool_pre_ping=True,
)

# 세션 팩토리
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


# FastAPI 의존성 주입용
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """현재 요청의 세션을 제공"""
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


# 트랜잭션 관리를 위한 컨텍스트 매니저
@asynccontextmanager
async def transaction(session: AsyncSession):
    """트랜잭션 관리를 위한 컨텍스트 매니저"""
    if not session.in_transaction():
        async with session.begin():
            logger.debug("트랜잭션 시작")
            yield
        logger.debug("트랜잭션 커밋")
    else:
        logger.debug("이미 트랜잭션 중")
        yield


# 데이터베이스 초기화 함수
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
