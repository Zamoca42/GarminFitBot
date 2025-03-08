from datetime import datetime, timezone
from typing import List, Optional

from garth.data._base import Data
from garth.utils import camel_to_snake_dict
from pydantic.dataclasses import dataclass


@dataclass(frozen=True)
class ActivityType:
    """활동 유형"""

    type_id: int
    type_key: str
    parent_type_id: int
    is_hidden: bool
    restricted: bool
    trimmable: bool


@dataclass(frozen=True)
class EventType:
    """이벤트 유형"""

    type_id: int
    type_key: str
    sort_order: int


@dataclass(frozen=True)
class Privacy:
    """공개 범위"""

    type_id: int
    type_key: str


@dataclass(frozen=True)
class SummarizedDiveInfo:
    """다이빙 요약 정보"""

    summarized_dive_gases: List = None


@dataclass(frozen=True)
class SummarizedExerciseSet:
    """운동 세트 요약"""

    category: str
    reps: int
    volume: float
    duration: float
    sets: int


@dataclass(frozen=True)
class SplitSummary:
    """구간 요약"""

    total_ascent: Optional[float] = None
    duration: Optional[float] = None
    split_type: Optional[str] = None
    num_climb_sends: Optional[int] = None
    max_elevation_gain: Optional[float] = None
    average_elevation_gain: Optional[float] = None
    max_distance: Optional[float] = None
    distance: Optional[float] = None
    average_speed: Optional[float] = None
    max_speed: Optional[float] = None
    num_falls: Optional[int] = None
    elevation_loss: Optional[float] = None


@dataclass(frozen=True)
class Activity(Data):
    """활동 데이터"""

    # [기본 정보]
    activity_id: int
    activity_name: str
    start_time_local: datetime
    start_time_gmt: datetime
    activity_type: ActivityType
    event_type: EventType

    # [거리/시간]
    duration: float
    elapsed_duration: float
    moving_duration: float

    # [칼로리]
    calories: int

    # [상태]
    has_polyline: bool
    has_splits: bool
    manual_activity: bool
    favorite: bool
    privacy: Privacy

    # [사용자]
    owner_id: int
    owner_display_name: str
    owner_full_name: str
    user_pro: bool

    # [Optional 필드]

    # [속도]
    average_speed: Optional[float] = None
    max_speed: Optional[float] = None

    # [위치/거리]
    distance: Optional[float] = None
    start_latitude: Optional[float] = None
    start_longitude: Optional[float] = None
    end_latitude: Optional[float] = None
    end_longitude: Optional[float] = None

    # [고도]
    elevation_gain: Optional[float] = None
    elevation_loss: Optional[float] = None
    min_elevation: Optional[float] = None
    max_elevation: Optional[float] = None

    # [심박수]
    average_hr: Optional[int] = None
    max_hr: Optional[int] = None

    # [걸음/케이던스]
    steps: Optional[int] = None
    average_running_cadence_in_steps_per_minute: Optional[float] = None
    max_running_cadence_in_steps_per_minute: Optional[float] = None
    max_double_cadence: Optional[float] = None
    avg_stride_length: Optional[float] = None

    # [칼로리]
    bmr_calories: Optional[int] = None

    # [운동 효과]
    training_effect_label: Optional[str] = None
    aerobic_training_effect_message: Optional[str] = None
    anaerobic_training_effect_message: Optional[str] = None
    vo2_max_value: Optional[int] = None

    # [강도]
    moderate_intensity_minutes: Optional[int] = None
    vigorous_intensity_minutes: Optional[int] = None
    hr_time_in_zone_1: Optional[float] = None
    hr_time_in_zone_2: Optional[float] = None
    hr_time_in_zone_3: Optional[float] = None
    hr_time_in_zone_4: Optional[float] = None
    hr_time_in_zone_5: Optional[float] = None

    # [기타 상태]
    lap_count: Optional[int] = None

    # [장비/앱]
    device_id: Optional[int] = None
    manufacturer: Optional[str] = None
    time_zone_id: Optional[int] = None
    water_estimated: Optional[int] = None

    # [요약 데이터]
    summarized_dive_info: Optional[SummarizedDiveInfo] = None
    summarized_exercise_sets: Optional[List[SummarizedExerciseSet]] = None
    split_summaries: Optional[List[SplitSummary]] = None

    @property
    def start_time_utc(self) -> datetime:
        """시작 시간 (UTC)"""
        return self.start_time_gmt.replace(tzinfo=timezone.utc)

    @property
    def local_offset(self) -> float:
        """로컬 시간과 GMT의 차이 (초)"""
        gmt_timestamp = self.start_time_gmt.timestamp()
        local_timestamp = self.start_time_local.timestamp()
        return local_timestamp - gmt_timestamp

    @classmethod
    def get(cls, day: str, *, client=None) -> Optional["Activity"]:
        """특정 날짜의 활동 조회"""
        # 활동은 list로만 조회 가능하므로 NotImplementedError 발생
        raise NotImplementedError(
            "Activity does not support get() method. Use list() instead."
        )

    @classmethod
    def list(cls, limit: int = 20, start: int = 0, *, client=None) -> List["Activity"]:
        """활동 목록 조회"""
        client = client
        path = "/activitylist-service/activities/search/activities"
        params = {"limit": limit, "start": start}

        raw_data = client.connectapi(path, params=params)
        if not raw_data:
            return []

        activities = []
        for activity_data in raw_data:
            data = camel_to_snake_dict(activity_data)
            activities.append(cls(**data))

        return activities
