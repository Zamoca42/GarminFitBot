from datetime import datetime
from typing import List, Optional
from pydantic.dataclasses import dataclass

from garth.data._base import Data
from garth.utils import camel_to_snake_dict

@dataclass(frozen=True)
class Baseline:
    low_upper: int
    balanced_low: int
    balanced_upper: int
    marker_value: float

@dataclass(frozen=True)
class HRVSummary:
    """HRV 요약 정보"""
    calendar_date: str
    weekly_avg: int
    last_night_avg: int
    last_night_5_min_high: int
    create_time_stamp: datetime
    status: str
    feedback_phrase: str
    baseline: Optional[Baseline] = None

@dataclass(frozen=True)
class HRVReading:
    """HRV 측정값"""
    hrv_value: int
    reading_time_gmt: datetime
    reading_time_local: datetime

@dataclass(frozen=True)
class SleepHRV(Data):
    """수면 중 HRV 데이터"""
    # [사용자 정보]
    user_profile_pk: int


    # [측정 시간]
    start_timestamp_gmt: datetime
    end_timestamp_gmt: datetime
    start_timestamp_local: datetime
    end_timestamp_local: datetime
    sleep_start_timestamp_gmt: datetime
    sleep_end_timestamp_gmt: datetime
    sleep_start_timestamp_local: datetime
    sleep_end_timestamp_local: datetime

    # [HRV 요약]
    hrv_summary: Optional[HRVSummary] = None

    # [측정값]
    hrv_readings: Optional[List[HRVReading]] = None

    @classmethod
    def get(cls, date: str, *, client=None) -> Optional["SleepHRV"]:
        """수면 HRV 데이터 조회"""
        client = client
        path = f"/hrv-service/hrv/{date}"
        
        raw_data = client.connectapi(path)
        if not raw_data:
            return None
            
        data = camel_to_snake_dict(raw_data)
        return cls(**data)

    @classmethod
    def get_summary(cls, date: str, *, client=None) -> Optional["SleepHRV"]:
        """수면 HRV 요약 데이터만 조회 (readings 제외)"""
        client = client
        path = f"/hrv-service/hrv/{date}"
        
        raw_data = client.connectapi(path)
        if not raw_data:
            return None
            
        data = camel_to_snake_dict(raw_data)
        data.pop("hrv_readings", None)
        return cls(**data) 
    
    @classmethod
    def get_readings(cls, date: str, *, client=None) -> Optional["SleepHRV"]:
        """수면 HRV 측정값 데이터만 조회 (summary 제외)"""
        client = client
        path = f"/hrv-service/hrv/{date}"
        
        raw_data = client.connectapi(path)
        if not raw_data:
            return None
            
        data = camel_to_snake_dict(raw_data)
        data.pop("hrv_summary", None)
        return cls(**data) 