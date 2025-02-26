import logging
from typing import List

from garth import DailyHRV, DailySleep, DailySteps, DailyStress, WeeklyStress

from app.service import BaseGarminService

logger = logging.getLogger(__name__)


class GarminStatsService(BaseGarminService):
    """
    통계 데이터 조회 서비스
    예시: 7일 동안 수면 품질 데이터 리스트

    - 여러 시점의 데이터 분석
    - 수학적/통계적 처리
    - 추세나 패턴을 보여줌
    """

    async def get_sleep_quality_stats(
        self, end_date: str = None, days: int = 7
    ) -> List[DailySleep]:
        """
        수면 품질 통계 조회

        params:
            end_date: 조회 종료일
            days: 조회 일수
        returns:
            List[DailySleep]: 수면 품질 통계 데이터 리스트
        """
        endpoint_name = "수면 품질 통계"
        logger.info("%s 조회 - EndDate: %s, Days: %d", endpoint_name, end_date, days)
        try:
            data = DailySleep.list(end=end_date, period=days, client=self.client)
            return self._format_response(data)
        except Exception as e:
            logger.error("%s 조회 실패 - Error: %s", endpoint_name, str(e))
            return self._format_response(None, message="error")

    async def get_daily_stress_stats(
        self, end_date: str = None, days: int = 7
    ) -> List[DailyStress]:
        """
        일간 스트레스 통계

        params:
            end_date: 조회 종료일
            days: 조회 일수
        returns:
            List[DailyStress]: 일간 스트레스 통계 데이터 리스트
        """
        endpoint_name = "일간 스트레스 통계"
        logger.info("%s 조회 - EndDate: %s, Days: %d", endpoint_name, end_date, days)
        try:
            data = DailyStress.list(end=end_date, period=days, client=self.client)
            return self._format_response(data)
        except Exception as e:
            logger.error("%s 조회 실패 - Error: %s", endpoint_name, str(e))
            return self._format_response(None, message="error")

    async def get_weekly_stress_stats(
        self, end_date: str = None, weeks: int = 4
    ) -> List[WeeklyStress]:
        """
        주간 스트레스 통계

        params:
            end_date: 조회 종료일
            weeks: 조회 주수
        returns:
            List[WeeklyStress]: 주간 스트레스 통계 데이터 리스트
        """
        endpoint_name = "주간 스트레스 통계"
        logger.info("%s 조회 - EndDate: %s, Weeks: %d", endpoint_name, end_date, weeks)
        try:
            data = WeeklyStress.list(end=end_date, period=weeks, client=self.client)
            return self._format_response(data)
        except Exception as e:
            logger.error("%s 조회 실패 - Error: %s", endpoint_name, str(e))
            return self._format_response(None, message="error")

    async def get_daily_hrv_stats(
        self, end_date: str = None, days: int = 7
    ) -> List[DailyHRV]:
        """
        일간 수면 중 HRV 통계

        params:
            end_date: 조회 종료일
            days: 조회 일수
        returns:
            List[DailyHRV]: 일간 수면 중 HRV 통계 데이터 리스트
        """
        endpoint_name = "일간 수면 중 HRV 통계"
        logger.info("%s 조회 - EndDate: %s, Days: %d", endpoint_name, end_date, days)
        try:
            data = DailyHRV.list(end=end_date, period=days, client=self.client)
            return self._format_response(data)
        except Exception as e:
            logger.error("%s 조회 실패 - Error: %s", endpoint_name, str(e))
            return self._format_response(None, message="error")

    async def get_daily_steps_stats(
        self, end_date: str = None, days: int = 7
    ) -> List[DailySteps]:
        """
        일간 걸음 수 통계

        params:
            end_date: 조회 종료일
            days: 조회 일수
        returns:
            List[DailySteps]: 일간 걸음 수 통계 데이터 리스트
        """
        endpoint_name = "일간 걸음 수 통계"
        logger.info("%s 조회 - EndDate: %s, Days: %d", endpoint_name, end_date, days)
        try:
            data = DailySteps.list(end=end_date, period=days, client=self.client)
            return self._format_response(data)
        except Exception as e:
            logger.error("%s 조회 실패 - Error: %s", endpoint_name, str(e))
            return self._format_response(None, message="error")
