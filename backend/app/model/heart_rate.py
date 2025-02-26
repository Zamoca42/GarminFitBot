from sqlalchemy import (
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    and_,
    func,
)
from sqlalchemy.orm import foreign, relationship, remote

from core.db import Base, TimeStampMixin


class HeartRateDaily(Base, TimeStampMixin):
    __tablename__ = "heart_rate_daily"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False)
    resting_hr = Column(Integer)
    max_hr = Column(Integer)
    min_hr = Column(Integer)
    avg_hr = Column(Integer)
    avg_hrv = Column(Float)

    # 해당 일자의 상세 측정값들과 관계 설정
    readings = relationship(
        "HeartRateReading",
        back_populates="daily_summary",
        primaryjoin=lambda: and_(
            HeartRateDaily.user_id == remote(foreign(HeartRateReading.user_id)),
            func.date(HeartRateDaily.date)
            == func.date(remote(HeartRateReading.timestamp)),
        ),
        uselist=True,
    )

    user = relationship("User", backref="heart_rate_dailies")
    __table_args__ = (Index("idx_hr_daily_user_date", "user_id", "date"),)


class HeartRateReading(Base):
    __tablename__ = "heart_rate_readings"
    __table_args__ = (
        Index("idx_hr_reading_user_time", "user_id", "timestamp"),
        {"postgresql_partition_by": "RANGE (timestamp)"},
    )

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    timestamp = Column(DateTime(timezone=True), primary_key=True)
    heart_rate = Column(Integer)
    hrv = Column(Integer)

    # 해당 측정값의 일일 요약과 관계 설정
    daily_summary = relationship(
        "HeartRateDaily",
        back_populates="readings",
        primaryjoin=lambda: and_(
            foreign(HeartRateReading.user_id) == remote(HeartRateDaily.user_id),
            func.date(HeartRateReading.timestamp)
            == func.date(remote(HeartRateDaily.date)),
        ),
        uselist=False,
    )

    user = relationship("User", backref="heart_rate_readings", viewonly=True)
