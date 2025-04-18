import logging
from datetime import datetime, timezone
from typing import List, Optional

from garth.data._base import Data
from garth.utils import camel_to_snake_dict
from pydantic.dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class HeartRateDescriptor:
    """심박수 데이터 필드 설명"""

    key: str  # timestamp 또는 heartrate
    index: int  # 배열에서의 인덱스 위치


@dataclass(frozen=True)
class HeartRateValue:
    """심박수 측정값"""

    timestamp: int
    heart_rate: Optional[int]  # 심박수 (bpm)

    @property
    def start_time_gmt(self) -> datetime:
        """측정 시간 (UTC)"""
        return datetime.fromtimestamp(self.timestamp / 1000, timezone.utc)


@dataclass(frozen=True)
class HeartRate(Data):
    """심박수 시계열 데이터"""

    # [사용자 정보]
    user_profile_pk: int

    # [날짜/시간]
    calendar_date: str
    start_timestamp_gmt: datetime
    end_timestamp_gmt: datetime
    start_timestamp_local: datetime
    end_timestamp_local: datetime

    # [데이터 구조]
    heart_rate_value_descriptors: Optional[List[HeartRateDescriptor]] = None
    heart_rate_values: Optional[List[HeartRateValue]] = None  # 변환된 측정값 목록

    # [심박수 통계]
    max_heart_rate: Optional[int] = None
    min_heart_rate: Optional[int] = None
    resting_heart_rate: Optional[int] = None
    last_seven_days_avg_resting_heart_rate: Optional[int] = None

    @property
    def local_offset(self) -> float:
        """로컬 시간과 GMT의 차이 (초)"""
        return (self.start_timestamp_local - self.start_timestamp_gmt).total_seconds()

    @classmethod
    def get(cls, date: str, *, client=None) -> Optional["HeartRate"]:
        """심박수 시계열 데이터 조회"""
        client = client
        path = "/wellness-service/wellness/dailyHeartRate"
        params = {"date": date}

        raw_data = client.connectapi(path, params=params)
        if not raw_data:
            return None
        try:
            data = camel_to_snake_dict(raw_data)
            heart_rate_values = data.get("heart_rate_values", [])
            values = []
            if heart_rate_values:
                for timestamp, heart_rate in heart_rate_values:
                    values.append(
                        HeartRateValue(
                            timestamp=timestamp,
                            heart_rate=(
                                int(heart_rate) if heart_rate is not None else None
                            ),
                        )
                    )
            data["heart_rate_values"] = values

            return cls(**data)
        except Exception as e:
            logger.warning(f"심박수 데이터 처리 중 오류 발생: {str(e)}")
            return None
