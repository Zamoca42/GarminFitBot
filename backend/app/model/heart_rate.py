from sqlalchemy import (
    BigInteger,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    PrimaryKeyConstraint,
)
from sqlalchemy.orm import relationship

from core.db import Base, TimeStampMixin


class HeartRateDaily(Base, TimeStampMixin):
    __tablename__ = "heart_rate_daily"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    date = Column(Date, nullable=False)
    resting_hr = Column(Integer)
    max_hr = Column(Integer)
    min_hr = Column(Integer)
    avg_hr = Column(Integer)

    # 해당 일자의 상세 측정값들과 관계 설정
    readings = relationship(
        "HeartRateReading",
        back_populates="daily_summary",
        cascade="all, delete-orphan",
        uselist=True,
    )

    user = relationship("User", back_populates="heart_rate_dailies")


class HeartRateReading(Base):
    __tablename__ = "heart_rate_readings"
    __table_args__ = (
        PrimaryKeyConstraint("daily_summary_id", "start_time_local"),
        {"postgresql_partition_by": "RANGE (start_time_local)"},
    )

    daily_summary_id = Column(
        BigInteger,
        ForeignKey("heart_rate_daily.id", ondelete="CASCADE"),
        nullable=False,
    )
    start_time_gmt = Column(DateTime(timezone=True), nullable=False)
    start_time_local = Column(DateTime(timezone=False), nullable=False)
    heart_rate = Column(Integer)

    # 해당 측정값의 일일 요약과 관계 설정
    daily_summary = relationship(
        "HeartRateDaily",
        back_populates="readings",
        uselist=False,
    )
