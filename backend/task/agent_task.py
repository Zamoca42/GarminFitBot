import logging
from typing import Optional

from langchain_core.tracers.langchain import wait_for_all_tracers

from app.agent.react_agent import create_agent
from core.celery_app import celery_app
from core.db.celery_session import DatabaseTask
from task.util import get_user_by_kakao_id, handle_task_failure

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, base=DatabaseTask, name="analysis-health", expires=172800)
def analysis_health_query(
    self: DatabaseTask,
    kakao_client_id: str,
    query: str,
    detail_params: dict,
    user_timezone: Optional[str] = None,
) -> str:
    """건강 데이터 AI 분석 태스크"""
    log_prefix = (
        f"사용자 {kakao_client_id}의 건강 데이터 분석 (Task ID: {self.request.id})"
    )
    logger.info(f"{log_prefix} 시작")
    try:
        user = get_user_by_kakao_id(self.session, kakao_client_id)
        agent = create_agent()
        result = agent.run(
            query=query,
            user_id=user.id,
            user_timezone=user_timezone,
            detail_params=detail_params,
        )
        final_report = result.get("final_report", "분석 보고서를 생성하지 못했습니다.")
        logger.info(f"{log_prefix} 완료")
        return final_report
    except ValueError as ve:
        handle_task_failure(self, ve, log_prefix)
        raise Exception(str(ve))
    except Exception as e:
        handle_task_failure(self, e, log_prefix)
        raise Exception(f"에러가 발생했습니다: {str(e)}")
    finally:
        wait_for_all_tracers()
