import logging
import traceback
from datetime import date, datetime, timedelta, timezone
from typing import Any, Dict, Generic, List, Optional, TypeAlias, TypeVar, Union

from garth import DailyHRV, SleepData
from garth.data.sleep import SleepMovement
from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.domain import (
    Activity,
    DailySummary,
    HeartRate,
    HeartRateValue,
    HRVReading,
    SleepHRV,
    StepsValue,
    Stress,
    StressValue,
)
from app.model import Activity as ActivityModel
from app.model import (
    HeartRateDaily,
    HeartRateReading,
    SleepHRVReading,
)
from app.model import SleepMovement as SleepMovementModel
from app.model import (
    SleepSession,
    StepsDaily,
    StepsIntraday,
    StressDaily,
    StressReading,
)
from app.service._base_service import BaseGarminService
from core.util.safe_access import (
    log_exception,
    safe_float,
    safe_get,
    safe_get_item,
    safe_list,
)

logger = logging.getLogger(__name__)

# 제네릭 타입 정의
T = TypeVar("T")
D = TypeVar("D")  # 도메인 모델 타입
M = TypeVar("M")  # DB 모델 타입

# 캐시 데이터 타입 정의
CacheData: TypeAlias = Union[
    Activity,
    DailyHRV,
    DailySummary,
    HeartRate,
    SleepData,
    SleepHRV,
    StepsValue,
    Stress,
]


class BaseDataCollector(Generic[D, M]):
    """데이터 수집을 위한 기본 클래스"""

    def __init__(self, client, data_cache: Dict[str, CacheData], session: Session):
        self.client = client
        self.data_cache = data_cache
        self.session = session
        self.logger = logging.getLogger(self.__class__.__name__)

    def fetch_data(self, date_str: str) -> Optional[D]:
        """API에서 데이터 가져오기"""
        raise NotImplementedError

    def map_data(self, user_id: int, target_date: date, data: D) -> Optional[M]:
        """데이터 매핑"""
        raise NotImplementedError

    def delete_existing_data(self, user_id: int, target_date: date) -> None:
        """기존 데이터 삭제"""
        raise NotImplementedError

    def safe_get_cache(self, key: str) -> Optional[CacheData]:
        """캐시에서 안전하게 데이터 가져오기"""
        return self.data_cache.get(key)

    def log_mapping_error(
        self, error: Exception, context: Dict[str, Any] = None
    ) -> None:
        """매핑 오류 로깅"""
        log_exception("데이터 매핑", error, context or {})

    def validate_data(self, data: Any) -> bool:
        """데이터 유효성 검사"""
        return data is not None

    def safe_session_execute(
        self, query, error_msg: str = "데이터베이스 쿼리 실행 실패"
    ) -> Any:
        """안전하게 세션 쿼리 실행"""
        try:
            return self.session.execute(query)
        except Exception as e:
            self.logger.error(f"{error_msg}: {str(e)}")
            self.session.rollback()
            raise


