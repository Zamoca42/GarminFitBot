import asyncio
import logging
from datetime import date, datetime, timedelta, timezone
from typing import Any, Dict, Generic, List, Optional, TypeAlias, TypeVar, Union

from garth import DailyHRV, SleepData
from garth.data.sleep import SleepMovement
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain import (
    Activity,
    DailySummary,
    HeartRate,
    SleepHRV,
    StepsValue,
    Stress,
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

    def __init__(self, client, data_cache: Dict[str, CacheData], session: AsyncSession):
        self.client = client
        self.data_cache = data_cache
        self.session = session

    async def fetch_data(self, date_str: str) -> Optional[D]:
        """API에서 데이터 가져오기"""
        raise NotImplementedError

    async def map_data(self, user_id: int, target_date: date, data: D) -> Optional[M]:
        """데이터 매핑"""
        raise NotImplementedError

    async def delete_existing_data(self, user_id: int, target_date: date) -> None:
        """기존 데이터 삭제"""
        raise NotImplementedError


class HeartRateCollector(BaseDataCollector):
    """심박수 데이터 수집기"""

    async def fetch_data(
        self, date_str: str
    ) -> Optional[Dict[str, Union[HeartRate, SleepHRV, DailyHRV]]]:
        heart_rate_data = self.data_cache.get(f"heart_rate:{date_str}")

        return {
            "heart_rate_data": heart_rate_data,
        }

    async def map_data(
        self,
        user_id: int,
        target_date: date,
        data: Dict[str, Union[HeartRate, SleepHRV, DailyHRV]],
    ) -> Optional[HeartRateDaily]:
        heart_rate_data = data["heart_rate_data"]

        avg_heart_rate = None
        if (
            hasattr(heart_rate_data, "heart_rate_values")
            and heart_rate_data.heart_rate_values
        ):
            valid_readings = [
                r.heart_rate
                for r in heart_rate_data.heart_rate_values
                if r.heart_rate is not None
            ]
            if valid_readings:
                avg_heart_rate = sum(valid_readings) / len(valid_readings)

        daily_summary = HeartRateDaily(
            user_id=user_id,
            date=target_date,
            resting_hr=heart_rate_data.resting_heart_rate,
            max_hr=heart_rate_data.max_heart_rate,
            min_hr=heart_rate_data.min_heart_rate,
            avg_hr=avg_heart_rate,
        )

        readings: List[HeartRateReading] = []
        for reading in heart_rate_data.heart_rate_values:
            readings.append(
                HeartRateReading(
                    start_time_gmt=reading.start_time_gmt,
                    start_time_local=reading.start_time_gmt.replace(tzinfo=None)
                    + timedelta(seconds=heart_rate_data.local_offset),
                    heart_rate=reading.heart_rate,
                    daily_summary=daily_summary,
                )
            )

        return {
            "daily_summary": daily_summary,
            "readings": readings,
        }

    async def delete_existing_data(self, user_id: int, target_date: date) -> None:
        """심박수 데이터 삭제"""
        try:
            result = await self.session.execute(
                select(HeartRateDaily).where(
                    HeartRateDaily.user_id == user_id,
                    HeartRateDaily.date == target_date,
                )
            )
            daily_summary = result.scalar_one_or_none()

            if daily_summary:
                await self.session.execute(
                    delete(HeartRateReading).where(
                        HeartRateReading.daily_summary_id == daily_summary.id,
                    )
                )
                await self.session.delete(daily_summary)
        except Exception as e:
            logger.error(
                f"심박수 데이터 삭제 실패 - User: {user_id}, Date: {target_date}, Error: {str(e)}"
            )
            await self.session.rollback()
            raise


class StressCollector(BaseDataCollector):
    """스트레스 데이터 수집기"""

    async def fetch_data(
        self, date_str: str
    ) -> Optional[Dict[str, Union[Stress, DailySummary]]]:
        stress_data = self.data_cache.get(f"stress:{date_str}")
        daily_summary = self.data_cache.get(f"daily_summary:{date_str}")

        if not stress_data or not daily_summary:
            return None

        return {"stress_data": stress_data, "daily_summary": daily_summary}

    async def map_data(
        self,
        user_id: int,
        target_date: date,
        data: Dict[str, Union[Stress, DailySummary]],
    ) -> Optional[Dict[str, Any]]:
        stress_data: Stress = data["stress_data"]
        daily_summary: DailySummary = data["daily_summary"]

        daily_summary_data = StressDaily(
            user_id=user_id,
            date=target_date,
            avg_stress_level=stress_data.avg_stress_level,
            max_stress_level=stress_data.max_stress_level,
            stress_duration_seconds=daily_summary.stress_duration,
            rest_duration_seconds=daily_summary.rest_stress_duration,
        )

        local_offset = daily_summary.local_offset

        # 상세 측정값 저장
        readings = []
        for reading in stress_data.stress_values:
            readings.append(
                StressReading(
                    start_time_gmt=reading.start_time_gmt,
                    start_time_local=reading.start_time_gmt.replace(tzinfo=None)
                    + timedelta(seconds=local_offset),
                    stress_level=reading.stress_level,
                    daily_summary=daily_summary_data,
                )
            )

        return {
            "daily_summary": daily_summary_data,
            "readings": readings,
        }

    async def delete_existing_data(self, user_id: int, target_date: date) -> None:
        """스트레스 데이터 삭제"""
        try:
            result = await self.session.execute(
                select(StressDaily).where(
                    StressDaily.user_id == user_id,
                    StressDaily.date == target_date,
                )
            )
            daily_summary = result.scalar_one_or_none()

            if daily_summary:
                await self.session.execute(
                    delete(StressReading).where(
                        StressReading.daily_summary_id == daily_summary.id,
                    )
                )
                await self.session.delete(daily_summary)
        except Exception as e:
            logger.error(
                f"스트레스 데이터 삭제 실패 - User: {user_id}, Date: {target_date}, Error: {str(e)}"
            )
            await self.session.rollback()
            raise


class StepsCollector(BaseDataCollector):
    """걸음수 데이터 수집기"""

    async def fetch_data(
        self, date_str: str
    ) -> Optional[Dict[str, Union[DailySummary, List[StepsValue]]]]:
        daily_summary_data = self.data_cache.get(f"daily_summary:{date_str}")
        steps_data = self.data_cache.get(f"steps_data:{date_str}")

        if not daily_summary_data:
            return None

        return {"daily_summary": daily_summary_data, "steps_data": steps_data}

    async def map_data(
        self,
        user_id: int,
        target_date: date,
        data: Dict[str, Union[DailySummary, List[StepsValue]]],
    ) -> Optional[StepsDaily]:
        daily_summary_data = data["daily_summary"]
        steps_data: List[StepsValue] = data["steps_data"]

        # 정수 변환 처리
        floors_climbed = (
            int(daily_summary_data.floors_ascended)
            if hasattr(daily_summary_data, "floors_ascended")
            else 0
        )

        local_offset = daily_summary_data.local_offset

        daily_summary = StepsDaily(
            user_id=user_id,
            date=target_date,
            total_steps=daily_summary_data.total_steps,
            goal_steps=daily_summary_data.daily_step_goal,
            distance=daily_summary_data.total_distance_meters / 1000,  # m -> km 변환
            calories=daily_summary_data.active_kilocalories,
            active_minutes=daily_summary_data.highly_active_seconds // 60
            + daily_summary_data.active_seconds // 60,
            floors_climbed=floors_climbed,
        )

        # 상세 측정값 저장 (있는 경우)
        readings = []
        if steps_data:
            for reading in steps_data:
                start_time_gmt = reading.start_time_gmt
                end_time_gmt = reading.end_time_gmt
                start_time_local = reading.start_time_gmt.replace(
                    tzinfo=None
                ) + timedelta(seconds=local_offset)
                end_time_local = reading.end_time_gmt.replace(tzinfo=None) + timedelta(
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
                        intensity=0,  # 기본값 설정
                        daily_summary=daily_summary,
                    )
                )

        return {
            "daily_summary": daily_summary,
            "readings": readings,
        }

    async def delete_existing_data(self, user_id: int, target_date: date) -> None:
        """걸음수 데이터 삭제"""
        try:
            result = await self.session.execute(
                select(StepsDaily).where(
                    StepsDaily.user_id == user_id,
                    StepsDaily.date == target_date,
                )
            )
            daily_summary = result.scalar_one_or_none()

            if daily_summary:
                await self.session.execute(
                    delete(StepsIntraday).where(
                        StepsIntraday.daily_summary_id == daily_summary.id,
                    )
                )
                await self.session.delete(daily_summary)
        except Exception as e:
            logger.error(
                f"걸음수 데이터 삭제 실패 - User: {user_id}, Date: {target_date}, Error: {str(e)}"
            )
            await self.session.rollback()
            raise


