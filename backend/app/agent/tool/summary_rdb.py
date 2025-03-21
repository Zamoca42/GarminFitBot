"""RDB 조회를 위한 도구들"""

from datetime import date
from typing import Any, Dict, Type

from pydantic import BaseModel, Field
from sqlalchemy import and_, select
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from app.agent.tool import BaseDBTool
from app.model import (
    Activity,
    HeartRateDaily,
    SleepSession,
    StepsDaily,
    StressDaily,
)


class DateRangeInput(BaseModel):
    """날짜 범위 입력"""

    user_id: int = Field(..., description="가민 사용자 ID")
    start_date: date = Field(..., description="조회 시작 날짜 (YYYY-MM-DD)")
    end_date: date = Field(..., description="조회 종료 날짜 (YYYY-MM-DD)")


# 심박수 도구들
class HeartRateSummaryTool(BaseDBTool):
    """심박수 요약 데이터 조회 도구"""

    name: str = "heart_rate_summary"
    description: str = "특정 기간의 심박수 일일 요약 데이터를 조회합니다."
    args_schema: Type[BaseModel] = DateRangeInput

    def _execute(
        self, session: Session, user_id: int, start_date: date, end_date: date
    ) -> Dict[str, Any]:
        summaries = (
            session.execute(
                select(HeartRateDaily)
                .where(
                    and_(
                        HeartRateDaily.user_id == user_id,
                        HeartRateDaily.date >= start_date,
                        HeartRateDaily.date <= end_date,
                    )
                )
                .order_by(HeartRateDaily.date)
            )
            .scalars()
            .all()
        )

        return {
            "period": {"start_date": start_date, "end_date": end_date},
            "type": "heart_rate_summary",
            "user_id": user_id,
            "description": self.description,
            "data": [
                {
                    "date": summary.date,
                    "resting": summary.resting_hr,
                    "max": summary.max_hr,
                    "min": summary.min_hr,
                    "avg": summary.avg_hr,
                }
                for summary in summaries
            ],
        }


class StepsSummaryTool(BaseDBTool):
    """걸음수 요약 데이터 조회 도구"""

    name: str = "steps_summary"
    description: str = "특정 기간의 걸음수 일일 요약 데이터를 조회합니다."
    args_schema: Type[BaseModel] = DateRangeInput

    def _execute(
        self, session: Session, user_id: int, start_date: date, end_date: date
    ) -> Dict[str, Any]:
        summaries = (
            session.execute(
                select(StepsDaily)
                .where(
                    and_(
                        StepsDaily.user_id == user_id,
                        StepsDaily.date >= start_date,
                        StepsDaily.date <= end_date,
                    )
                )
                .order_by(StepsDaily.date)
            )
            .scalars()
            .all()
        )

        return {
            "period": {"start_date": start_date, "end_date": end_date},
            "type": "steps_summary",
            "user_id": user_id,
            "description": self.description,
            "data": [
                {
                    "date": summary.date,
                    "total_steps": summary.total_steps,
                    "goal_steps": summary.goal_steps,
                    "distance": summary.distance,
                    "calories": summary.calories,
                    "active_minutes": summary.active_minutes,
                }
                for summary in summaries
            ],
        }


class StressSummaryTool(BaseDBTool):
    """스트레스 요약 데이터 조회 도구"""

    name: str = "stress_summary"
    description: str = "특정 기간의 스트레스 일일 요약 데이터를 조회합니다."
    args_schema: Type[BaseModel] = DateRangeInput

    def _execute(
        self, session: Session, user_id: int, start_date: date, end_date: date
    ) -> Dict[str, Any]:
        summaries = (
            session.execute(
                select(StressDaily)
                .where(
                    and_(
                        StressDaily.user_id == user_id,
                        StressDaily.date >= start_date,
                        StressDaily.date <= end_date,
                    )
                )
                .order_by(StressDaily.date)
            )
            .scalars()
            .all()
        )

        return {
            "period": {"start_date": start_date, "end_date": end_date},
            "type": "stress_summary",
            "user_id": user_id,
            "description": self.description,
            "data": [
                {
                    "date": summary.date,
                    "avg_stress_level": summary.avg_stress_level,
                    "max_stress_level": summary.max_stress_level,
                    "stress_duration": summary.stress_duration_seconds,
                    "rest_duration": summary.rest_duration_seconds,
                }
                for summary in summaries
            ],
        }


