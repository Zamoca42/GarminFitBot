from sqlalchemy import (
    BigInteger,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    PrimaryKeyConstraint,
    String,
)
from sqlalchemy.orm import relationship

from core.db import Base, TimeStampMixin


class SleepSession(Base, TimeStampMixin):
    __tablename__ = "sleep_sessions"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False)
    start_time_gmt = Column(DateTime(timezone=True), nullable=False)
    end_time_gmt = Column(DateTime(timezone=True), nullable=False)
    start_time_local = Column(DateTime(timezone=False), nullable=False)
    end_time_local = Column(DateTime(timezone=False), nullable=False)

    # 수면 단계별 시간
    total_seconds = Column(Integer)
    deep_sleep_seconds = Column(Integer)
    light_sleep_seconds = Column(Integer)
    rem_sleep_seconds = Column(Integer)
    awake_seconds = Column(Integer)

    # 생체 지표 평균
    avg_stress_level = Column(Integer)
    avg_hrv = Column(Float)
    avg_spo2 = Column(Integer)
    avg_respiration = Column(Float)

    # HRV 상세 정보
    hrv_weekly_avg = Column(Integer)
    hrv_last_night_avg = Column(Integer)
    hrv_last_night_5_min_high = Column(Integer)
    hrv_status = Column(String(50))
    hrv_feedback = Column(String(255))

    # HRV Baseline 데이터
    hrv_baseline_low_upper = Column(Integer)
    hrv_baseline_balanced_low = Column(Integer)
    hrv_baseline_balanced_upper = Column(Integer)
    hrv_baseline_marker_value = Column(Float)

    # 관계 설정
    movements = relationship("SleepMovement", back_populates="session", uselist=True)
    hrv_readings = relationship(
        "SleepHRVReading",
        back_populates="session",
        uselist=True,  # one-to-many 관계 명시
    )
    user = relationship("User", backref="sleep_sessions")


class SleepMovement(Base):
    __tablename__ = "sleep_movement"
    __table_args__ = (
        PrimaryKeyConstraint("sleep_session_id", "start_time_local"),
        {"postgresql_partition_by": "RANGE (start_time_local)"},
    )

    sleep_session_id = Column(
        BigInteger, ForeignKey("sleep_sessions.id"), nullable=False
    )
    start_time_gmt = Column(DateTime(timezone=True), nullable=False)
    start_time_local = Column(DateTime(timezone=False), nullable=False)
    interval = Column(Integer)
    activity_level = Column(Integer)  # 0: 깊은수면, 1: 얕은수면, 2: REM, 3: 깨어있음

    session = relationship("SleepSession", back_populates="movements", uselist=False)


class SleepHRVReading(Base):
    """수면 중 HRV 상세 측정값"""

    __tablename__ = "sleep_hrv_readings"
    __table_args__ = (
        PrimaryKeyConstraint("sleep_session_id", "start_time_local"),
        {"postgresql_partition_by": "RANGE (start_time_local)"},
    )

    sleep_session_id = Column(
        BigInteger, ForeignKey("sleep_sessions.id"), nullable=False
    )
    start_time_gmt = Column(DateTime(timezone=True), nullable=False)
    start_time_local = Column(DateTime(timezone=False), nullable=False)
    hrv_value = Column(Integer)

    session = relationship(
        "SleepSession",
        back_populates="hrv_readings",
        uselist=False,  # many-to-one 관계 명시
    )