class SleepCollector(BaseDataCollector):
    """수면 데이터 수집기"""

    async def fetch_data(
        self, date_str: str
    ) -> Optional[Dict[str, Union[SleepData, SleepHRV, List[SleepMovement]]]]:
        # 캐시된 데이터 사용
        sleep_data = self.data_cache.get(f"sleep_data:{date_str}")
        hrv_data = self.data_cache.get(f"sleep_hrv:{date_str}")

        if not sleep_data:
            return None

        return {
            "sleep_data": sleep_data,
            "hrv_data": hrv_data,
            "movements": (
                sleep_data.sleep_movement
                if hasattr(sleep_data, "sleep_movement")
                else []
            ),
        }

    async def map_data(
        self,
        user_id: int,
        target_date: date,
        data: Dict[str, Union[SleepData, SleepHRV, List[SleepMovement]]],
    ) -> Optional[Dict[str, Any]]:
        sleep_data: SleepData = data["sleep_data"]
        hrv_data: SleepHRV = data["hrv_data"]
        movements: List[SleepMovement] = data["movements"]

        sleep_start_timestamp_gmt = sleep_data.daily_sleep_dto.sleep_start_timestamp_gmt
        sleep_start_timestamp_local = (
            sleep_data.daily_sleep_dto.sleep_start_timestamp_local
        )

        # 타임스탬프를 datetime 객체로 변환하고 타임존 정보 제거
        start_time_gmt = datetime.fromtimestamp(
            sleep_start_timestamp_gmt / 1000, timezone.utc
        )
        end_time_gmt = datetime.fromtimestamp(
            sleep_data.daily_sleep_dto.sleep_end_timestamp_gmt / 1000, timezone.utc
        )
        start_time_local = datetime.fromtimestamp(
            sleep_start_timestamp_local / 1000, timezone.utc
        ).replace(tzinfo=None)
        end_time_local = datetime.fromtimestamp(
            sleep_data.daily_sleep_dto.sleep_end_timestamp_local / 1000, timezone.utc
        ).replace(tzinfo=None)
        local_diff = sleep_start_timestamp_local - sleep_start_timestamp_gmt

        # 수면 세션 생성
        sleep_session = SleepSession(
            user_id=user_id,
            date=target_date,
            start_time_gmt=start_time_gmt,
            end_time_gmt=end_time_gmt,
            start_time_local=start_time_local,
            end_time_local=end_time_local,
            total_seconds=sleep_data.daily_sleep_dto.sleep_time_seconds,
            deep_sleep_seconds=sleep_data.daily_sleep_dto.deep_sleep_seconds,
            light_sleep_seconds=sleep_data.daily_sleep_dto.light_sleep_seconds,
            rem_sleep_seconds=sleep_data.daily_sleep_dto.rem_sleep_seconds,
            awake_seconds=sleep_data.daily_sleep_dto.awake_sleep_seconds,
            avg_stress_level=sleep_data.daily_sleep_dto.avg_sleep_stress,
            avg_respiration=sleep_data.daily_sleep_dto.average_respiration_value,
            avg_spo2=sleep_data.daily_sleep_dto.average_sp_o2_value,
        )

        # HRV 데이터가 있는 경우 추가
        if hrv_data and hasattr(hrv_data, "hrv_summary") and hrv_data.hrv_summary:
            sleep_session.avg_hrv = hrv_data.hrv_summary.last_night_avg
            sleep_session.hrv_weekly_avg = hrv_data.hrv_summary.weekly_avg
            sleep_session.hrv_last_night_avg = hrv_data.hrv_summary.last_night_avg
            sleep_session.hrv_last_night_5_min_high = (
                hrv_data.hrv_summary.last_night_5_min_high
            )
            sleep_session.hrv_status = hrv_data.hrv_summary.status
            sleep_session.hrv_feedback = hrv_data.hrv_summary.feedback_phrase

            if hrv_data.hrv_summary.baseline:
                sleep_session.hrv_baseline_low_upper = (
                    hrv_data.hrv_summary.baseline.low_upper
                )
                sleep_session.hrv_baseline_balanced_low = (
                    hrv_data.hrv_summary.baseline.balanced_low
                )
                sleep_session.hrv_baseline_balanced_upper = (
                    hrv_data.hrv_summary.baseline.balanced_upper
                )
                sleep_session.hrv_baseline_marker_value = (
                    hrv_data.hrv_summary.baseline.marker_value
                )

        # 수면 움직임 데이터 생성
        movement_readings: List[SleepMovementModel] = []
        for movement in movements:

            start_time_gmt = movement.start_gmt.replace(tzinfo=timezone.utc)
            start_time_local = start_time_gmt.replace(tzinfo=None) + timedelta(
                milliseconds=local_diff
            )

            movement_readings.append(
                SleepMovementModel(
                    start_time_gmt=start_time_gmt,
                    start_time_local=start_time_local,
                    interval=int(
                        (movement.end_gmt - movement.start_gmt).total_seconds()
                    ),
                    activity_level=movement.activity_level,
                    session=sleep_session,
                )
            )

        # HRV 상세 데이터 생성
        hrv_readings = []
        for reading in hrv_data.hrv_readings:
            start_time_gmt = reading.reading_time_gmt.replace(tzinfo=timezone.utc)
            start_time_local = reading.reading_time_local.replace(tzinfo=None)

            hrv_readings.append(
                SleepHRVReading(
                    start_time_gmt=start_time_gmt,
                    start_time_local=start_time_local,
                    hrv_value=reading.hrv_value,
                    session=sleep_session,
                )
            )

        return {
            "daily_summary": sleep_session,
            "movements": movement_readings,
            "hrv_readings": hrv_readings,
        }

    async def delete_existing_data(self, user_id: int, target_date: date) -> None:
        """수면 데이터 삭제"""
        try:
            result = await self.session.execute(
                select(SleepSession).where(
                    SleepSession.user_id == user_id,
                    SleepSession.date == target_date,
                )
            )
            sleep_session = result.scalar_one_or_none()

            if sleep_session:
                await self.session.execute(
                    delete(SleepMovementModel).where(
                        SleepMovementModel.sleep_session_id == sleep_session.id
                    )
                )

                await self.session.execute(
                    delete(SleepHRVReading).where(
                        SleepHRVReading.sleep_session_id == sleep_session.id
                    )
                )

                await self.session.delete(sleep_session)
        except Exception as e:
            logger.error(
                f"수면 데이터 삭제 실패 - User: {user_id}, Date: {target_date}, Error: {str(e)}"
            )
            raise


