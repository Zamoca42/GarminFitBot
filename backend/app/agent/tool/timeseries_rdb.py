"""RDB 조회를 위한 도구들"""

from datetime import date
from typing import Any, Dict, Optional, Type

from pydantic import BaseModel, Field
from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.agent.tool import BaseDBTool
from app.model import (
    HeartRateDaily,
    HeartRateReading,
    SleepHRVReading,
    SleepMovement,
    SleepSession,
    StepsDaily,
    StepsIntraday,
    StressDaily,
    StressReading,
)


class TimeSeriesInput(BaseModel):
    """시계열 데이터 조회 입력"""

    user_id: int = Field(..., description="가민 사용자 ID")
    target_date: date = Field(..., description="조회할 날짜 (YYYY-MM-DD)")


class HeartRateTimeSeriesTool(BaseDBTool):
    """심박수 시계열 데이터 조회 도구"""

    name: str = "heart_rate_timeseries"
    description: str = "특정 날짜의 심박수 시계열 데이터를 조회합니다."
    args_schema: Type[BaseModel] = TimeSeriesInput

    def _execute(
        self, session: Session, user_id: int, target_date: date
    ) -> Dict[str, Any]:
        daily = session.execute(
            select(HeartRateDaily).where(
                and_(
                    HeartRateDaily.user_id == user_id,
                    HeartRateDaily.date == target_date,
                )
            )
        ).scalar_one_or_none()

        if not daily:
            return None

        readings = (
            session.execute(
                select(HeartRateReading)
                .where(HeartRateReading.daily_summary_id == daily.id)
                .order_by(HeartRateReading.start_time_local)
            )
            .scalars()
            .all()
        )

        return {
            "date": target_date,
            "user_id": user_id,
            "description": self.description,
            "type": "heart_rate_timeseries",
            "readings": [
                {"time": reading.start_time_local, "value": reading.heart_rate}
                for reading in readings
            ],
        }


class StepsTimeSeriesTool(BaseDBTool):
    """걸음수 시계열 데이터 조회 도구"""

    name: str = "steps_timeseries"
    description: str = "특정 날짜의 걸음수 시계열 데이터를 조회합니다."
    args_schema: Type[BaseModel] = TimeSeriesInput

    def _execute(
        self, session: Session, user_id: int, target_date: date
    ) -> Dict[str, Any]:
        daily = session.execute(
            select(StepsDaily).where(
                and_(StepsDaily.user_id == user_id, StepsDaily.date == target_date)
            )
        ).scalar_one_or_none()

        if not daily:
            return None

        readings = (
            session.execute(
                select(StepsIntraday)
                .where(StepsIntraday.daily_summary_id == daily.id)
                .order_by(StepsIntraday.start_time_local)
            )
            .scalars()
            .all()
        )

        return {
            "date": target_date,
            "user_id": user_id,
            "description": self.description,
            "type": "steps_timeseries",
            "readings": [
                {
                    "start_time": reading.start_time_local,
                    "end_time": reading.end_time_local,
                    "steps": reading.steps,
                    "activity_level": reading.activity_level,
                }
                for reading in readings
            ],
        }


class StressTimeSeriesTool(BaseDBTool):
    """스트레스 시계열 데이터 조회 도구"""

    name: str = "stress_timeseries"
    description: str = "특정 날짜의 스트레스 시계열 데이터를 조회합니다."
    args_schema: Type[BaseModel] = TimeSeriesInput

    def _execute(
        self, session: Session, user_id: int, target_date: date
    ) -> Dict[str, Any]:
        daily = session.execute(
            select(StressDaily).where(
                and_(StressDaily.user_id == user_id, StressDaily.date == target_date)
            )
        ).scalar_one_or_none()

        if not daily:
            return None

        readings = (
            session.execute(
                select(StressReading)
                .where(StressReading.daily_summary_id == daily.id)
                .order_by(StressReading.start_time_local)
            )
            .scalars()
            .all()
        )

        return {
            "date": target_date,
            "user_id": user_id,
            "description": self.description,
            "type": "stress_timeseries",
            "readings": [
                {"time": reading.start_time_local, "level": reading.stress_level}
                for reading in readings
            ],
        }


