from sqlalchemy import Column, Integer, Float, String, Date, DateTime, ForeignKey, Index, CheckConstraint
from sqlalchemy.orm import relationship
from .base import Base, TimeStampMixin

class StepsDaily(Base, TimeStampMixin):
    __tablename__ = 'steps_daily'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    date = Column(Date, nullable=False)
    total_steps = Column(Integer)
    goal_steps = Column(Integer)
    distance = Column(Float)  # km
    calories = Column(Integer)
    active_minutes = Column(Integer)
    floors_climbed = Column(Integer)

    # 해당 일자의 상세 측정값들과 관계 설정
    intraday_readings = relationship("StepsIntraday", 
                                   back_populates="daily_summary",
                                   primaryjoin="and_(StepsDaily.user_id==StepsIntraday.user_id, "
                                             "cast(StepsDaily.date as DateTime)==cast(StepsIntraday.start_time as Date))")

    user = relationship("User", backref="steps_dailies")
    __table_args__ = (Index('idx_steps_daily_user_date', 'user_id', 'date'),)

class StepsIntraday(Base):
    __tablename__ = 'steps_intraday'
    __table_args__ = (
        Index('idx_steps_intraday_user_time', 'user_id', 'start_time'),
        CheckConstraint('intensity BETWEEN 0 AND 10', name='intensity_range'),
        {
            'postgresql_partition_by': 'RANGE (start_time)'
        }
    ) 

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    start_time = Column(DateTime(timezone=True), primary_key=True)
    end_time = Column(DateTime(timezone=True), nullable=False)
    steps = Column(Integer)
    activity_level = Column(String(20))
    intensity = Column(Integer)

    # 해당 측정값의 일일 요약과 관계 설정
    daily_summary = relationship("StepsDaily", 
                               back_populates="intraday_readings",
                               foreign_keys=[user_id],
                               primaryjoin="and_(StepsDaily.user_id==StepsIntraday.user_id, "
                                         "cast(StepsDaily.date as DateTime)==cast(StepsIntraday.start_time as Date))")

    user = relationship("User", backref="steps_intraday")
