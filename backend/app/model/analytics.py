from sqlalchemy import BigInteger, Column, Date, ForeignKey, String
from sqlalchemy.orm import relationship

from core.db import Base, TimeStampMixin


class Analytics(Base, TimeStampMixin):
    __tablename__ = "analytics"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
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