class ActivityCollector(BaseDataCollector):
    """활동 데이터 수집기"""

    async def fetch_data(self, date_str: str) -> Optional[List[Activity]]:
        all_activities = self.data_cache.get(f"activities:{date_str}")
        if not all_activities:
            return None

        target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        target_date_start = datetime.combine(target_date, datetime.min.time())
        target_date_end = datetime.combine(target_date, datetime.max.time())
        activities = [
            activity
            for activity in all_activities
            if target_date_start <= activity.start_time_local <= target_date_end
        ]

        if not activities:
            return None

        return activities

    async def map_data(
        self, user_id: int, target_date: date, activities: List[Activity]
    ) -> Dict[str, Any]:
        saved_activities = []

        for activity_detail in activities:
            # 종료 시간 계산
            end_time_utc = activity_detail.start_time_utc + timedelta(
                seconds=int(activity_detail.duration)
            )
            end_time_local = activity_detail.start_time_local + timedelta(
                seconds=int(activity_detail.duration)
            )

            # 활동 저장
            activity = ActivityModel(
                id=activity_detail.activity_id,
                user_id=user_id,
                activity_type=activity_detail.activity_type.type_key,
                start_time_utc=activity_detail.start_time_utc,
                start_time_local=activity_detail.start_time_local,
                end_time_utc=end_time_utc,
                end_time_local=end_time_local,
                distance=getattr(activity_detail, "distance", None),
                duration_seconds=int(activity_detail.duration),
                calories=activity_detail.calories,
                avg_heart_rate=getattr(activity_detail, "average_hr", None),
                max_heart_rate=getattr(activity_detail, "max_hr", None),
                avg_speed=getattr(activity_detail, "average_speed", None),
                elevation_gain=getattr(activity_detail, "elevation_gain", None),
                training_effect=None,
            )
            saved_activities.append(activity)

        return {"activities": saved_activities}

    async def delete_existing_data(self, user_id: int, target_date: date) -> None:
        """활동 데이터 삭제"""
        try:
            await self.session.execute(
                delete(ActivityModel).where(
                    func.date(ActivityModel.start_time_local) == target_date,
                )
            )
            await self.session.commit()
        except Exception as e:
            logger.error(
                f"활동 데이터 삭제 실패 - User: {user_id}, Date: {target_date}, Error: {str(e)}"
            )
            raise


