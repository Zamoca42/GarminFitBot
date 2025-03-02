from contextvars import ContextVar, Token
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
)

from core.config import (
    DATABASE_URL,
    MAX_OVERFLOW,
    POOL_RECYCLE,
    POOL_SIZE,
    POOL_TIMEOUT,
)
from core.db import Base

# 세션 컨텍스트 관리
session_context: ContextVar[str] = ContextVar("session_context")

def get_session_id() -> str:
    return session_context.get()

def set_session_context(session_id: str) -> Token:
    return session_context.set(session_id)

def reset_session_context(context: Token) -> None:
    session_context.reset(context)

# 엔진 설정
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # SQL 로깅
    pool_size=POOL_SIZE,
    max_overflow=MAX_OVERFLOW,
    pool_timeout=POOL_TIMEOUT,
    pool_recycle=POOL_RECYCLE,
    pool_pre_ping=True,  # 연결 상태 확인
)

# 세션 팩토리
session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# 스코프된 세션
session = async_scoped_session(
    session_factory,
    scopefunc=get_session_id
)

# FastAPI 의존성 주입용
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """현재 요청의 세션을 제공"""
    session_instance = session()
    try:
        yield session_instance
    finally:
        await session_instance.close()

# 데이터베이스 초기화 함수
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
