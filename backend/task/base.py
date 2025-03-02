from functools import wraps
from uuid import uuid4

from core.db.session import set_session_context, reset_session_context, session

def with_db_context(func):
    """Celery task용 DB 컨텍스트 데코레이터"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        session_id = str(uuid4())
        context = set_session_context(session_id)
        
        try:
            return await func(*args, **kwargs)
        finally:
            await session.remove()
            reset_session_context(context)
            
    return wrapper 