class GarminDataCollectorService(BaseGarminService):
    """
    Garmin 데이터 수집 서비스
    - 일일 데이터 수집 및 DB 저장
    - 분석용 데이터 적재
    - 배치 작업으로 실행
    """

    def __init__(self, client, session: AsyncSession):
        super().__init__(client)
        self.session = session
        self._data_cache: Dict[str, CacheData] = {}

    def _get_cache_key(self, endpoint: str, date_str: str) -> str:
        """캐시 키 생성"""
        return f"{endpoint}:{date_str}"

    async def _fetch_with_cache(self, endpoint: str, date_str: str, fetch_func) -> Any:
        """
        새로운 데이터를 가져와서 캐시에 저장

        Args:
            endpoint: API 엔드포인트
            date_str: 날짜 문자열
            fetch_func: 데이터 가져오는 함수
        """
        cache_key = self._get_cache_key(endpoint, date_str)

        try:
            # 비동기 함수인 경우 await 사용
            if asyncio.iscoroutinefunction(fetch_func):
                data = await fetch_func(date_str, client=self.client)
            else:
                # 동기 함수인 경우 직접 호출
                data = fetch_func(date_str, client=self.client)

            if data:
                self._data_cache[cache_key] = data
                logger.info(f"데이터 가져오기 성공: {cache_key}")
            return data
        except Exception as e:
            logger.error(f"데이터 가져오기 실패: {cache_key}, Error: {str(e)}")
            return None

    async def _prefetch_data(self, date_str: str) -> None:
        """
        필요한 모든 데이터를 미리 가져와서 캐시에 저장
        """
        try:
            sync_time = self.client.connectapi(
                "/wellness-service/wellness/syncTimestamp"
            )
            if not sync_time:
                raise ValueError("동기화 시간을 가져올 수 없습니다")

            try:
                if isinstance(sync_time, str):
                    sync_datetime = datetime.fromisoformat(
                        sync_time.replace("Z", "+00:00")
                    )
                else:
                    sync_datetime = datetime.fromtimestamp(
                        int(sync_time) / 1000, timezone.utc
                    )
                logger.info(f"변환된 동기화 시간: {sync_datetime}")
            except (ValueError, TypeError) as e:
                raise ValueError(f"동기화 시간 변환 실패: {str(e)}")

            target_date = datetime.strptime(date_str, "%Y-%m-%d").date()

            # 동기화 시간이 대상 날짜보다 이전이면 예외 발생
            if sync_datetime.date() < target_date:
                raise ValueError(
                    f"기기 동기화 시간({sync_datetime.date()})이 대상 날짜({target_date})보다 이전입니다"
                )

            logger.info("데이터 가져오기 시작")
            tasks = [
                self._fetch_with_cache("daily_summary", date_str, DailySummary.get),
                self._fetch_with_cache("heart_rate", date_str, HeartRate.get),
                self._fetch_with_cache("stress", date_str, Stress.get),
                self._fetch_with_cache("steps_data", date_str, StepsValue.get_readings),
                self._fetch_with_cache(
                    "activities",
                    date_str,
                    lambda date_str, client: Activity.list(50, 0, client=client),
                ),
            ]

            sleep_data = await self._fetch_with_cache(
                "sleep_data", date_str, SleepData.get
            )
            if sleep_data:
                await self._fetch_with_cache("sleep_hrv", date_str, SleepHRV.get)
            else:
                logger.info("수면 데이터 없음")

            await asyncio.gather(*tasks)
            logger.info("데이터 가져오기 완료")

        except Exception as e:
            logger.error(f"데이터 프리페치 실패: {str(e)}")
            raise

    async def _collect_with_collector(
        self,
        collector: BaseDataCollector,
        user_id: int,
        target_date: date,
        date_str: str,
    ) -> Optional[Any]:
        try:
            data = await collector.fetch_data(date_str)
            if not data:
                logger.warning(
                    f"{collector.__class__.__name__}에서 데이터를 가져오지 못함"
                )
                return None

            mapped_data = await collector.map_data(user_id, target_date, data)
            if not mapped_data:
                logger.warning(f"{collector.__class__.__name__}에서 데이터 매핑 실패")
                return None

            await collector.delete_existing_data(user_id, target_date)

            if isinstance(mapped_data, dict):
                if "daily_summary" in mapped_data:
                    self.session.add(mapped_data["daily_summary"])
                if "movements" in mapped_data:
                    self.session.add_all(mapped_data["movements"])
                if "readings" in mapped_data:
                    self.session.add_all(mapped_data["readings"])
                if "hrv_readings" in mapped_data:
                    self.session.add_all(mapped_data["hrv_readings"])
                if "activities" in mapped_data:
                    self.session.add_all(mapped_data["activities"])
            else:
                self.session.add(mapped_data)

            await self.session.flush()
            await self.session.commit()

            return mapped_data

        except Exception as e:
            await self.session.rollback()
            logger.error(f"{collector.__class__.__name__} 데이터 수집 실패: {str(e)}")
            raise

    async def collect_daily_data(
        self, user_id: int, target_date: date
    ) -> Dict[str, Any]:
        logger.info("데이터 수집 시작 - User: %d, Date: %s", user_id, target_date)
        date_str = target_date.strftime("%Y-%m-%d")

        try:
            await self._prefetch_data(date_str)

            heart_rate_collector = HeartRateCollector(
                self.client, self._data_cache, self.session
            )
            stress_collector = StressCollector(
                self.client, self._data_cache, self.session
            )
            steps_collector = StepsCollector(
                self.client, self._data_cache, self.session
            )
            sleep_collector = SleepCollector(
                self.client, self._data_cache, self.session
            )
            activity_collector = ActivityCollector(
                self.client, self._data_cache, self.session
            )

            result = {}
            collectors = [
                ("heart_rate", heart_rate_collector),
                ("stress", stress_collector),
                ("steps", steps_collector),
                ("sleep", sleep_collector),
                ("activities", activity_collector),
            ]

            for key, collector in collectors:
                try:
                    data = await self._collect_with_collector(
                        collector, user_id, target_date, date_str
                    )
                    if data:
                        result[key] = data
                except Exception as e:
                    logger.error(f"{key} 데이터 수집 실패: {str(e)}")
                    continue

            return result

        except Exception as e:
            logger.error(
                f"데이터 수집 실패 - User: {user_id}, Date: {target_date}, Error: {str(e)}"
            )
            raise
