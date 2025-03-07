from sqlalchemy import BigInteger, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from core.db import Base, TimeStampMixin


class Activity(Base, TimeStampMixin):
    __tablename__ = "activities"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    activity_type = Column(String(50), nullable=False)
    start_time_utc = Column(DateTime(timezone=True), nullable=False)
    start_time_local = Column(DateTime(timezone=False), nullable=False)
    end_time_utc = Column(DateTime(timezone=True), nullable=False)
    end_time_local = Column(DateTime(timezone=False), nullable=False)
    distance = Column(Float)  # km
    duration_seconds = Column(Integer)
    calories = Column(Integer)
    avg_heart_rate = Column(Integer)
    max_heart_rate = Column(Integer)
    avg_speed = Column(Float)  # km/h
    elevation_gain = Column(Integer)  # meters
    training_effect = Column(Float)

    user = relationship("User", backref="activities")
