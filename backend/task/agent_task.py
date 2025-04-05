"""에이전트 관련 Celery 태스크"""

import logging
from typing import Dict, Optional

from langchain_core.tracers.langchain import wait_for_all_tracers
from sqlalchemy import select

from app.agent.react_agent import create_agent
from app.model.user import User
from core.celery_app import celery_app
from core.db import DatabaseTask

logger = logging.getLogger(__name__)


class HealthQueryTask(DatabaseTask):
    """건강 데이터 AI 분석 태스크"""

    name = "analysis-health"
    expires = 86400

    def run(
        self,
        kakao_client_id: str,
        query: str,
        user_timezone: Optional[str] = None,
    ) -> str:
        """건강 데이터 AI 분석"""
        try:
            user = self._get_user(kakao_client_id)
            agent = create_agent()
            result = agent.run(
                query=query, user_id=user.id, user_timezone=user_timezone
            )

            return result["final_report"]
        except Exception as e:
            raise Exception(f"에러가 발생했습니다: {str(e)}")
        finally:
            wait_for_all_tracers()

    def _get_user(self, kakao_client_id: str) -> User:
        """사용자 정보 조회"""
        result = self.session.execute(
            select(User).where(User.kakao_client_id == kakao_client_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            logger.warning(
                f"카카오톡 유저 ID {kakao_client_id}에 해당하는 사용자를 찾을 수 없음"
            )
            error_response = f"{kakao_client_id}를 찾을 수 없습니다."
            raise Exception(error_response)

        return user


analysis_health_query = celery_app.register_task(HealthQueryTask())
