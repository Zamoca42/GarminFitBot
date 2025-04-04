import logging
from datetime import datetime, timezone
from typing import List, Optional

from garth.data._base import Data
from pydantic.dataclasses import dataclass

from core.util.dict_converter import camel_to_snake_dict_safe

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class StressDescriptor:
    """스트레스 데이터 필드 설명"""

    key: str  # timestamp 또는 stressLevel
    index: int  # 배열에서의 인덱스 위치


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

    # [스트레스 통계]
    max_stress_level: int
    avg_stress_level: int
    stress_chart_value_offset: int
    stress_chart_y_axis_origin: int

    # [데이터 구조]
    stress_value_descriptors_dto_list: List[StressDescriptor]
    stress_values: List[StressValue]  # 변환된 측정값 목록

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
            # 안전한 변환 함수 사용
            data = camel_to_snake_dict_safe(raw_data, cls=cls)

            # 스트레스 측정값 변환
            values = []
            for timestamp, stress_level in data.get("stress_values_array", []):
                values.append(
                    StressValue(
                        timestamp=timestamp,
                        stress_level=(
                            int(stress_level) if stress_level is not None else None
                        ),
                    )
                )
            data["stress_values"] = values

            return cls(**data)
        except Exception as e:
            logger.warning(f"스트레스 데이터 처리 중 오류 발생: {str(e)}")
            return None