class HeartRateCollector(BaseDataCollector):
    """심박수 데이터 수집기"""

    def fetch_data(
        self, date_str: str
    ) -> Optional[Dict[str, Union[HeartRate, SleepHRV, DailyHRV]]]:
        heart_rate_data = self.safe_get_cache(f"heart_rate:{date_str}")

        if not self.validate_data(heart_rate_data):
            self.logger.info(f"심박수 데이터가 없습니다: {date_str}")
            return None

        return {
            "heart_rate_data": heart_rate_data,
        }

    def map_data(
        self,
        user_id: int,
        target_date: date,
        data: Dict[str, Union[HeartRate, SleepHRV, DailyHRV]],
    ) -> Optional[Dict[str, Any]]:
        try:
            heart_rate_data = safe_get_item(data, "heart_rate_data", HeartRate)

            if not self.validate_data(heart_rate_data):
                self.logger.warning(
                    f"심박수 데이터가 유효하지 않습니다: 사용자 {user_id}, 날짜 {target_date}"
                )
                return None

            resting_hr = safe_get(
                heart_rate_data, "resting_heart_rate", HeartRate.resting_heart_rate
            )
            max_hr = safe_get(
                heart_rate_data, "max_heart_rate", HeartRate.max_heart_rate
            )
            min_hr = safe_get(
                heart_rate_data, "min_heart_rate", HeartRate.min_heart_rate
            )
            heart_rate_values: List[HeartRateValue] = safe_list(
                safe_get(heart_rate_data, "heart_rate_values")
            )
            local_offset = safe_float(safe_get(heart_rate_data, "local_offset", 0.0))

            avg_heart_rate = None
            valid_readings = []
            if heart_rate_values:
                for reading in heart_rate_values:
                    hr_value = reading.heart_rate
                    if hr_value:
                        valid_readings.append(hr_value)

            if valid_readings:
                avg_heart_rate = sum(valid_readings) / len(valid_readings)

            heart_rate_daily_summary = HeartRateDaily(
                user_id=user_id,
                date=target_date,
                resting_hr=resting_hr,
                max_hr=max_hr,
                min_hr=min_hr,
                avg_hr=avg_heart_rate,
            )

            readings = []
            if not heart_rate_values:
                self.logger.info(
                    f"심박수 시계열 데이터가 없습니다: 사용자 {user_id}, 날짜 {target_date}"
                )
                return {
                    "daily_summary": heart_rate_daily_summary,
                    "readings": [],
                }

            for reading in heart_rate_values:
                try:
                    start_time_gmt = reading.start_time_gmt
                    heart_rate_value = reading.heart_rate

                    if start_time_gmt is None:
                        self.logger.info("심박수 start_time_gmt가 None 있음")
                        continue

                    start_time_local = start_time_gmt.replace(tzinfo=None) + timedelta(
                        seconds=local_offset
                    )
                    readings.append(
                        HeartRateReading(
                            start_time_gmt=start_time_gmt,
                            start_time_local=start_time_local,
                            heart_rate=heart_rate_value,
                            daily_summary=heart_rate_daily_summary,
                        )
                    )
                except Exception as e:
                    self.log_mapping_error(e, {"reading": str(reading)})
                    continue

            return {
                "daily_summary": heart_rate_daily_summary,
                "readings": readings,
            }

        except Exception as e:
            self.log_mapping_error(
                e, {"user_id": user_id, "target_date": str(target_date)}
            )
            return None

    def delete_existing_data(self, user_id: int, target_date: date) -> None:
        """심박수 데이터 삭제"""
        try:
            result = self.safe_session_execute(
                select(HeartRateDaily).where(
                    HeartRateDaily.user_id == user_id,
                    HeartRateDaily.date == target_date,
                ),
                error_msg=f"심박수 데이터 검색 실패 - User: {user_id}, Date: {target_date}",
            )
            daily_summary = result.scalar_one_or_none()

            if daily_summary:
                self.safe_session_execute(
                    delete(HeartRateReading).where(
                        HeartRateReading.daily_summary_id == daily_summary.id,
                    ),
                    error_msg=f"심박수 상세 데이터 삭제 실패 - Summary ID: {daily_summary.id}",
                )
                self.session.delete(daily_summary)
        except Exception as e:
            self.logger.error(
                f"심박수 데이터 삭제 실패 - User: {user_id}, Date: {target_date}, Error: {str(e)}"
            )
            self.session.rollback()
            raise


class StressCollector(BaseDataCollector):
    """스트레스 데이터 수집기"""

    def fetch_data(
        self, date_str: str
    ) -> Optional[Dict[str, Union[Stress, DailySummary]]]:
        stress_data = self.safe_get_cache(f"stress:{date_str}")
        daily_summary = self.safe_get_cache(f"daily_summary:{date_str}")

        if not self.validate_data(stress_data) or not self.validate_data(daily_summary):
            self.logger.info(f"스트레스 또는 일일 요약 데이터가 없습니다: {date_str}")
            return None

        return {"stress_data": stress_data, "daily_summary": daily_summary}

    def map_data(
        self,
        user_id: int,
        target_date: date,
        data: Dict[str, Union[Stress, DailySummary]],
    ) -> Optional[Dict[str, Any]]:
        try:
            stress_data = safe_get_item(data, "stress_data", Stress)
            daily_summary = safe_get_item(data, "daily_summary", DailySummary)

            if not self.validate_data(stress_data) or not self.validate_data(
                daily_summary
            ):
                self.logger.info(
                    f"스트레스 또는 일일 요약 데이터가 유효하지 않습니다: 사용자 {user_id}, 날짜 {target_date}"
                )
                return None

            avg_stress_level = safe_get(
                stress_data, "avg_stress_level", Stress.avg_stress_level
            )
            max_stress_level = safe_get(
                stress_data, "max_stress_level", Stress.max_stress_level
            )
            stress_duration = safe_get(
                daily_summary, "stress_duration", DailySummary.stress_duration
            )
            rest_stress_duration = safe_get(
                daily_summary, "rest_stress_duration", DailySummary.rest_stress_duration
            )
            stress_values: List[StressValue] = safe_list(
                safe_get(stress_data, "stress_values")
            )
            local_offset = safe_float(safe_get(daily_summary, "local_offset", 0.0))

            stress_daily_summary = StressDaily(
                user_id=user_id,
                date=target_date,
                avg_stress_level=avg_stress_level,
                max_stress_level=max_stress_level,
                stress_duration_seconds=stress_duration,
                rest_duration_seconds=rest_stress_duration,
            )

            readings = []
            if not stress_values:
                self.logger.info(
                    f"스트레스 시계열 데이터가 없습니다: 사용자 {user_id}, 날짜 {target_date}"
                )
                return {
                    "daily_summary": stress_daily_summary,
                    "readings": [],
                }

            for reading in stress_values:
                try:
                    start_time_gmt = reading.start_time_gmt
                    stress_level = reading.stress_level

                    if start_time_gmt is None:
                        self.logger.info("스트레스 start_time_gmt가 None 있음")
                        continue

                    start_time_local = start_time_gmt.replace(tzinfo=None) + timedelta(
                        seconds=local_offset
                    )

                    readings.append(
                        StressReading(
                            start_time_gmt=start_time_gmt,
                            start_time_local=start_time_local,
                            stress_level=stress_level,
                            daily_summary=stress_daily_summary,
                        )
                    )
                except Exception as e:
                    self.log_mapping_error(e, {"reading": str(reading)})
                    continue

            return {
                "daily_summary": stress_daily_summary,
                "readings": readings,
            }

        except Exception as e:
            self.log_mapping_error(
                e, {"user_id": user_id, "target_date": str(target_date)}
            )
            return None

    def delete_existing_data(self, user_id: int, target_date: date) -> None:
        """스트레스 데이터 삭제"""
        try:
            result = self.safe_session_execute(
                select(StressDaily).where(
                    StressDaily.user_id == user_id,
                    StressDaily.date == target_date,
                ),
                error_msg=f"스트레스 데이터 검색 실패 - User: {user_id}, Date: {target_date}",
            )
            daily_summary = result.scalar_one_or_none()

            if daily_summary:
                self.safe_session_execute(
                    delete(StressReading).where(
                        StressReading.daily_summary_id == daily_summary.id,
                    ),
                    error_msg=f"스트레스 상세 데이터 삭제 실패 - Summary ID: {daily_summary.id}",
                )
                self.session.delete(daily_summary)
        except Exception as e:
            self.logger.error(
                f"스트레스 데이터 삭제 실패 - User: {user_id}, Date: {target_date}, Error: {str(e)}"
            )
            self.session.rollback()
            raise


