from typing import Type

from langchain_core.tools import StructuredTool
from pydantic import BaseModel
from sqlalchemy.orm import Session

from core.db import SessionFactory


class BaseDBTool(StructuredTool):
    """기본 DB 도구"""

    name: str
    description: str
    args_schema: Type[BaseModel]

    def __init__(self):
        super().__init__()

    def _run(self, *args, **kwargs):
        """도구 실행 시 새로운 세션 사용"""
        session = SessionFactory()
        try:
            result = self._execute(session, *args, **kwargs)
            session.commit()
            return result
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def _execute(self, session: Session, *args, **kwargs):
        """실제 도구 실행 로직 (하위 클래스에서 구현)"""
        raise NotImplementedError("하위 클래스에서 구현해야 합니다")
