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


class StressDaily(Base, TimeStampMixin):
    __tablename__ = "stress_daily"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False)
    avg_stress_level = Column(Integer)
    max_stress_level = Column(Integer)
    stress_duration_seconds = Column(Integer)
    rest_duration_seconds = Column(Integer)

    # 해당 일자의 상세 측정값들과 관계 설정
    readings = relationship(
        "StressReading",
        back_populates="daily_summary",
        uselist=True,
    )

    user = relationship("User", backref="stress_dailies")


class StressReading(Base):
    __tablename__ = "stress_readings"
    __table_args__ = (
        PrimaryKeyConstraint("daily_summary_id", "start_time_local"),
        {"postgresql_partition_by": "RANGE (start_time_local)"},
    )

    daily_summary_id = Column(BigInteger, ForeignKey("stress_daily.id"), nullable=False)
    start_time_gmt = Column(DateTime(timezone=True), nullable=False)
    start_time_local = Column(DateTime(timezone=False), nullable=False)
    stress_level = Column(Integer)

    # 해당 측정값의 일일 요약과 관계 설정
    daily_summary = relationship(
        "StressDaily",
        back_populates="readings",
        uselist=False,
    )
