from datetime import datetime
from typing import List, Optional, Union
from pydantic.dataclasses import dataclass

from garth.data._base import Data
from garth.utils import camel_to_snake_dict

@dataclass(frozen=True)
class HeartRateDescriptor:
    """심박수 데이터 필드 설명"""
    key: str  # timestamp 또는 heartrate
    index: int  # 배열에서의 인덱스 위치

@dataclass(frozen=True)
class HeartRateValue:
    """심박수 측정값"""
    time: datetime  # 측정 시간
    heart_rate: Optional[int]  # 심박수 (bpm)

@dataclass(frozen=True)
class HeartRate(Data):
    """심박수 시계열 데이터"""
    # [사용자 정보]
    user_profile_pk: int

    # [날짜/시간]
    calendar_date: str
    start_timestamp_gmt: str
    end_timestamp_gmt: str
    start_timestamp_local: str
    end_timestamp_local: str

    # [심박수 통계]
    max_heart_rate: int
    min_heart_rate: int
    resting_heart_rate: int
    last_seven_days_avg_resting_heart_rate: int

    # [데이터 구조]
    heart_rate_value_descriptors: List[HeartRateDescriptor]
    heart_rate_values: List[HeartRateValue]  # 변환된 측정값 목록

    @classmethod
    def get(cls, date: str, *, client=None) -> Optional["HeartRate"]:
        """심박수 시계열 데이터 조회"""
        client = client
        path = "/wellness-service/wellness/dailyHeartRate"
        params = {"date": date}
        
        raw_data = client.connectapi(path, params=params)
        if not raw_data:
            return None
            
        data = camel_to_snake_dict(raw_data)
        
        # 심박수 측정값 변환
        values = []
        for timestamp, heart_rate in data["heart_rate_values"]:
            values.append({
                "time": datetime.fromtimestamp(timestamp/1000).strftime("%Y-%m-%d %H:%M:%S"),
                "heart_rate": int(heart_rate) if heart_rate is not None else None
            })
        data["heart_rate_values"] = values
        
        return cls(**data) 