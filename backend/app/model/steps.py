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


class StepsDaily(Base, TimeStampMixin):
    __tablename__ = "steps_daily"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    date = Column(Date, nullable=False)
    total_steps = Column(Integer)
    goal_steps = Column(Integer)
    distance = Column(Float)  # km
    calories = Column(Integer)
    active_minutes = Column(Integer)
    floors_climbed = Column(Integer)

    # 해당 일자의 상세 측정값들과 관계 설정
    intraday_readings = relationship(
        "StepsIntraday",
        back_populates="daily_summary",
        cascade="all, delete-orphan",
        uselist=True,
    )

    user = relationship("User", back_populates="steps_dailies")


class StepsIntraday(Base):
    __tablename__ = "steps_intraday"
    __table_args__ = (
        PrimaryKeyConstraint("daily_summary_id", "start_time_local"),
        {"postgresql_partition_by": "RANGE (start_time_local)"},
    )

    daily_summary_id = Column(
        BigInteger, ForeignKey("steps_daily.id", ondelete="CASCADE"), nullable=False
    )
    start_time_gmt = Column(DateTime(timezone=True), nullable=False)
    end_time_gmt = Column(DateTime(timezone=True), nullable=False)
    start_time_local = Column(DateTime(timezone=False), nullable=False)
    end_time_local = Column(DateTime(timezone=False), nullable=False)
    steps = Column(Integer)
    activity_level = Column(String(20))
    intensity = Column(Integer)

    # 해당 측정값의 일일 요약과 관계 설정
    daily_summary = relationship(
        "StepsDaily",
        back_populates="intraday_readings",
        uselist=False,
    )
