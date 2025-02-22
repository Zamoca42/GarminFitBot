from sqlalchemy import Column, Integer, Float, Date, DateTime, ForeignKey, Index, String
from sqlalchemy.orm import relationship
from .base import Base, TimeStampMixin

class SleepSession(Base, TimeStampMixin):
    __tablename__ = 'sleep_sessions'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    date = Column(Date, nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    
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
    
    # HRV 상세 정보 추가
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
    movements = relationship("SleepMovement", back_populates="session")
    hrv_readings = relationship("SleepHRVReading", 
                              back_populates="session",
                              primaryjoin="and_(SleepSession.user_id==SleepHRVReading.user_id, "
                                        "cast(SleepSession.date as DateTime)==cast(SleepHRVReading.timestamp as Date))")
    user = relationship("User", backref="sleep_sessions")
    
    __table_args__ = (Index('idx_sleep_session_user_date', 'user_id', 'date'),)

class SleepMovement(Base):
    __tablename__ = 'sleep_movement'
    __table_args__ = (
        Index('idx_sleep_movement_time', 'sleep_session_id', 'timestamp'),
        {
            'postgresql_partition_by': 'RANGE (timestamp)'
        }
    )

    id = Column(Integer, primary_key=True)
    sleep_session_id = Column(Integer, ForeignKey('sleep_sessions.id'), nullable=False)
    timestamp = Column(DateTime(timezone=True), primary_key=True)
    activity_level = Column(Integer)  # 0: 깊은수면, 1: 얕은수면, 2: REM, 3: 깨어있음

    session = relationship("SleepSession", back_populates="movements")

class SleepHRVReading(Base):
    """수면 중 HRV 상세 측정값"""
    __tablename__ = 'sleep_hrv_readings'
    __table_args__ = (
        Index('idx_sleep_hrv_reading_user_time', 'user_id', 'timestamp'),
        {
            'postgresql_partition_by': 'RANGE (timestamp)'
        }
    )

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime(timezone=True), primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    hrv_value = Column(Integer)
    
    # SleepSession과의 관계 설정
    session = relationship("SleepSession", 
                         back_populates="hrv_readings",
                         foreign_keys=[user_id],
                         primaryjoin="and_(SleepSession.user_id==SleepHRVReading.user_id, "
                                   "cast(SleepSession.date as DateTime)==cast(SleepHRVReading.timestamp as Date))")
    user = relationship("User", backref="sleep_hrv_readings") 