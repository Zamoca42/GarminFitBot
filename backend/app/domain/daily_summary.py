from datetime import datetime
from typing import List, Optional

from garth.data._base import Data
from garth.utils import camel_to_snake_dict
from pydantic.dataclasses import dataclass


@dataclass(frozen=True)
class BodyBatteryFeedbackEvent:
    """바디 배터리 피드백 이벤트"""

    event_timestamp_gmt: datetime
    body_battery_level: str
    feedback_short_type: Optional[str] = None
    feedback_long_type: Optional[str] = None


@dataclass(frozen=True)
class BodyBatteryActivityEvent:
    """바디 배터리 활동 이벤트"""

    event_type: str
    event_start_time_gmt: datetime
    timezone_offset: int
    duration_in_milliseconds: int
    body_battery_impact: int
    feedback_type: str
    short_feedback: str
    device_id: int
    activity_name: Optional[str] = None
    activity_type: Optional[str] = None
    activity_id: Optional[int] = None
    event_update_time_gmt: Optional[datetime] = None


@dataclass(frozen=True)
class Rule:
    """데이터 접근 규칙"""

    type_id: int
    type_key: str


@dataclass(frozen=True)
class DailySummary(Data):
    """일일 활동 요약"""

    # 필수 필드들 (기본값 없는 필드들)

    # [사용자 정보]
    user_profile_id: int
    user_daily_summary_id: int
    uuid: str
    rule: Rule
    source: str

    # [시간 정보]
    calendar_date: str
    wellness_start_time_gmt: datetime
    wellness_start_time_local: datetime
    wellness_end_time_gmt: datetime
    wellness_end_time_local: datetime
    duration_in_milliseconds: int

    # [칼로리]
    total_kilocalories: int
    active_kilocalories: int
    bmr_kilocalories: int
    wellness_kilocalories: int
    wellness_active_kilocalories: int
    net_remaining_kilocalories: int

    # [걸음/거리]
    total_steps: int
    daily_step_goal: int
    total_distance_meters: float
    wellness_distance_meters: float

    # [활동 시간]
    highly_active_seconds: int
    active_seconds: int
    sedentary_seconds: int
    sleeping_seconds: int
    moderate_intensity_minutes: int
    vigorous_intensity_minutes: int
    intensity_minutes_goal: int
    measurable_awake_duration: int
    measurable_asleep_duration: int

    # [층수]
    floors_ascended_in_meters: float
    floors_descended_in_meters: float
    floors_ascended: float
    floors_descended: float
    user_floors_ascended_goal: int

    # [심박수]
    min_heart_rate: int
    max_heart_rate: int
    resting_heart_rate: int
    last_seven_days_avg_resting_heart_rate: int
    min_avg_heart_rate: int
    max_avg_heart_rate: int

    # [스트레스]
    average_stress_level: int
    max_stress_level: int
    stress_duration: int
    rest_stress_duration: int
    activity_stress_duration: int
    total_stress_duration: int
    low_stress_duration: int
    medium_stress_duration: int
    stress_percentage: float
    rest_stress_percentage: float
    activity_stress_percentage: float
    low_stress_percentage: float
    medium_stress_percentage: float
    high_stress_percentage: float
    stress_qualifier: str

    # [바디 배터리]
    body_battery_charged_value: int
    body_battery_drained_value: int
    body_battery_highest_value: int
    body_battery_lowest_value: int
    body_battery_most_recent_value: int
    body_battery_during_sleep: int
    body_battery_at_wake_time: int
    body_battery_version: int

    # [호흡]
    avg_waking_respiration_value: float
    highest_respiration_value: int
    lowest_respiration_value: int
    latest_respiration_value: int
    latest_respiration_time_gmt: str
    respiration_algorithm_version: int

    # [기타 상태]
    includes_wellness_data: bool
    includes_activity_data: bool
    includes_calorie_consumed_data: bool
    privacy_protected: bool

    # Optional 필드들 (기본값 있는 필드들)

    # [기본 정보]
    wellness_description: Optional[str] = None

    # [칼로리]
    burned_kilocalories: Optional[int] = None
    consumed_kilocalories: Optional[int] = None
    remaining_kilocalories: Optional[int] = None
    net_calorie_goal: Optional[int] = None

    # [동기화]
    last_sync_timestamp_gmt: Optional[str] = None

    # [심박수]
    abnormal_heart_rate_alerts_count: Optional[int] = None

    # [산소포화도]
    average_spo2: Optional[float] = None
    lowest_spo2: Optional[int] = None
    latest_spo2: Optional[int] = None
    latest_spo2_reading_time_gmt: Optional[str] = None
    latest_spo2_reading_time_local: Optional[str] = None

    # [기타]
    average_monitoring_environment_altitude: Optional[float] = None
    resting_calories_from_activity: Optional[int] = None

    # [스트레스]
    uncategorized_stress_duration: Optional[int] = None
    high_stress_duration: Optional[int] = None

    # [바디 배터리 이벤트]
    body_battery_dynamic_feedback_event: Optional[BodyBatteryFeedbackEvent] = None
    end_of_day_body_battery_dynamic_feedback_event: Optional[
        BodyBatteryFeedbackEvent
    ] = None
    body_battery_activity_event_list: Optional[List[BodyBatteryActivityEvent]] = None

    @property
    def local_offset(self) -> int:
        """로컬 오프셋"""
        return (
            self.wellness_start_time_local - self.wellness_start_time_gmt
        ).total_seconds()

    @classmethod
    def get(cls, date: str, *, client=None) -> Optional["DailySummary"]:
        """일일 활동 요약 조회"""
        client = client
        path = "/usersummary-service/usersummary/daily"
        params = {"calendarDate": date}

        raw_data = client.connectapi(path, params=params)
        if not raw_data:
            return None

        data = camel_to_snake_dict(raw_data)
        return cls(**data)
