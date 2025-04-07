import logging
import traceback
from datetime import datetime, timezone
from typing import Optional

import pytz
from celery import states
from sqlalchemy import select

from app.model import User
from app.service import GarminDataCollectorService, TokenService
from core.celery_app import celery_app
from core.db import DatabaseTask

logger = logging.getLogger(__name__)


class GarminDataCollectionTask(DatabaseTask):
    """Garmin 데이터 수집 태스크"""

    name = "collect-fit-data"
    expires = 86400

    def run(self, kakao_client_id: str, target_date: str, user_timezone: str):
        """메인 실행 메서드"""
        logger.info(f"사용자 {kakao_client_id}의 Garmin 데이터 수집 시작")

        try:
            user = self._get_user(kakao_client_id)
            garmin_client = self._create_garmin_client(user)
            self._validate_sync_time(garmin_client, target_date, user_timezone)
            result = self._collect_data(garmin_client, user.id, target_date)
            return result
        except Exception as e:
            self._handle_error(e, kakao_client_id)
            raise

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
            raise Exception("데이터를 수집할 수 없습니다.")

        return user

    def _create_garmin_client(self, user: User):
        """Garmin 클라이언트 생성"""
        token_service = TokenService()
        oauth1_token = {
            "oauth_token": user.oauth_token,
            "oauth_token_secret": user.oauth_token_secret,
            "domain": user.domain,
        }
        return token_service.create_garmin_client(oauth1_token)

    def _validate_sync_time(
        self, garmin_client, target_date: str, user_timezone: str
    ) -> None:
        """동기화 시간 검증"""
        last_sync_time_utc = self._get_last_sync_time(garmin_client)
        user_tz = self._get_user_timezone(user_timezone)
        target_datetime_local = self._parse_target_date(target_date, user_tz)
        last_sync_time_local = last_sync_time_utc.astimezone(user_tz)

        if last_sync_time_local.date() < target_datetime_local.date():
            self._handle_sync_time_error(last_sync_time_local, target_datetime_local)

    def _get_last_sync_time(self, garmin_client) -> datetime:
        """마지막 동기화 시간 조회"""
        get_last_sync_time = garmin_client.connectapi(
            "/wellness-service/wellness/syncTimestamp"
        )
        last_sync_time_utc = datetime.strptime(
            get_last_sync_time, "%Y-%m-%dT%H:%M:%S.%f"
        )
        return last_sync_time_utc.replace(tzinfo=timezone.utc)

    def _get_user_timezone(self, user_timezone: str) -> pytz.timezone:
        """사용자 시간대 조회"""
        try:
            return pytz.timezone(user_timezone)
        except pytz.exceptions.UnknownTimeZoneError:
            error_response = f"알 수 없는 시간대입니다: {user_timezone}"
            logger.error(error_response)
            raise Exception(error_response)

    def _parse_target_date(self, target_date: str, user_tz: pytz.timezone) -> datetime:
        """목표 날짜 파싱"""
        target_datetime_local = datetime.strptime(target_date, "%Y-%m-%d")
        return user_tz.localize(target_datetime_local)

    def _handle_sync_time_error(
        self, last_sync_time_local: datetime, target_datetime_local: datetime
    ) -> None:
        """동기화 시간 오류 처리"""
        error_response = f"마지막 동기화 시간(로컬: {last_sync_time_local})이 요청된 날짜({target_datetime_local.date()})보다 이전입니다."
        logger.warning(error_response)
        raise Exception(error_response)

    def _collect_data(
        self, garmin_client, user_id: int, target_date: str
    ) -> Optional[dict]:
        """데이터 수집"""
        collector_service = GarminDataCollectorService(
            client=garmin_client, session=self.session
        )

        target_date = datetime.strptime(target_date, "%Y-%m-%d").date()

        try:
            result = collector_service.collect_daily_data(user_id, target_date)

            if not result:
                raise Exception("데이터를 수집할 수 없습니다.")

            return result

        except Exception as e:
            logger.error(f"데이터 수집 중 오류 발생: {str(e)}")
            self.update_state(
                state=states.FAILURE,
                meta={
                    "exc_type": type(e).__name__,
                    "exc_message": str(e),
                    "traceback": traceback.format_exc(),
                },
            )
            raise e

    def _handle_error(self, error: Exception, kakao_client_id: str) -> None:
        """오류 처리"""
        logger.error(
            f"사용자 {kakao_client_id}의 데이터 수집 중 오류 발생: {str(error)}"
        )
        self.update_state(
            state=states.FAILURE,
            meta={
                "exc_type": type(error).__name__,
                "exc_message": str(error),
                "traceback": traceback.format_exc(),
            },
        )


collect_fit_data = celery_app.register_task(GarminDataCollectionTask())
