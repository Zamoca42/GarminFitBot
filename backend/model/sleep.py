from sqlalchemy import Column, Integer, Float, Date, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from .base import Base, TimeStampMixin

class SleepSession(Base, TimeStampMixin):
    __tablename__ = 'sleep_sessions'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    date = Column(Date, nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    total_seconds = Column(Integer)
    deep_sleep_seconds = Column(Integer)
    light_sleep_seconds = Column(Integer)
    rem_sleep_seconds = Column(Integer)
    awake_seconds = Column(Integer)
    avg_stress_level = Column(Integer)
    avg_hrv = Column(Float)
    avg_spo2 = Column(Integer)
    avg_respiration = Column(Float)

    movements = relationship("SleepMovement", back_populates="session")
    user = relationship("User", backref="sleep_sessions")

class SleepMovement(Base):
    __tablename__ = 'sleep_movement'
    __table_args__ = (
        Index('idx_sleep_movement_time', 'sleep_session_id', 'timestamp'),
        {
            'postgresql_partition_by': 'RANGE (timestamp)',
            'postgresql_partition_func': 'date_trunc(\'month\', timestamp)'
        }
    )

    id = Column(Integer, primary_key=True)
    sleep_session_id = Column(Integer, ForeignKey('sleep_sessions.id'), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    activity_level = Column(Integer)  # 0: 깊은수면, 1: 얕은수면, 2: REM, 3: 깨어있음

    session = relationship("SleepSession", back_populates="movements") 