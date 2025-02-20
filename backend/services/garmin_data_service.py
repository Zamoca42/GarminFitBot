import logging
from typing import Optional, List
from datetime import date

from garth import Client as GarthClient, DailySteps
from garth.data.sleep import SleepData
from garth.data.hrv import HRVData
from garth.stats.sleep import DailySleep
from garth.stats.stress import DailyStress, WeeklyStress
from garth.stats.hrv import DailyHRV

logger = logging.getLogger(__name__)

class GarminDataService:
    """Garth 모델을 사용한 데이터 서비스"""
    def __init__(self, client: GarthClient):
        self.client = client

    def get_sleep_details(self, day: str) -> Optional[SleepData]:
        """
        수면 상세 데이터 조회
        TODO: sleep DTO와 movement 분리
        """
        logger.info("수면 상세 데이터 조회 - Date: %s", day)
        return SleepData.get(day, client=self.client)

    def get_sleep_quality_stats(self, end_date: str = None, days: int = 7) -> List[DailySleep]:
        """수면 품질 통계 데이터 조회"""
        logger.info("수면 통계 조회 - EndDate: %s, Days: %d", end_date, days)
        return DailySleep.list(end=end_date, period=days, client=self.client)

    def get_stress_stats(self, end_date: str = None, days: int = 7) -> List[DailyStress]:
        """일간 스트레스 통계 조회"""
        logger.info("일간 스트레스 통계 조회 - EndDate: %s, Days: %d", end_date, days)
        return DailyStress.list(end=end_date, period=days, client=self.client)

    def get_weekly_stress_stats(self, end_date: str = None, weeks: int = 4) -> List[WeeklyStress]:
        """주간 스트레스 통계 조회"""
        logger.info("주간 스트레스 통계 조회 - EndDate: %s, Weeks: %d", end_date, weeks)
        return WeeklyStress.list(end=end_date, period=weeks, client=self.client)

    def get_hrv_stats(self, end_date: str = None, days: int = 7) -> List[DailyHRV]:
        """일간 수면 중 HRV 통계 데이터 조회"""
        logger.info("일간 수면 중 HRV 통계 조회 - EndDate: %s, Days: %d", end_date, days)
        return DailyHRV.list(end=end_date, period=days, client=self.client) 
    
    def get_daily_steps_stats(self, end_date: str = None, days: int = 7) -> List[DailySteps]:
        """일간 걸음 수 통계 데이터 조회"""
        logger.info("일간 걸음 수 통계 조회 - EndDate: %s, Days: %d", end_date, days)
        return DailySteps.list(end=end_date, period=days, client=self.client)
    
