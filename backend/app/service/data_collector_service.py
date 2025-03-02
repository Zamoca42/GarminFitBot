import logging
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional, Any

from sqlalchemy import select, delete

from app.model import (
    HeartRateDaily,
    HeartRateReading,
    StressDaily,
    StressReading,
    StepsDaily,
    StepsIntraday,
    SleepSession,
    SleepMovement,
    SleepHRVReading,
    Activity,
)
from app.service._base_service import BaseGarminService
from core.db.session import session

logger = logging.getLogger(__name__)


class GarminDataCollectorService(BaseGarminService):
    """
    Garmin 데이터 수집 서비스
    - 일일 데이터 수집 및 DB 저장
    - 분석용 데이터 적재
    - 배치 작업으로 실행
    """

    async def collect_daily_data(self, user_id: int, target_date: date) -> Dict[str, Any]:
        """특정 날짜의 모든 데이터 수집"""
        logger.info("데이터 수집 시작 - User: %d, Date: %s", user_id, target_date)
        date_str = target_date.strftime("%Y-%m-%d")

        try:
            # 1. 심박수 데이터 수집
            heart_rate_data = await self._collect_heart_rate(user_id, target_date, date_str)

            # 2. 스트레스 데이터 수집
            stress_data = await self._collect_stress(user_id, target_date, date_str)

            # 3. 걸음수 데이터 수집
            steps_data = await self._collect_steps(user_id, target_date, date_str)

            # 4. 수면 데이터 수집
            sleep_data = await self._collect_sleep(user_id, target_date, date_str)

            # 5. 활동 데이터 수집
            activity_data = await self._collect_activities(user_id, target_date, date_str)

            return {
                "heart_rate": heart_rate_data,
                "stress": stress_data,
                "steps": steps_data,
                "sleep": sleep_data,
                "activities": activity_data,
            }

        except Exception as e:
            logger.error(
                "데이터 수집 실패 - User: %d, Date: %s, Error: %s",
                user_id,
                target_date,
                str(e),
            )
            await session.rollback()
            raise

    async def _collect_heart_rate(self, user_id: int, target_date: date, date_str: str) -> Optional[HeartRateDaily]:
        """심박수 데이터 수집 및 저장"""
        from app.domain import HeartRate, SleepHRV
        from garth import DailyHRV
        
        logger.info("심박수 데이터 수집 - User: %d, Date: %s", user_id, date_str)
        
        try:
            # 1. Garmin API 조회
            heart_rate_data = HeartRate.get(date_str, client=self.client)
            if not heart_rate_data:
                logger.info("심박수 데이터 없음 - User: %d, Date: %s", user_id, date_str)
                return None
                
            # 1-1. HRV 데이터 조회 (수면 중 HRV)
            sleep_hrv_data = SleepHRV.get(date_str, client=self.client)
            
            # 1-2. 일간 HRV 통계 데이터 조회
            daily_hrv_data = None
            try:
                daily_hrv_list = DailyHRV.list(end=date_str, period=1, client=self.client)
                if daily_hrv_list and len(daily_hrv_list) > 0:
                    daily_hrv_data = daily_hrv_list[0]
            except Exception as e:
                logger.warning(f"일간 HRV 통계 조회 실패: {str(e)}")

            # 2. 기존 데이터 확인 및 삭제
            await session.execute(
                delete(HeartRateReading).where(
                    HeartRateReading.user_id == user_id,
                    HeartRateReading.timestamp >= target_date,
                    HeartRateReading.timestamp < target_date + date.resolution
                )
            )

            # 3. 평균 심박수 계산 (시계열 데이터에서)
            avg_heart_rate = None
            if hasattr(heart_rate_data, 'heart_rate_values') and heart_rate_data.heart_rate_values:
                valid_readings = [r.heart_rate for r in heart_rate_data.heart_rate_values if r.heart_rate is not None]
                if valid_readings:
                    avg_heart_rate = sum(valid_readings) / len(valid_readings)
            
            # 4. HRV 값 결정 (여러 소스에서 가져옴)
            avg_hrv = None
            # 수면 HRV 데이터에서 가져오기
            if sleep_hrv_data and hasattr(sleep_hrv_data, 'hrv_summary') and sleep_hrv_data.hrv_summary:
                avg_hrv = sleep_hrv_data.hrv_summary.last_night_avg
            # 일간 HRV 통계에서 가져오기
            elif daily_hrv_data and hasattr(daily_hrv_data, 'avg_hrv'):
                avg_hrv = daily_hrv_data.avg_hrv

            # 5. 일일 요약 저장
            daily_summary = HeartRateDaily(
                user_id=user_id,
                date=target_date,
                resting_hr=heart_rate_data.resting_heart_rate,
                max_hr=heart_rate_data.max_heart_rate,
                min_hr=heart_rate_data.min_heart_rate,
                avg_hr=avg_heart_rate,
                avg_hrv=avg_hrv,
            )
            session.add(daily_summary)
            await session.flush()

            # 6. 상세 측정값 저장
            readings = []
            for reading in heart_rate_data.heart_rate_values:
                readings.append(
                    HeartRateReading(
                        user_id=user_id,
                        timestamp=reading.time,
                        heart_rate=reading.heart_rate,
                        hrv=getattr(reading, 'hrv', None),
                    )
                )
            
            if readings:
                session.add_all(readings)
                await session.flush()
            
            await session.commit()
            logger.info("심박수 데이터 저장 완료 - User: %d, Date: %s, 측정값: %d개", 
                        user_id, date_str, len(readings))
            return daily_summary

        except Exception as e:
            await session.rollback()
            logger.error("심박수 데이터 수집 실패 - User: %d, Date: %s, Error: %s", 
                        user_id, date_str, str(e))
            return None

    async def _collect_stress(self, user_id: int, target_date: date, date_str: str) -> Optional[StressDaily]:
        """스트레스 데이터 수집 및 저장"""
        from app.domain import Stress
        
        logger.info("스트레스 데이터 수집 - User: %d, Date: %s", user_id, date_str)
        
        try:
            # 1. Garmin API 조회
            stress_data = Stress.get(date_str, client=self.client)
            if not stress_data:
                logger.info("스트레스 데이터 없음 - User: %d, Date: %s", user_id, date_str)
                return None

            # 2. 기존 데이터 확인 및 삭제
            result = await session.execute(
                select(StressDaily).where(
                    StressDaily.user_id == user_id,
                    StressDaily.date == target_date
                )
            )
            existing_daily = result.scalar_one_or_none()
            
            if existing_daily:
                # 기존 상세 데이터 삭제
                await session.execute(
                    delete(StressReading).where(
                        StressReading.user_id == user_id,
                        StressReading.timestamp >= target_date,
                        StressReading.timestamp < target_date + date.resolution
                    )
                )
                # 기존 일일 요약 삭제
                await session.delete(existing_daily)
                await session.flush()

            # 3. 일일 요약 저장
            # 스트레스 지속 시간 계산 (초 단위)
            stress_duration = 0
            rest_duration = 0
            for reading in stress_data.stress_values:
                if reading.stress_level >= 0:  # 0-100: 스트레스 수준
                    stress_duration += 60  # 각 측정값은 1분 간격으로 가정
                elif reading.stress_level == -2:  # -2: 수면
                    rest_duration += 60
            
            daily_summary = StressDaily(
                user_id=user_id,
                date=target_date,
                avg_stress_level=stress_data.avg_stress_level,
                max_stress_level=stress_data.max_stress_level,
                stress_duration_seconds=stress_duration,
                rest_duration_seconds=rest_duration,
            )
            session.add(daily_summary)
            await session.flush()

            # 4. 상세 측정값 저장
            readings = []
            for reading in stress_data.stress_values:
                readings.append(
                    StressReading(
                        user_id=user_id,
                        timestamp=reading.time,
                        stress_level=reading.stress_level,
                        body_battery=getattr(reading, 'body_battery', None),
                    )
                )
            
            if readings:
                session.add_all(readings)
                await session.flush()
            
            await session.commit()
            logger.info("스트레스 데이터 저장 완료 - User: %d, Date: %s, 측정값: %d개", 
                        user_id, date_str, len(readings))
            return daily_summary

        except Exception as e:
            await session.rollback()
            logger.error("스트레스 데이터 수집 실패 - User: %d, Date: %s, Error: %s", 
                        user_id, date_str, str(e))
            return None

    async def _collect_steps(self, user_id: int, target_date: date, date_str: str) -> Optional[StepsDaily]:
        """걸음수 데이터 수집 및 저장"""
        from app.domain import DailySummary, StepsValue
        
        logger.info("걸음수 데이터 수집 - User: %d, Date: %s", user_id, date_str)
        
        try:
            # 1. Garmin API 조회 - 일일 요약
            daily_summary_data = DailySummary.get(date_str, client=self.client)
            if not daily_summary_data:
                logger.info("걸음수 요약 데이터 없음 - User: %d, Date: %s", user_id, date_str)
                return None
                
            # 2. 상세 걸음수 데이터 조회
            steps_data = StepsValue.get_readings(date_str, client=self.client)

            # 3. 기존 데이터 확인 및 삭제
            result = await session.execute(
                select(StepsDaily).where(
                    StepsDaily.user_id == user_id,
                    StepsDaily.date == target_date
                )
            )
            existing_daily = result.scalar_one_or_none()
            
            if existing_daily:
                # 기존 상세 데이터 삭제
                await session.execute(
                    delete(StepsIntraday).where(
                        StepsIntraday.user_id == user_id,
                        StepsIntraday.start_time >= target_date,
                        StepsIntraday.start_time < target_date + date.resolution
                    )
                )
                # 기존 일일 요약 삭제
                await session.delete(existing_daily)
                await session.flush()

            # 4. 일일 요약 저장
            # 정수 변환 처리
            floors_climbed = int(daily_summary_data.floors_ascended) if hasattr(daily_summary_data, 'floors_ascended') else 0
            
            daily_summary = StepsDaily(
                user_id=user_id,
                date=target_date,
                total_steps=daily_summary_data.total_steps,
                goal_steps=daily_summary_data.daily_step_goal,
                distance=daily_summary_data.total_distance_meters / 1000,  # m -> km 변환
                calories=daily_summary_data.active_kilocalories,
                active_minutes=daily_summary_data.highly_active_seconds // 60 + daily_summary_data.active_seconds // 60,
                floors_climbed=floors_climbed,
            )
            session.add(daily_summary)
            await session.flush()

            # 5. 상세 측정값 저장 (있는 경우)
            readings = []
            if steps_data:
                for reading in steps_data:
                    readings.append(
                        StepsIntraday(
                            user_id=user_id,
                            start_time=reading.start_gmt,
                            end_time=reading.end_gmt,
                            steps=reading.steps,
                            activity_level=reading.primary_activity_level,
                            intensity=0,  # 기본값 설정
                        )
                    )
                
                if readings:
                    session.add_all(readings)
                    await session.flush()
            
            await session.commit()
            logger.info("걸음수 데이터 저장 완료 - User: %d, Date: %s, 측정값: %d개", 
                        user_id, date_str, len(readings))
            return daily_summary

        except Exception as e:
            await session.rollback()
            logger.error("걸음수 데이터 수집 실패 - User: %d, Date: %s, Error: %s", 
                        user_id, date_str, str(e))
            return None

    async def _collect_sleep(self, user_id: int, target_date: date, date_str: str) -> Optional[SleepSession]:
        """수면 데이터 수집 및 저장"""
        from garth import SleepData
        from app.domain import SleepHRV
        
        logger.info("수면 데이터 수집 - User: %d, Date: %s", user_id, date_str)
        
        try:
            # 1. Garmin API 조회
            sleep_data = SleepData.get(date_str, client=self.client)
            if not sleep_data:
                logger.info("수면 데이터 없음 - User: %d, Date: %s", user_id, date_str)
                return None
                
            # 2. HRV 데이터 조회
            hrv_data = SleepHRV.get(date_str, client=self.client)
            hrv_readings = hrv_data.hrv_readings

            # 3. 기존 데이터 확인 및 삭제
            result = await session.execute(
                select(SleepSession).where(
                    SleepSession.user_id == user_id,
                    SleepSession.date == target_date
                )
            )
            existing_session = result.scalar_one_or_none()
            
            if existing_session:
                # 기존 움직임 데이터 삭제
                await session.execute(
                    delete(SleepMovement).where(
                        SleepMovement.sleep_session_id == existing_session.id
                    )
                )
                # 기존 HRV 데이터 삭제
                await session.execute(
                    delete(SleepHRVReading).where(
                        SleepHRVReading.user_id == user_id,
                        SleepHRVReading.timestamp >= target_date,
                        SleepHRVReading.timestamp < target_date + date.resolution
                    )
                )
                # 기존 세션 삭제
                await session.delete(existing_session)
                await session.flush()

            # 4. 수면 세션 저장
            sleep_session = SleepSession(
                user_id=user_id,
                date=target_date,
                start_time=sleep_data.daily_sleep_dto.sleep_start,
                end_time=sleep_data.daily_sleep_dto.sleep_end,
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
            if hrv_data and hrv_data.hrv_summary:
                sleep_session.avg_hrv = hrv_data.hrv_summary.last_night_avg
                sleep_session.hrv_weekly_avg = hrv_data.hrv_summary.weekly_avg
                sleep_session.hrv_last_night_avg = hrv_data.hrv_summary.last_night_avg
                sleep_session.hrv_last_night_5_min_high = hrv_data.hrv_summary.last_night_5_min_high
                sleep_session.hrv_status = hrv_data.hrv_summary.status
                sleep_session.hrv_feedback = hrv_data.hrv_summary.feedback_phrase
                
                if hrv_data.hrv_summary.baseline:
                    sleep_session.hrv_baseline_low_upper = hrv_data.hrv_summary.baseline.low_upper
                    sleep_session.hrv_baseline_balanced_low = hrv_data.hrv_summary.baseline.balanced_low
                    sleep_session.hrv_baseline_balanced_upper = hrv_data.hrv_summary.baseline.balanced_upper
                    sleep_session.hrv_baseline_marker_value = hrv_data.hrv_summary.baseline.marker_value
            
            session.add(sleep_session)
            await session.flush()

            # 5. 수면 움직임 데이터 저장
            movements = []
            if hasattr(sleep_data, 'sleep_movement') and sleep_data.sleep_movement:
                for movement in sleep_data.sleep_movement:
                    movements.append(
                        SleepMovement(
                            sleep_session_id=sleep_session.id,
                            timestamp=movement.start_gmt,
                            activity_level=movement.activity_level,
                        )
                    )
                
                if movements:
                    session.add_all(movements)
                    await session.flush()
            
            # 6. HRV 상세 데이터 저장
            hrv_readings_db = []
            if hrv_readings:
                # hrv_readings가 반복 가능한지 확인
                if not isinstance(hrv_readings, list):
                    # 반복 가능하지 않다면 리스트로 변환
                    hrv_readings = [hrv_readings] if hrv_readings else []
                
                for reading in hrv_readings:
                    hrv_readings_db.append(
                        SleepHRVReading(
                            user_id=user_id,
                            timestamp=reading.reading_time_gmt,
                            hrv_value=reading.hrv_value,
                        )
                    )
            
            if hrv_readings_db:
                session.add_all(hrv_readings_db)
                await session.flush()
            
            await session.commit()
            logger.info("수면 데이터 저장 완료 - User: %d, Date: %s, 움직임: %d개, HRV: %d개", 
                        user_id, date_str, len(movements), len(hrv_readings_db))
            return sleep_session

        except Exception as e:
            await session.rollback()
            logger.error("수면 데이터 수집 실패 - User: %d, Date: %s, Error: %s", 
                        user_id, date_str, str(e))
            return None

    async def _collect_activities(self, user_id: int, target_date: date, date_str: str) -> List[Activity]:
        """활동 데이터 수집 및 저장"""
        from app.domain import Activity as ActivityDomain
        
        logger.info("활동 데이터 수집 - User: %d, Date: %s", user_id, date_str)
        
        try:
            # 1. Garmin API 조회 - 해당 날짜의 활동 목록
            # 날짜 기반 조회 메서드가 없으므로 전체 목록에서 필터링
            all_activities = ActivityDomain.list(limit=50, client=self.client)
            if not all_activities:
                logger.info("활동 데이터 없음 - User: %d, Date: %s", user_id, date_str)
                return []
                
            # 해당 날짜의 활동만 필터링
            target_date_start = datetime.combine(target_date, datetime.min.time())
            target_date_end = datetime.combine(target_date, datetime.max.time())
            activities = [
                activity for activity in all_activities 
                if target_date_start <= activity.start_time_local <= target_date_end
            ]
            
            if not activities:
                logger.info("해당 날짜의 활동 데이터 없음 - User: %d, Date: %s", user_id, date_str)
                return []

            # 2. 각 활동 상세 정보 조회 및 저장
            saved_activities = []
            for activity_summary in activities:
                # 활동 상세 정보는 이미 조회된 상태로 가정
                activity_detail = activity_summary
                
                # 기존 활동 확인
                result = await session.execute(
                    select(Activity).where(
                        Activity.id == activity_detail.activity_id,
                        Activity.user_id == user_id
                    )
                )
                existing_activity = result.scalar_one_or_none()
                
                # 기존 활동이 있으면 건너뛰기
                if existing_activity:
                    logger.info(f"이미 존재하는 활동 건너뛰기 - ID: {activity_detail.activity_id}")
                    saved_activities.append(existing_activity)
                    continue
                
                # 활동 저장
                activity = Activity(
                    id=activity_detail.activity_id,
                    user_id=user_id,
                    activity_type=activity_detail.activity_type.type_key,
                    start_time=activity_detail.start_time_local,
                    end_time=activity_detail.start_time_local + timedelta(seconds=int(activity_detail.duration)),
                    distance=getattr(activity_detail, 'distance', None),
                    duration_seconds=int(activity_detail.duration),
                    calories=activity_detail.calories,
                    avg_heart_rate=getattr(activity_detail, 'average_hr', None),
                    max_heart_rate=getattr(activity_detail, 'max_hr', None),
                    avg_speed=getattr(activity_detail, 'average_speed', None),
                    elevation_gain=getattr(activity_detail, 'elevation_gain', None),
                    training_effect=None,  # 훈련 효과 데이터가 없음
                )
                session.add(activity)
                await session.flush()
                
                saved_activities.append(activity)
            
            await session.commit()
            logger.info("활동 데이터 저장 완료 - User: %d, Date: %s, 활동: %d개", 
                        user_id, date_str, len(saved_activities))
            return saved_activities

        except Exception as e:
            await session.rollback()
            logger.error("활동 데이터 수집 실패 - User: %d, Date: %s, Error: %s", 
                        user_id, date_str, str(e))
            return []
