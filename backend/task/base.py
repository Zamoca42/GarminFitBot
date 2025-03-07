from functools import wraps

from core.db.session import async_session_factory


def with_db_context(func):
    """Celery task용 DB 컨텍스트 데코레이터"""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        async with async_session_factory() as session:
            try:
                return await func(session, *args, **kwargs)
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    return wrapper
