from sqlalchemy import Column, Date, ForeignKey, Index, Integer, String
from sqlalchemy.orm import relationship

from core.db import Base, TimeStampMixin


class Analytics(Base, TimeStampMixin):
    __tablename__ = "analytics"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False)
    step_comment = Column(String(255), nullable=False)
    sleep_comment = Column(String(255), nullable=False)
    stress_comment = Column(String(255), nullable=False)
    activity_comment = Column(String(255), nullable=False)
    heart_rate_comment = Column(String(255), nullable=False)
    daily_summary_comment = Column(String(255), nullable=False)
    weather_comment = Column(String(255), nullable=True)
    all_comment = Column(String(255), nullable=True)

    user = relationship("User", backref="ai_analytics_comments")

    __table_args__ = (Index("idx_analytics_user_date", "user_id", "date"),)
