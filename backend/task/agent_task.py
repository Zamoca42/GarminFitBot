"""에이전트 관련 Celery 태스크"""

import logging
from datetime import date
from typing import Dict, Optional

from sqlalchemy import select

from app.agent.react_agent import create_agent
from app.model.user import User
from core.db import DatabaseTask
from task import celery_app

logger = logging.getLogger(__name__)


class HealthQueryTask(DatabaseTask):
    """건강 데이터 AI 분석 태스크"""

    name = "analysis_health_query"

    def run(
        self,
        kakao_client_id: str,
        query: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> Dict:
        """건강 데이터 AI 분석"""
        try:
            user = self._get_user(kakao_client_id)
            agent = create_agent(session=self.session)

            return agent.run(
                query=query, user_id=user.id, start_date=start_date, end_date=end_date
            )
        except Exception as e:
            raise Exception(f"에러가 발생했습니다: {str(e)}")

    def _get_user(self, kakao_user_id: str) -> User:
        """사용자 정보 조회"""
        result = self.session.execute(
            select(User).where(User.kakao_client_id == kakao_user_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            logger.warning(
                f"카카오톡 유저 ID {kakao_user_id}에 해당하는 사용자를 찾을 수 없음"
            )
            error_response = f"{kakao_user_id}를 찾을 수 없습니다."
            raise Exception(error_response)

        return user


analysis_health_query = celery_app.register_task(HealthQueryTask())
