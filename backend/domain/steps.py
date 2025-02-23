from datetime import datetime
from typing import List, Optional
from pydantic.dataclasses import dataclass

from garth.utils import camel_to_snake_dict

@dataclass(frozen=True)
class StepsValue:
    """걸음수 측정값"""
    start_gmt: datetime  # 시작 시간
    end_gmt: datetime  # 종료 시간
    steps: int  # 걸음수
    pushes: int  # 휠체어 밀기 횟수
    primary_activity_level: str  # 활동 수준 (sedentary, active, highlyActive, sleeping, generic)
    activity_level_constant: bool  # 활동 수준 일정 여부

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
            snake_data = camel_to_snake_dict(data)
            values.append(cls(**snake_data))
            
        return values 