class StepsCollector(BaseDataCollector):
    """걸음수 데이터 수집기"""

    def fetch_data(
        self, date_str: str
    ) -> Optional[Dict[str, Union[DailySummary, List[StepsValue]]]]:
        daily_summary_data = self.safe_get_cache(f"daily_summary:{date_str}")
        steps_data = self.safe_get_cache(f"steps_data:{date_str}")

        if not self.validate_data(daily_summary_data):
            self.logger.warning(f"일일 요약 데이터를 찾을 수 없음: {date_str}")
            return None

        return {"daily_summary": daily_summary_data, "steps_data": steps_data}

    def map_data(
        self,
        user_id: int,
        target_date: date,
        data: Dict[str, Union[DailySummary, List[StepsValue]]],
    ) -> Optional[Dict[str, Any]]:
        try:
            daily_summary_data = safe_get_item(data, "daily_summary", DailySummary)
            steps_data = safe_get_item(data, "steps_data", List[StepsValue])

            if not self.validate_data(daily_summary_data):
                self.logger.info(
                    f"일일 요약 데이터가 없습니다. 사용자: {user_id}, 날짜: {target_date}"
                )
                return None

            # 안전한 값 변환
            floors_climbed = safe_get(
                daily_summary_data, "floors_ascended", DailySummary.floors_ascended
            )
            local_offset = safe_float(safe_get(daily_summary_data, "local_offset", 0.0))
            total_steps = safe_get(
                daily_summary_data, "total_steps", DailySummary.total_steps
            )
            goal_steps = safe_get(
                daily_summary_data, "daily_step_goal", DailySummary.daily_step_goal
            )
            distance_meters = safe_float(
                safe_get(
                    daily_summary_data,
                    "total_distance_meters",
                    DailySummary.total_distance_meters,
                )
            )
            active_kilocalories = safe_get(
                daily_summary_data,
                "active_kilocalories",
                DailySummary.active_kilocalories,
            )
            highly_active_seconds = safe_get(
                daily_summary_data,
                "highly_active_seconds",
                DailySummary.highly_active_seconds,
            )
            active_seconds = safe_get(
                daily_summary_data, "active_seconds", DailySummary.active_seconds
            )
            steps_data: List[StepsValue] = safe_list(steps_data)

            steps_daily_summary = StepsDaily(
                user_id=user_id,
                date=target_date,
                total_steps=total_steps,
                goal_steps=goal_steps,
                distance=distance_meters / 1000,  # m -> km 변환
                calories=active_kilocalories,
                active_minutes=(highly_active_seconds + active_seconds) // 60,
                floors_climbed=floors_climbed,
            )

            # 상세 측정값 처리 (안전하게)
            readings = []
            if not steps_data:
                self.logger.info(
                    f"걸음수 시계열 데이터가 없습니다: 사용자 {user_id}, 날짜 {target_date}"
                )
                return {
                    "daily_summary": steps_daily_summary,
                    "readings": [],
                }

            for reading in steps_data:
                try:
                    start_time_gmt = reading.start_time_gmt
                    end_time_gmt = reading.end_time_gmt

                    if start_time_gmt is None or end_time_gmt is None:
                        self.logger.info("걸음수 time_gmt가 None 있음")
                        continue

                    start_time_local = start_time_gmt.replace(tzinfo=None) + timedelta(
                        seconds=local_offset
                    )

                    end_time_local = end_time_gmt.replace(tzinfo=None) + timedelta(
                        seconds=local_offset
                    )

                    readings.append(
                        StepsIntraday(
                            start_time_gmt=start_time_gmt,
                            end_time_gmt=end_time_gmt,
                            start_time_local=start_time_local,
                            end_time_local=end_time_local,
                            steps=reading.steps,
                            activity_level=reading.primary_activity_level,
                            intensity=0,
                            daily_summary=steps_daily_summary,
                        )
                    )
                except Exception as e:
                    self.log_mapping_error(e, {"reading": str(reading)})
                    continue

            return {
                "daily_summary": steps_daily_summary,
                "readings": readings,
            }
        except Exception as e:
            self.log_mapping_error(
                e, {"user_id": user_id, "target_date": str(target_date)}
            )
            return None

    def delete_existing_data(self, user_id: int, target_date: date) -> None:
        """걸음수 데이터 삭제"""
        try:
            result = self.safe_session_execute(
                select(StepsDaily).where(
                    StepsDaily.user_id == user_id,
                    StepsDaily.date == target_date,
                ),
                error_msg=f"걸음수 데이터 검색 실패 - User: {user_id}, Date: {target_date}",
            )
            daily_summary = result.scalar_one_or_none()

            if daily_summary:
                self.safe_session_execute(
                    delete(StepsIntraday).where(
                        StepsIntraday.daily_summary_id == daily_summary.id,
                    ),
                    error_msg=f"걸음수 상세 데이터 삭제 실패 - Summary ID: {daily_summary.id}",
                )
                self.session.delete(daily_summary)
        except Exception as e:
            self.logger.error(
                f"걸음수 데이터 삭제 실패 - User: {user_id}, Date: {target_date}, Error: {str(e)}"
            )
            self.session.rollback()
            raise


