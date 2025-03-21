from functools import wraps

from celery import Task
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from core.config import DEBUG, SYNC_DATABASE_URL

engine = create_engine(SYNC_DATABASE_URL, echo=DEBUG)
SessionFactory = sessionmaker(autoflush=False, autocommit=False, bind=engine)


def with_db_context(func):
    """Celery task용 동기 DB 컨텍스트 데코레이터"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        session = SessionFactory()
        try:
            if len(args) > 0 and hasattr(args[0], "request"):
                return func(args[0], session=session, *args[1:], **kwargs)
            else:
                kwargs.pop("session", None)
                return func(session=session, *args, **kwargs)
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    return wrapper


class DatabaseTask(Task):
    """데이터베이스 세션을 관리하는 Celery Task"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._session = None

    @property
    def session(self) -> Session:
        if self._session is None:
            self._session = SessionFactory()
        return self._session

    def after_return(self, *args, **kwargs):
        """태스크 완료 후 세션 정리"""
        if self._session is not None:
            self._session.close()
            self._session = None

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """태스크 실패 시 롤백"""
        if self._session is not None:
            self._session.rollback()
            self._session.close()
            self._session = None
