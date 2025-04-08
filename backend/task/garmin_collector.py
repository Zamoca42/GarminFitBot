import logging
from typing import Optional

from app.service import TokenService
from core.celery_app import celery_app
from core.db.celery_session import DatabaseTask
from task.util import (
    collect_garmin_daily_data,
    create_garmin_client_from_user,
    get_user_by_kakao_id,
    handle_task_failure,
    validate_garmin_sync_time,
)

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, base=DatabaseTask, name="collect-fit-data", expires=21600)
def collect_fit_data(
    self: DatabaseTask, kakao_client_id: str, target_date: str, user_timezone: str
) -> Optional[dict]:
    """Garmin 데이터 수집 태스크 (데코레이터 기반)"""
    log_prefix = f"사용자 {kakao_client_id}의 {target_date} Garmin 데이터 수집 (Task ID: {self.request.id})"
    logger.info(f"{log_prefix} 시작")

    token_service = TokenService()

    try:
        user = get_user_by_kakao_id(self.session, kakao_client_id)
        garmin_client = create_garmin_client_from_user(user, token_service)
        validate_garmin_sync_time(garmin_client, target_date, user_timezone)
        result = collect_garmin_daily_data(
            self.session, garmin_client, user.id, target_date
        )
        logger.info(f"{log_prefix} 완료")
        return result
    except ValueError as ve:
        handle_task_failure(self, ve, log_prefix)
        raise Exception(str(ve))
    except Exception as e:
        handle_task_failure(self, e, log_prefix)
        raise
