import logging
import traceback
from datetime import datetime, timezone
from typing import Optional

import pytz
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.model import User
from app.service import GarminDataCollectorService, TokenService
from core.db import DatabaseTask

logger = logging.getLogger(__name__)


def get_user_by_kakao_id(session: Session, kakao_client_id: str) -> User:
    """카카오 클라이언트 ID로 사용자 조회"""
    result = session.execute(
        select(User).where(User.kakao_client_id == kakao_client_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        logger.warning(
            f"카카오톡 유저 ID {kakao_client_id}에 해당하는 사용자를 찾을 수 없음"
        )
        raise ValueError(f"{kakao_client_id}를 찾을 수 없습니다.")
    return user


def create_garmin_client_from_user(user: User, token_service: TokenService):
    """사용자 정보로 Garmin 클라이언트 생성"""
    oauth1_token = {
        "oauth_token": user.oauth_token,
        "oauth_token_secret": user.oauth_token_secret,
        "domain": user.domain,
    }
    return token_service.create_garmin_client(oauth1_token)


def get_garmin_last_sync_time(garmin_client) -> datetime:
    """Garmin 마지막 동기화 시간 조회 (UTC)"""
    get_last_sync_time_str = garmin_client.connectapi(
        "/wellness-service/wellness/syncTimestamp"
    )
    try:
        last_sync_time_utc = datetime.strptime(
            get_last_sync_time_str, "%Y-%m-%dT%H:%M:%S.%f"
        )
    except ValueError:
        try:
            last_sync_time_utc = datetime.strptime(
                get_last_sync_time_str, "%Y-%m-%dT%H:%M:%S"
            )
        except ValueError:
            logger.error(f"알 수 없는 동기화 시간 형식: {get_last_sync_time_str}")
            raise ValueError("동기화 시간 형식을 파싱할 수 없습니다.")

    return last_sync_time_utc.replace(tzinfo=timezone.utc)


def get_pytz_timezone(user_timezone_str: str) -> pytz.timezone:
    """문자열로부터 pytz 시간대 객체 가져오기"""
    try:
        return pytz.timezone(user_timezone_str)
    except pytz.exceptions.UnknownTimeZoneError:
        logger.error(f"알 수 없는 시간대입니다: {user_timezone_str}")
        raise ValueError(f"알 수 없는 시간대: {user_timezone_str}")


def parse_date_string(date_str: str, tz: pytz.timezone) -> datetime:
    """날짜 문자열(YYYY-MM-DD)을 해당 시간대의 datetime 객체로 변환"""
    try:
        naive_datetime = datetime.strptime(date_str, "%Y-%m-%d")
        return tz.localize(naive_datetime)
    except ValueError:
        logger.error(f"잘못된 날짜 형식: {date_str}")
        raise ValueError(f"잘못된 날짜 형식: {date_str}")


def validate_garmin_sync_time(
    garmin_client, target_date_str: str, user_timezone_str: str
) -> None:
    """Garmin 동기화 시간 검증"""
    last_sync_time_utc = get_garmin_last_sync_time(garmin_client)
    user_tz = get_pytz_timezone(user_timezone_str)
    target_datetime_local = parse_date_string(target_date_str, user_tz)
    last_sync_time_local = last_sync_time_utc.astimezone(user_tz)

    if last_sync_time_local.date() < target_datetime_local.date():
        error_msg = (
            f"마지막 동기화 시간({last_sync_time_local.strftime('%Y-%m-%d %H:%M')})이 "
            f"요청된 날짜({target_datetime_local.strftime('%Y-%m-%d')})보다 이전입니다. "
            f"가민 앱 또는 기기를 먼저 동기화해주세요."
        )
        logger.warning(error_msg)
        raise ValueError(error_msg)


def collect_garmin_daily_data(
    session: Session, garmin_client, user_id: int, target_date_str: str
) -> Optional[dict]:
    """Garmin 일일 데이터 수집 실행"""
    collector_service = GarminDataCollectorService(
        client=garmin_client, session=session
    )
    try:
        target_date = datetime.strptime(target_date_str, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError(f"잘못된 날짜 형식: {target_date_str}")

    result = collector_service.collect_daily_data(user_id, target_date)
    return result


def handle_task_failure(
    task: DatabaseTask,
    error: Exception,
    log_message_prefix: str = "태스크 실행 중 오류 발생",
) -> None:
    """Celery 태스크 실패 시 상태 업데이트 및 로깅"""
    logger.error(f"{log_message_prefix}: {str(error)}", exc_info=True)
    try:
        task.update_state(
            state="FAILURE",
            meta={
                "exc_type": type(error).__name__,
                "exc_message": str(error),
                "traceback": traceback.format_exc(),
            },
        )
    except Exception as update_err:
        logger.error(f"태스크 상태 업데이트 실패: {update_err}", exc_info=True)
