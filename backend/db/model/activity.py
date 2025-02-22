from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base, TimeStampMixin

class Activity(Base, TimeStampMixin):
    __tablename__ = 'activities'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    activity_type = Column(String(50), nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    distance = Column(Float)  # km
    duration_seconds = Column(Integer)
    calories = Column(Integer)
    avg_heart_rate = Column(Integer)
    max_heart_rate = Column(Integer)
    avg_speed = Column(Float)  # km/h
    elevation_gain = Column(Integer)  # meters
    training_effect = Column(Float)

    laps = relationship("ActivityLap", back_populates="activity")
    user = relationship("User", backref="activities")

class ActivityLap(Base):
    __tablename__ = 'activity_laps'

    id = Column(Integer, primary_key=True)
    activity_id = Column(Integer, ForeignKey('activities.id'), nullable=False)
    lap_number = Column(Integer, nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False)
    duration_seconds = Column(Integer)
    distance = Column(Float)
    avg_heart_rate = Column(Integer)

    activity = relationship("Activity", back_populates="laps") 