class SleepCollector(BaseDataCollector):
    """수면 데이터 수집기"""

    def fetch_data(
        self, date_str: str
    ) -> Optional[Dict[str, Union[SleepData, SleepHRV, List[SleepMovement]]]]:
        # 캐시된 데이터 사용
        sleep_data = self.safe_get_cache(f"sleep_data:{date_str}")
        hrv_data = self.safe_get_cache(f"sleep_hrv:{date_str}")

        if not self.validate_data(sleep_data):
            self.logger.info(f"수면 데이터가 없습니다: {date_str}")
            return None

        movements = []
        if sleep_data and hasattr(sleep_data, "sleep_movement"):
            movements = safe_list(sleep_data.sleep_movement)

        return {
            "sleep_data": sleep_data,
            "hrv_data": hrv_data,
            "movements": movements,
        }

    def map_data(
        self,
        user_id: int,
        target_date: date,
        data: Dict[str, Union[SleepData, SleepHRV, List[SleepMovement]]],
    ) -> Optional[Dict[str, Any]]:
        try:
            sleep_data = safe_get_item(data, "sleep_data", SleepData)
            hrv_data = safe_get_item(data, "hrv_data", SleepHRV)
            movements = safe_get_item(data, "movements", List[SleepMovement])

            if not self.validate_data(sleep_data):
                self.logger.info(
                    f"수면 데이터가 유효하지 않습니다: 사용자 {user_id}, 날짜 {target_date}"
                )
                return None

            # 안전한 값 추출
            daily_sleep_dto = sleep_data.daily_sleep_dto
            if not self.validate_data(daily_sleep_dto):
                self.logger.info(
                    f"수면 세션 데이터가 유효하지 않습니다: 사용자 {user_id}, 날짜 {target_date}"
                )
                return None

            sleep_start_timestamp_gmt = daily_sleep_dto.sleep_start_timestamp_gmt
            sleep_end_timestamp_gmt = daily_sleep_dto.sleep_end_timestamp_gmt
            sleep_start_timestamp_local = daily_sleep_dto.sleep_start_timestamp_local
            sleep_end_timestamp_local = daily_sleep_dto.sleep_end_timestamp_local
            movements: List[SleepMovement] = safe_list(movements)
            hrv_readings_data: List[HRVReading] = []
            if self.validate_data(hrv_data) and hasattr(hrv_data, "hrv_readings"):
                hrv_readings_data = safe_list(hrv_data.hrv_readings)

            # 타임스탬프를 datetime 객체로 변환
            try:
                start_time_gmt = datetime.fromtimestamp(
                    sleep_start_timestamp_gmt / 1000, timezone.utc
                )
                end_time_gmt = datetime.fromtimestamp(
                    sleep_end_timestamp_gmt / 1000, timezone.utc
                )
                start_time_local = datetime.fromtimestamp(
                    sleep_start_timestamp_local / 1000, timezone.utc
                ).replace(tzinfo=None)
                end_time_local = datetime.fromtimestamp(
                    sleep_end_timestamp_local / 1000, timezone.utc
                ).replace(tzinfo=None)
                local_diff = sleep_start_timestamp_local - sleep_start_timestamp_gmt
            except (ValueError, TypeError, OSError) as e:
                self.logger.error(f"날짜 변환 중 오류: {str(e)}")
                start_time_gmt = datetime.now(timezone.utc)
                end_time_gmt = datetime.now(timezone.utc)
                start_time_local = datetime.now().replace(tzinfo=None)
                end_time_local = datetime.now().replace(tzinfo=None)
                local_diff = 0

            # 수면 세션 생성
            sleep_session = SleepSession(
                user_id=user_id,
                date=target_date,
                start_time_gmt=start_time_gmt,
                end_time_gmt=end_time_gmt,
                start_time_local=start_time_local,
                end_time_local=end_time_local,
                total_seconds=daily_sleep_dto.sleep_time_seconds,
                deep_sleep_seconds=daily_sleep_dto.deep_sleep_seconds,
                light_sleep_seconds=daily_sleep_dto.light_sleep_seconds,
                rem_sleep_seconds=daily_sleep_dto.rem_sleep_seconds,
                awake_seconds=daily_sleep_dto.awake_sleep_seconds,
                avg_stress_level=daily_sleep_dto.avg_sleep_stress,
                avg_respiration=daily_sleep_dto.average_respiration_value,
                avg_spo2=daily_sleep_dto.average_sp_o2_value,
            )

            # HRV 데이터가 있는 경우 추가
            if self.validate_data(hrv_data):
                hrv_summary = safe_get(hrv_data, "hrv_summary", SleepHRV.hrv_summary)
                if self.validate_data(hrv_summary):
                    sleep_session.avg_hrv = hrv_summary.last_night_avg
                    sleep_session.hrv_weekly_avg = hrv_summary.weekly_avg
                    sleep_session.hrv_last_night_avg = hrv_summary.last_night_avg

                    sleep_session.hrv_last_night_5_min_high = (
                        hrv_summary.last_night_5_min_high
                    )
                    sleep_session.hrv_status = hrv_summary.status
                    sleep_session.hrv_feedback = hrv_summary.feedback_phrase

                    baseline = hrv_summary.baseline
                    if self.validate_data(baseline):
                        sleep_session.hrv_baseline_low_upper = baseline.low_upper
                        sleep_session.hrv_baseline_balanced_low = baseline.balanced_low
                        sleep_session.hrv_baseline_balanced_upper = (
                            baseline.balanced_upper
                        )
                        sleep_session.hrv_baseline_marker_value = baseline.marker_value

            # 수면 움직임 데이터 생성
            movement_readings = []
            if movements:
                for movement in movements:
                    try:
                        start_gmt = movement.start_gmt
                        end_gmt = movement.end_gmt
                        activity_level = movement.activity_level

                        if start_gmt is None or end_gmt is None:
                            continue

                        start_time_gmt = start_gmt.replace(tzinfo=timezone.utc)
                        interval = int((end_gmt - start_gmt).total_seconds())
                        start_time_local = start_time_gmt.replace(
                            tzinfo=None
                        ) + timedelta(milliseconds=local_diff)

                        movement_readings.append(
                            SleepMovementModel(
                                start_time_gmt=start_time_gmt,
                                start_time_local=start_time_local,
                                interval=interval,
                                activity_level=activity_level,
                                session=sleep_session,
                            )
                        )
                    except Exception as e:
                        self.log_mapping_error(e, {"movement": str(movement)})
                        continue

            # HRV 상세 데이터 생성
            hrv_readings = []
            if hrv_readings_data:
                for reading in hrv_readings_data:
                    try:
                        reading_time_gmt = reading.reading_time_gmt
                        reading_time_local = reading.reading_time_local
                        hrv_value = reading.hrv_value

                        if reading_time_gmt is None or reading_time_local is None:
                            continue

                        start_time_gmt = reading_time_gmt.replace(tzinfo=timezone.utc)
                        start_time_local = reading_time_local.replace(tzinfo=None)

                        hrv_readings.append(
                            SleepHRVReading(
                                start_time_gmt=start_time_gmt,
                                start_time_local=start_time_local,
                                hrv_value=hrv_value,
                                session=sleep_session,
                            )
                        )
                    except Exception as e:
                        self.log_mapping_error(e, {"reading": str(reading)})
                        continue

            return {
                "daily_summary": sleep_session,
                "movements": movement_readings,
                "hrv_readings": hrv_readings,
            }
        except Exception as e:
            self.log_mapping_error(
                e, {"user_id": user_id, "target_date": str(target_date)}
            )
            return None

    def delete_existing_data(self, user_id: int, target_date: date) -> None:
        """수면 데이터 삭제"""
        try:
            result = self.safe_session_execute(
                select(SleepSession).where(
                    SleepSession.user_id == user_id,
                    SleepSession.date == target_date,
                ),
                error_msg=f"수면 데이터 검색 실패 - User: {user_id}, Date: {target_date}",
            )
            sleep_session = result.scalar_one_or_none()

            if sleep_session:
                self.safe_session_execute(
                    delete(SleepMovementModel).where(
                        SleepMovementModel.sleep_session_id == sleep_session.id
                    ),
                    error_msg=f"수면 움직임 데이터 삭제 실패 - Session ID: {sleep_session.id}",
                )

                self.safe_session_execute(
                    delete(SleepHRVReading).where(
                        SleepHRVReading.sleep_session_id == sleep_session.id
                    ),
                    error_msg=f"수면 HRV 데이터 삭제 실패 - Session ID: {sleep_session.id}",
                )

                self.session.delete(sleep_session)
        except Exception as e:
            self.logger.error(
                f"수면 데이터 삭제 실패 - User: {user_id}, Date: {target_date}, Error: {str(e)}"
            )
            raise


