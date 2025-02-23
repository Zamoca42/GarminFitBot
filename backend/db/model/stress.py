from sqlalchemy import Column, Integer, Date, DateTime, ForeignKey, Index, CheckConstraint, func, and_
from sqlalchemy.orm import relationship, remote, foreign
from .base import Base, TimeStampMixin

class StressDaily(Base, TimeStampMixin):
    __tablename__ = 'stress_daily'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    date = Column(Date, nullable=False)
    avg_stress_level = Column(Integer)
    max_stress_level = Column(Integer)
    stress_duration_seconds = Column(Integer)
    rest_duration_seconds = Column(Integer)

    # 해당 일자의 상세 측정값들과 관계 설정
    readings = relationship(
        "StressReading", 
        back_populates="daily_summary",
        primaryjoin=lambda: and_(
            StressDaily.user_id == remote(foreign(StressReading.user_id)),
            func.date(StressDaily.date) == func.date(remote(StressReading.timestamp))
        ),
        uselist=True
    )

    user = relationship("User", backref="stress_dailies")
    __table_args__ = (Index('idx_stress_daily_user_date', 'user_id', 'date'),)

class StressReading(Base):
    __tablename__ = 'stress_readings'
    __table_args__ = (
        Index('idx_stress_reading_user_time', 'user_id', 'timestamp'),
        CheckConstraint('stress_level BETWEEN -2 AND 100', name='stress_level_range'),
        CheckConstraint('body_battery BETWEEN 0 AND 100', name='body_battery_range'),
        {
            'postgresql_partition_by': 'RANGE (timestamp)'
        }
    ) 
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    timestamp = Column(DateTime(timezone=True), primary_key=True)
    stress_level = Column(Integer)
    body_battery = Column(Integer)

    # 해당 측정값의 일일 요약과 관계 설정
    daily_summary = relationship(
        "StressDaily", 
        back_populates="readings",
        primaryjoin=lambda: and_(
            foreign(StressReading.user_id) == remote(StressDaily.user_id),
            func.date(StressReading.timestamp) == func.date(remote(StressDaily.date))
        ),
        uselist=False
    )

    user = relationship(
        "User", 
        backref="stress_readings",
        viewonly=True
    )
