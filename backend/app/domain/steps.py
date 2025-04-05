import logging
from datetime import datetime, timezone
from typing import List, Optional

from garth.utils import camel_to_snake_dict
from pydantic.dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class StepsValue:
    """걸음수 측정값"""

    start_gmt: datetime
    end_gmt: datetime
    steps: int
    pushes: int  # 휠체어 밀기 횟수
    primary_activity_level: (
        str  # 활동 수준 (sedentary, active, highlyActive, sleeping, generic)
    )
    activity_level_constant: bool  # 활동 수준 일정 여부

    @property
    def start_time_gmt(self) -> datetime:
        """시작 시간 (UTC)"""
        return self.start_gmt.replace(tzinfo=timezone.utc)

    @property
    def end_time_gmt(self) -> datetime:
        """종료 시간 (UTC)"""
        return self.end_gmt.replace(tzinfo=timezone.utc)

    @classmethod
    def get_readings(cls, date: str, *, client=None) -> Optional[List["StepsValue"]]:
        """걸음수 시계열 데이터 조회"""
        client = client
        path = "/wellness-service/wellness/dailySummaryChart"
        params = {"date": date}

        raw_data = client.connectapi(path, params=params)
        if not raw_data:
            return None

        values = []
        for data in raw_data:
            try:
                snake_data = camel_to_snake_dict(data)
                values.append(cls(**snake_data))
            except Exception as e:
                logger.warning(f"걸음수 데이터 처리 중 오류 발생: {str(e)}")
                continue

        return values