class ActivityCollector(BaseDataCollector):
    """활동 데이터 수집기"""

    def fetch_data(self, date_str: str) -> Optional[List[Activity]]:
        all_activities = self.safe_get_cache(f"activities:{date_str}")
        if not self.validate_data(all_activities):
            self.logger.info(f"활동 데이터가 없습니다: {date_str}")
            return None

        try:
            target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            target_date_start = datetime.combine(target_date, datetime.min.time())
            target_date_end = datetime.combine(target_date, datetime.max.time())
            all_activities: List[Activity] = safe_list(all_activities)

            activities = []

            for activity in all_activities:
                if activity is None or not activity.start_time_local:
                    continue
                start_time_local = activity.start_time_local
                if (
                    start_time_local
                    and target_date_start <= start_time_local <= target_date_end
                ):
                    activities.append(activity)

            if not activities:
                self.logger.info(f"해당 날짜({date_str})의 활동이 없습니다.")
                return None

            return activities
        except Exception as e:
            self.logger.error(f"활동 데이터 필터링 중 오류 발생: {str(e)}")
            return None

    def map_data(
        self, user_id: int, target_date: date, activities: List[Activity]
    ) -> Dict[str, Any]:
        try:
            saved_activities = []
            activities: List[Activity] = safe_list(activities)

            if not activities:
                self.logger.info(f"해당 날짜({target_date})의 활동이 없습니다.")
                return {"activities": []}

            for activity_detail in activities:
                try:
                    if activity_detail is None:
                        continue

                    # 필수 데이터 확인
                    activity_id = activity_detail.activity_id
                    activity_type_obj = activity_detail.activity_type
                    start_time_gmt = activity_detail.start_time_gmt
                    start_time_local = activity_detail.start_time_local
                    duration = activity_detail.duration or 0.0
                    calories = activity_detail.calories or 0

                    if (
                        not start_time_gmt
                        or not start_time_local
                        or not activity_type_obj
                    ):
                        self.logger.info(
                            f"활동 필수 데이터 누락: {activity_id} 데이터: {start_time_gmt}, {start_time_local}, {activity_type_obj}"
                        )
                        continue

                    # 추가 데이터 안전하게 추출
                    activity_type_key = activity_detail.activity_type.type_key
                    distance = activity_detail.distance
                    average_hr = activity_detail.average_hr
                    max_hr = activity_detail.max_hr
                    average_speed = activity_detail.average_speed
                    elevation_gain = activity_detail.elevation_gain

                    # 종료 시간 계산
                    end_time_utc = start_time_gmt + timedelta(seconds=int(duration))
                    end_time_local = start_time_local + timedelta(seconds=int(duration))

                    # 활동 저장
                    activity = ActivityModel(
                        id=activity_id,
                        user_id=user_id,
                        activity_type=activity_type_key,
                        start_time_utc=start_time_gmt,
                        start_time_local=start_time_local,
                        end_time_utc=end_time_utc,
                        end_time_local=end_time_local,
                        distance=distance,
                        duration_seconds=int(duration),
                        calories=calories,
                        avg_heart_rate=average_hr,
                        max_heart_rate=max_hr,
                        avg_speed=average_speed,
                        elevation_gain=elevation_gain,
                        training_effect=None,
                    )
                    saved_activities.append(activity)
                except Exception as e:
                    self.log_mapping_error(
                        e,
                        {"activity_id": activity_detail.activity_id or "unknown"},
                    )
                    continue

            return {"activities": saved_activities}
        except Exception as e:
            self.log_mapping_error(
                e, {"user_id": user_id, "target_date": str(target_date)}
            )
            return {"activities": []}

    def delete_existing_data(self, user_id: int, target_date: date) -> None:
        """활동 데이터 삭제"""
        try:
            self.safe_session_execute(
                delete(ActivityModel).where(
                    func.date(ActivityModel.start_time_local) == target_date,
                    ActivityModel.user_id == user_id,
                ),
                error_msg=f"활동 데이터 삭제 실패 - User: {user_id}, Date: {target_date}",
            )
            self.session.commit()
        except Exception as e:
            self.logger.error(
                f"활동 데이터 삭제 실패 - User: {user_id}, Date: {target_date}, Error: {str(e)}"
            )
            self.session.rollback()
            raise