class SleepSummaryTool(BaseDBTool):
    """수면 요약 데이터 조회 도구"""

    name: str = "sleep_summary"
    description: str = "특정 기간의 수면 일일 요약 데이터를 조회합니다."
    args_schema: Type[BaseModel] = DateRangeInput

    def _execute(
        self, session: Session, user_id: int, start_date: date, end_date: date
    ) -> Dict[str, Any]:
        summaries = (
            session.execute(
                select(SleepSession)
                .where(
                    and_(
                        SleepSession.user_id == user_id,
                        SleepSession.date >= start_date,
                        SleepSession.date <= end_date,
                    )
                )
                .order_by(SleepSession.date)
            )
            .scalars()
            .all()
        )

        return {
            "period": {"start_date": start_date, "end_date": end_date},
            "user_id": user_id,
            "description": self.description,
            "type": "sleep_summary",
            "data": [
                {
                    "date": summary.date,
                    "start_time": summary.start_time_local,
                    "end_time": summary.end_time_local,
                    "duration": {
                        "total": summary.total_seconds,
                        "deep": summary.deep_sleep_seconds,
                        "light": summary.light_sleep_seconds,
                        "rem": summary.rem_sleep_seconds,
                        "awake": summary.awake_seconds,
                    },
                    "biometrics": {
                        "avg_stress": summary.avg_stress_level,
                        "avg_hrv": summary.avg_hrv,
                        "avg_spo2": summary.avg_spo2,
                        "avg_respiration": summary.avg_respiration,
                    },
                    "hrv_analysis": {
                        "weekly_avg": summary.hrv_weekly_avg,
                        "last_night_avg": summary.hrv_last_night_avg,
                        "last_night_5min_high": summary.hrv_last_night_5_min_high,
                        "status": summary.hrv_status,
                        "feedback": summary.hrv_feedback,
                        "baseline": {
                            "low_upper": summary.hrv_baseline_low_upper,
                            "balanced_low": summary.hrv_baseline_balanced_low,
                            "balanced_upper": summary.hrv_baseline_balanced_upper,
                            "marker_value": summary.hrv_baseline_marker_value,
                        },
                    },
                }
                for summary in summaries
            ],
        }


class ActivitySummaryTool(BaseDBTool):
    """활동 요약 데이터 조회 도구"""

    name: str = "activity_summary"
    description: str = "특정 기간의 운동 활동 요약 데이터를 조회합니다."
    args_schema: Type[BaseModel] = DateRangeInput

    def _execute(
        self, session: Session, user_id: int, start_date: date, end_date: date
    ) -> Dict[str, Any]:
        # 시작 날짜와 종료 날짜를 기준으로 활동 데이터 조회
        activities = (
            session.execute(
                select(Activity)
                .where(
                    and_(
                        Activity.user_id == user_id,
                        func.date(Activity.start_time_local) >= start_date,
                        func.date(Activity.start_time_local) <= end_date,
                    )
                )
                .order_by(Activity.start_time_local)
            )
            .scalars()
            .all()
        )

        return {
            "period": {"start_date": start_date, "end_date": end_date},
            "type": "activity_summary",
            "user_id": user_id,
            "description": self.description,
            "data": [
                {
                    "activity_type": activity.activity_type,
                    "start_time": activity.start_time_local,
                    "end_time": activity.end_time_local,
                    "duration_seconds": activity.duration_seconds,
                    "distance": activity.distance,
                    "calories": activity.calories,
                    "heart_rate": {
                        "avg": activity.avg_heart_rate,
                        "max": activity.max_heart_rate,
                    },
                    "performance": {
                        "avg_speed": activity.avg_speed,
                        "elevation_gain": activity.elevation_gain,
                        "training_effect": activity.training_effect,
                    },
                }
                for activity in activities
            ],
        }
