import logging
from datetime import date

from app.model import (
    HeartRateDaily,
    HeartRateReading,
)
from app.service import BaseGarminService

logger = logging.getLogger(__name__)


class GarminDataCollectorService(BaseGarminService):
    """
    Garmin 데이터 수집 서비스
    - 일일 데이터 수집 및 DB 저장
    - 분석용 데이터 적재
    - 배치 작업으로 실행
    """

    async def collect_daily_data(self, user_id: int, target_date: date):
        """특정 날짜의 모든 데이터 수집"""
        logger.info("데이터 수집 시작 - User: %d, Date: %s", user_id, target_date)

        try:
            # 1. 심박수 데이터 수집
            heart_rate_data = await self._collect_heart_rate(user_id, target_date)

            # 2. 스트레스 데이터 수집
            stress_data = await self._collect_stress(user_id, target_date)

            # 3. 걸음수 데이터 수집
            steps_data = await self._collect_steps(user_id, target_date)

            # 4. 수면 데이터 수집
            sleep_data = await self._collect_sleep(user_id, target_date)

            # 5. 활동 데이터 수집
            activity_data = await self._collect_activities(user_id, target_date)

            return {
                "heart_rate": heart_rate_data,
                "stress": stress_data,
                "steps": steps_data,
                "sleep": sleep_data,
                "activities": activity_data,
            }

        except Exception as e:
            logger.error(
                "데이터 수집 실패 - User: %d, Date: %s, Error: %s",
                user_id,
                target_date,
                str(e),
            )
            raise

    async def _collect_heart_rate(self, user_id: int, target_date: date):
        """심박수 데이터 수집 및 저장"""
        # 1. Garmin API 조회
        data = await self.time_series_service.get_heart_rates(target_date)
        if not data:
            return None

        # 2. 일일 요약 저장
        daily_summary = HeartRateDaily(
            user_id=user_id,
            date=target_date,
            resting_hr=data.resting_heart_rate,
            max_hr=data.max_heart_rate,
            min_hr=data.min_heart_rate,
            avg_hr=data.avg_heart_rate,
            avg_hrv=data.avg_hrv,
        )
        await daily_summary.save()

        # 3. 상세 측정값 저장
        readings = []
        for reading in data.heart_rate_values:
            readings.append(
                HeartRateReading(
                    user_id=user_id,
                    timestamp=reading.time,
                    heart_rate=reading.heart_rate,
                    hrv=reading.hrv,
                )
            )
        await HeartRateReading.bulk_create(readings)

        return daily_summary

    # 비슷한 패턴으로 다른 데이터 수집 메서드들 구현
    async def _collect_stress(self, user_id: int, target_date: date):
        """스트레스 데이터 수집"""
        pass

    async def _collect_steps(self, user_id: int, target_date: date):
        """걸음수 데이터 수집"""
        pass

    async def _collect_sleep(self, user_id: int, target_date: date):
        """수면 데이터 수집"""
        pass

    async def _collect_activities(self, user_id: int, target_date: date):
        """활동 데이터 수집"""
        pass
