import logging
from datetime import datetime, timezone
from typing import List, Optional

from garth.data._base import Data
from garth.utils import camel_to_snake_dict
from pydantic.dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class StressValue:
    """스트레스 측정값"""

    timestamp: int
    stress_level: Optional[
        int
    ]  # 스트레스 레벨 (-2: 수면, -1: 측정불가, 0~100: 스트레스 수준)

    @property
    def start_time_gmt(self) -> datetime:
        return datetime.fromtimestamp(self.timestamp / 1000, timezone.utc)

    @property
    def end_time_gmt(self) -> datetime:
        return datetime.fromtimestamp(self.timestamp / 1000, timezone.utc)


@dataclass(frozen=True)
class Stress(Data):
    """스트레스 시계열 데이터"""

    # [사용자 정보]
    user_profile_pk: int

    # [날짜/시간]
    calendar_date: str
    start_timestamp_gmt: datetime
    end_timestamp_gmt: datetime
    start_timestamp_local: datetime
    end_timestamp_local: datetime

    # [데이터 구조]
    stress_values: List[StressValue]

    # [스트레스 통계]
    max_stress_level: Optional[int] = None
    avg_stress_level: Optional[int] = None

    @property
    def local_offset(self) -> int:
        return (self.start_timestamp_local - self.start_timestamp_gmt).total_seconds()

    @classmethod
    def get(cls, date: str, *, client=None) -> Optional["Stress"]:
        """스트레스 시계열 데이터 조회"""
        client = client
        path = f"/wellness-service/wellness/dailyStress/{date}"

        raw_data = client.connectapi(path)
        if not raw_data:
            return None

        try:
            stress_data = camel_to_snake_dict(raw_data)

            values = []
            for timestamp, stress_level in stress_data.get("stress_values_array", []):
                values.append(
                    StressValue(
                        timestamp=timestamp,
                        stress_level=(
                            int(stress_level) if stress_level is not None else None
                        ),
                    )
                )
            stress_data["stress_values"] = values

            return cls(**stress_data)
        except Exception as e:
            logger.warning(f"스트레스 데이터 처리 중 오류 발생: {str(e)}")
            return None