class SleepTimeSeriesTool(BaseDBTool):
    """수면 시계열 데이터 조회 도구"""

    name: str = "sleep_timeseries"
    description: str = "특정 날짜의 수면 시계열 데이터(수면 단계와 HRV)를 조회합니다."
    args_schema: Type[BaseModel] = TimeSeriesInput

    def _execute(
        self, session: Session, user_id: int, target_date: date
    ) -> Dict[str, Any]:
        sleep_session = session.execute(
            select(SleepSession).where(
                and_(SleepSession.user_id == user_id, SleepSession.date == target_date)
            )
        ).scalar_one_or_none()

        if not sleep_session:
            return None

        # 수면 단계 데이터 조회 (1분 단위)
        movements = (
            session.execute(
                select(SleepMovement)
                .where(SleepMovement.sleep_session_id == sleep_session.id)
                .order_by(SleepMovement.start_time_local)
            )
            .scalars()
            .all()
        )

        # HRV 데이터 조회 (5분 단위)
        hrv_readings = (
            session.execute(
                select(SleepHRVReading)
                .where(SleepHRVReading.sleep_session_id == sleep_session.id)
                .order_by(SleepHRVReading.start_time_local)
            )
            .scalars()
            .all()
        )

        sleep_analysis = []
        current_hrv_index = 0

        for movement in movements:
            current_hrv = None
            movement_time = movement.start_time_local

            if hrv_readings and current_hrv_index < len(hrv_readings):
                hrv_reading = hrv_readings[current_hrv_index]
                time_diff = (
                    movement_time - hrv_reading.start_time_local
                ).total_seconds()

                while time_diff >= 300 and current_hrv_index < len(hrv_readings) - 1:
                    current_hrv_index += 1
                    hrv_reading = hrv_readings[current_hrv_index]
                    time_diff = (
                        movement_time - hrv_reading.start_time_local
                    ).total_seconds()

                if -300 <= time_diff < 300:
                    current_hrv = hrv_reading.hrv_value

            sleep_analysis.append(
                {
                    "start_time": movement_time,
                    "duration": 60,  # 항상 60초
                    "movement_level": movement.activity_level,
                    "hrv": current_hrv,
                    "stage": self._analyze_sleep_stage(
                        movement_level=movement.activity_level, hrv_value=current_hrv
                    ),
                }
            )

        return {
            "date": target_date,
            "user_id": user_id,
            "description": self.description,
            "type": "sleep_timeseries",
            "session_period": {
                "start": sleep_session.start_time_local,
                "end": sleep_session.end_time_local,
            },
            "sleep_stages": sleep_analysis,
            "hrv_readings": [
                {"time": reading.start_time_local, "value": reading.hrv_value}
                for reading in hrv_readings
            ],
        }

    def _analyze_sleep_stage(
        self, movement_level: int, hrv_value: Optional[int] = None
    ) -> Dict[str, Any]:
        """수면 단계 분석

        Args:
            movement_level: 움직임 레벨 (1분 단위로 측정)
            hrv_value: HRV 값 (5분 단위로 측정, 없을 수 있음)

        Returns:
            Dict: 수면 단계 분석 결과
                - stage: 수면 단계 (deep_sleep, light_sleep, rem_sleep, awake)
                - confidence: 신뢰도 (0-100)
                - factors: 판단에 사용된 요소들
        """
        confidence = 70
        factors = ["movement"]

        if movement_level == 0:  # 움직임 없음
            stage = "deep_sleep"
            confidence += 10
        elif movement_level == 1:  # 약간의 움직임
            stage = "light_sleep"
        elif movement_level == 2:  # 중간 정도의 움직임
            stage = "rem_sleep"
        else:  # 많은 움직임
            stage = "awake"
            confidence += 10

        if hrv_value is not None:
            factors.append("hrv")

            if stage == "deep_sleep":
                if hrv_value > 50:  # 높은 HRV는 깊은 수면과 맞지 않음
                    confidence -= 20
                elif hrv_value < 30:  # 낮은 HRV는 깊은 수면과 일치
                    confidence += 10
            elif stage == "rem_sleep":
                if hrv_value > 60:  # REM 수면은 보통 높은 HRV
                    confidence += 15
                elif hrv_value < 40:  # 낮은 HRV는 REM 수면과 맞지 않음
                    confidence -= 15
            elif stage == "light_sleep" and 30 <= hrv_value <= 50:  # 적당한 HRV
                confidence += 10

        confidence = max(0, min(100, confidence))

        return {"stage": stage, "confidence": confidence, "factors": factors}
