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

    type_id: Optional[int] = None
    type_key: Optional[str] = None


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

    # [기타 상태]
    includes_wellness_data: bool
    includes_activity_data: bool
    includes_calorie_consumed_data: bool
    privacy_protected: bool

    # Optional 필드들 (기본값 있는 필드들)

    # [칼로리]
    total_kilocalories: Optional[int]
    active_kilocalories: Optional[int]
    bmr_kilocalories: Optional[int]
    wellness_kilocalories: Optional[int]
    wellness_active_kilocalories: Optional[int]
    net_remaining_kilocalories: Optional[int]

    # [걸음/거리]
    total_steps: Optional[int]
    daily_step_goal: Optional[int]
    total_distance_meters: Optional[float]
    wellness_distance_meters: Optional[float]

    # [활동 시간]
    highly_active_seconds: Optional[int]
    active_seconds: Optional[int]
    sedentary_seconds: Optional[int]
    sleeping_seconds: Optional[int]
    moderate_intensity_minutes: Optional[int]
    vigorous_intensity_minutes: Optional[int]
    intensity_minutes_goal: Optional[int]
    measurable_awake_duration: Optional[int]
    measurable_asleep_duration: Optional[int]

    # [층수]
    floors_ascended_in_meters: Optional[float]
    floors_descended_in_meters: Optional[float]
    floors_ascended: Optional[float]
    floors_descended: Optional[float]
    user_floors_ascended_goal: Optional[int]

    # [심박수]
    min_heart_rate: Optional[int]
    max_heart_rate: Optional[int]
    resting_heart_rate: Optional[int]
    last_seven_days_avg_resting_heart_rate: Optional[int]
    min_avg_heart_rate: Optional[int]
    max_avg_heart_rate: Optional[int]

    # [스트레스]
    average_stress_level: Optional[int]
    max_stress_level: Optional[int]
    stress_duration: Optional[int]
    rest_stress_duration: Optional[int]
    activity_stress_duration: Optional[int]
    total_stress_duration: Optional[int]
    low_stress_duration: Optional[int]
    medium_stress_duration: Optional[int]
    stress_percentage: Optional[float]
    rest_stress_percentage: Optional[float]
    activity_stress_percentage: Optional[float]
    low_stress_percentage: Optional[float]
    medium_stress_percentage: Optional[float]
    high_stress_percentage: Optional[float]
    stress_qualifier: Optional[str]

    # [바디 배터리]
    body_battery_charged_value: Optional[int]
    body_battery_drained_value: Optional[int]
    body_battery_highest_value: Optional[int]
    body_battery_lowest_value: Optional[int]
    body_battery_most_recent_value: Optional[int]
    body_battery_during_sleep: Optional[int]
    body_battery_at_wake_time: Optional[int]
    body_battery_version: Optional[int]

    # [호흡]
    avg_waking_respiration_value: Optional[float]
    highest_respiration_value: Optional[int]
    lowest_respiration_value: Optional[int]
    latest_respiration_value: Optional[int]
    latest_respiration_time_gmt: Optional[str]
    respiration_algorithm_version: Optional[int]

    # [기본 정보]
    wellness_description: Optional[str]

    # [칼로리]
    burned_kilocalories: Optional[int]
    consumed_kilocalories: Optional[int]
    remaining_kilocalories: Optional[int]
    net_calorie_goal: Optional[int]

    # [동기화]
    last_sync_timestamp_gmt: Optional[str]

    # [심박수]
    abnormal_heart_rate_alerts_count: Optional[int]

    # [산소포화도]
    average_spo2: Optional[float]
    lowest_spo2: Optional[int]
    latest_spo2: Optional[int]
    latest_spo2_reading_time_gmt: Optional[str]
    latest_spo2_reading_time_local: Optional[str]

    # [기타]
    average_monitoring_environment_altitude: Optional[float]
    resting_calories_from_activity: Optional[int]

    # [스트레스]
    uncategorized_stress_duration: Optional[int]
    high_stress_duration: Optional[int]

    # [바디 배터리 이벤트]
    body_battery_dynamic_feedback_event: Optional[BodyBatteryFeedbackEvent]
    end_of_day_body_battery_dynamic_feedback_event: Optional[BodyBatteryFeedbackEvent]
    body_battery_activity_event_list: Optional[List[BodyBatteryActivityEvent]]

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
