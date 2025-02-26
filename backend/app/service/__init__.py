"""
Garmin 서비스 패키지

기본 구조:
- 기본 서비스 (BaseGarminService): 공통 기능 제공
- 인증 관리 (GarminAuthManager): 사용자 인증 및 토큰 관리
- 데이터 서비스:
  - 요약 데이터 (SummaryService): 일일 활동 요약, 수면 데이터 등
  - 시계열 데이터 (TimeSeriesService): 심박수, 스트레스 등의 상세 데이터
  - 통계 데이터 (StatsService): 기간별 통계 및 분석
- 데이터 수집 (DataCollectorService): 배치 작업용 데이터 수집
"""

from ._base_service import BaseGarminService
from .auth_manager import GarminAuthManager
from .data_collector_service import GarminDataCollectorService
from .stats_service import GarminStatsService
from .summary_service import GarminSummaryService
from .time_series_service import GarminTimeSeriesService
from .token_service import TokenService

__all__ = [
    "BaseGarminService",
    "GarminAuthManager",
    "GarminSummaryService",
    "GarminTimeSeriesService",
    "GarminStatsService",
    "GarminDataCollectorService",
    "TokenService",
]