class DataCollectionError(Exception):
    """데이터 수집 중 발생하는 예외"""

    def __init__(self, message: str, error_type: str = "GENERAL", details: dict = None):
        self.message = message
        self.error_type = error_type
        self.details = details or {}
        super().__init__(self.message)


class DataFetchError(DataCollectionError):
    """데이터 가져오기 실패 예외"""

    def __init__(self, message: str, details: dict = None):
        super().__init__(message, "FETCH_ERROR", details)


class DataMappingError(DataCollectionError):
    """데이터 매핑 실패 예외"""

    def __init__(self, message: str, details: dict = None):
        super().__init__(message, "MAPPING_ERROR", details)


class DataValidationError(DataCollectionError):
    """데이터 유효성 검증 실패 예외"""

    def __init__(self, message: str, details: dict = None):
        super().__init__(message, "VALIDATION_ERROR", details)


class DataStorageError(DataCollectionError):
    """데이터 저장 실패 예외"""

    def __init__(self, message: str, details: dict = None):
        super().__init__(message, "STORAGE_ERROR", details)


class GarminDataCollectorService(BaseGarminService):
    """
    Garmin 데이터 수집 서비스
    - 일일 데이터 수집 및 DB 저장
    - 분석용 데이터 적재
    - 배치 작업으로 실행
    """

    def __init__(self, client, session: Session):
        super().__init__(client)
        self.session = session
        self._data_cache: Dict[str, CacheData] = {}

    def _get_cache_key(self, endpoint: str, date_str: str) -> str:
        """캐시 키 생성"""
        return f"{endpoint}:{date_str}"

    def _fetch_with_cache(self, endpoint: str, date_str: str, fetch_func) -> Any:
        """
        새로운 데이터를 가져와서 캐시에 저장
        """
        cache_key = self._get_cache_key(endpoint, date_str)
        if cache_key in self._data_cache:
            logger.debug(f"캐시된 데이터 사용: {cache_key}")
            return self._data_cache[cache_key]

        try:
            data = fetch_func(date_str, client=self.client)
            if data:
                self._data_cache[cache_key] = data
                logger.info(f"데이터 가져오기 성공: {cache_key}")
            else:
                logger.info(f"가져온 데이터가 없음: {cache_key}")
            return data
        except Exception as e:
            error_msg = f"{endpoint} 데이터 가져오기 실패: {str(e)}"
            logger.error(error_msg)
            # 오류 유형 식별
            error_type = "UNKNOWN"
            if "validation error" in str(e).lower():
                error_type = "VALIDATION_ERROR"
            elif "not found" in str(e).lower() or "404" in str(e):
                error_type = "NOT_FOUND"
            elif "timeout" in str(e).lower():
                error_type = "TIMEOUT"
            elif "permission" in str(e).lower() or "401" in str(e) or "403" in str(e):
                error_type = "PERMISSION_ERROR"

            raise DataFetchError(
                error_msg,
                details={
                    "endpoint": endpoint,
                    "date": date_str,
                    "error_type": error_type,
                    "error_message": str(e),
                },
            )

    def _prefetch_data(self, date_str: str) -> None:
        """
        필요한 데이터를 미리 가져와서 캐시
        """
        try:
            # 일일 요약 데이터
            self._fetch_with_cache(
                "daily_summary",
                date_str,
                lambda date_str, client: DailySummary.get(date_str, client=client),
            )

            # 심박수 데이터
            self._fetch_with_cache(
                "heart_rate",
                date_str,
                lambda date_str, client: HeartRate.get(date_str, client=client),
            )

            # 스트레스 데이터
            self._fetch_with_cache(
                "stress",
                date_str,
                lambda date_str, client: Stress.get(date_str, client=client),
            )

            # 걸음수 데이터
            self._fetch_with_cache(
                "steps_data",
                date_str,
                lambda date_str, client: StepsValue.get_readings(
                    date_str, client=client
                ),
            )

            # 수면 데이터
            sleep_data = self._fetch_with_cache(
                "sleep_data",
                date_str,
                lambda date_str, client: SleepData.get(date_str, client=client),
            )
            if sleep_data:
                self._fetch_with_cache(
                    "sleep_hrv",
                    date_str,
                    lambda date_str, client: SleepHRV.get(date_str, client=client),
                )

            # 활동 데이터
            self._fetch_with_cache(
                "activities",
                date_str,
                lambda date_str, client: Activity.list(50, 0, client=client),
            )

        except DataFetchError as e:
            logger.error(f"데이터 프리페치 실패: {str(e)}")
            raise DataCollectionError(
                f"데이터 프리페치 실패: {str(e)}",
                error_type="PREFETCH_ERROR",
                details={"date": date_str},
            )
        except Exception as e:
            logger.error(f"데이터 프리페치 중 예상치 못한 오류: {str(e)}")
            raise DataCollectionError(
                f"데이터 프리페치 중 예상치 못한 오류: {str(e)}",
                error_type="PREFETCH_ERROR",
                details={"date": date_str, "error_type": type(e).__name__},
            )

    def _collect_with_collector(
        self,
        collector: BaseDataCollector,
        user_id: int,
        target_date: date,
        date_str: str,
    ) -> Optional[Any]:
        """
        컬렉터를 사용하여 데이터 수집
        """
        collector_name = collector.__class__.__name__
        try:
            # 데이터 가져오기
            data = collector.fetch_data(date_str)
            if not data:
                return None

            # 데이터 매핑
            mapped_data = collector.map_data(user_id, target_date, data)
            if not mapped_data:
                logger.warning(f"{collector_name} 데이터 매핑 실패")
                raise DataMappingError(
                    f"{collector_name} 데이터 매핑 실패",
                    details={
                        "collector": collector_name,
                        "date": date_str,
                    },
                )

            # 기존 데이터 삭제
            try:
                collector.delete_existing_data(user_id, target_date)
            except Exception as e:
                logger.error(f"{collector_name} 기존 데이터 삭제 실패: {str(e)}")
                self.session.rollback()
                raise DataStorageError(
                    f"{collector_name} 기존 데이터 삭제 실패: {str(e)}",
                    details={
                        "collector": collector_name,
                        "date": date_str,
                    },
                )

            # 데이터 저장
            try:
                if isinstance(mapped_data, dict):
                    if "activities" in mapped_data:
                        activities = safe_list(
                            safe_get_item(mapped_data, "activities", [])
                        )
                        for activity in activities:
                            if activity:
                                self.session.add(activity)
                    else:
                        for key, model in mapped_data.items():
                            if isinstance(model, list):
                                for item in safe_list(model):
                                    if item:
                                        self.session.add(item)
                            elif model:
                                self.session.add(model)
                elif mapped_data:
                    self.session.add(mapped_data)

                self.session.commit()
                return f"{collector_name} 데이터 저장 성공"
            except Exception as e:
                self.session.rollback()
                raise DataStorageError(
                    f"{collector_name} 데이터 저장 실패: {str(e)}",
                    details={
                        "collector": collector_name,
                        "date": date_str,
                    },
                )

        except (DataFetchError, DataMappingError, DataStorageError) as e:
            raise e
        except Exception as e:
            logger.error(f"{collector_name} 데이터 수집 실패: {str(e)}")
            raise DataCollectionError(
                f"{collector_name} 데이터 수집 실패: {str(e)}",
                details={"collector": collector_name, "date": date_str},
            )

    def collect_daily_data(self, user_id: int, target_date: date) -> Dict[str, Any]:
        """
        일일 데이터 수집
        """
        date_str = target_date.strftime("%Y-%m-%d")
        logger.info(f"사용자 {user_id}의 {date_str} 데이터 수집 시작")

        try:
            # 미리 데이터 가져오기
            self._prefetch_data(date_str)

            # 각 컬렉터로 데이터 수집
            collectors = [
                HeartRateCollector(self.client, self._data_cache, self.session),
                StressCollector(self.client, self._data_cache, self.session),
                StepsCollector(self.client, self._data_cache, self.session),
                SleepCollector(self.client, self._data_cache, self.session),
                ActivityCollector(self.client, self._data_cache, self.session),
            ]

            results = {}
            errors = []

            for collector in collectors:
                collector_name = collector.__class__.__name__
                try:
                    result = self._collect_with_collector(
                        collector, user_id, target_date, date_str
                    )
                    if result:
                        results[collector_name] = result
                        logger.info(f"{collector_name} 데이터 수집 완료")
                except Exception as e:
                    logger.error(f"{collector_name} 데이터 수집 실패: {str(e)}")
                    errors.append(f"{collector_name}: {str(e)}")
                    # 에러가 발생해도 다른 컬렉터는 계속 실행

            # 결과 검증 및 오류 처리
            if not results and errors:
                error_msg = f"모든 데이터 수집 시도 실패: {'; '.join(errors)}"
                logger.error(error_msg)
                raise DataCollectionError(
                    error_msg,
                    details={"user_id": user_id, "date": date_str, "errors": errors},
                )
            elif not results:
                error_msg = "수집된 데이터가 없습니다"
                logger.warning(error_msg)
                raise DataValidationError(
                    error_msg,
                    details={"user_id": user_id, "date": date_str},
                )
            elif errors:
                # 일부 성공, 일부 실패
                logger.warning(
                    f"일부 데이터 수집 실패 ({len(errors)}개): {'; '.join(errors)}"
                )
                # 오류를 결과에 포함
                results["errors"] = errors

            logger.info(
                f"사용자 {user_id}의 {date_str} 데이터 수집 완료 - 성공: {len(results) - ('errors' in results)}, 실패: {len(errors)}"
            )
            return results

        except (
            DataFetchError,
            DataMappingError,
            DataStorageError,
            DataValidationError,
        ) as e:
            # 이미 적절한 예외 타입이면 그대로 전달
            raise e
        except Exception as e:
            # 예상치 못한 오류
            error_msg = f"데이터 수집 중 예상치 못한 오류: {str(e)}"
            logger.error(f"{error_msg}\n{traceback.format_exc()}")
            raise DataCollectionError(
                error_msg,
                details={
                    "user_id": user_id,
                    "date": date_str,
                    "error_type": type(e).__name__,
                },
            )
