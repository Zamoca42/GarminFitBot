from sqlalchemy import BigInteger, Column, String, Text
from sqlalchemy.orm import relationship

from core.db import Base, TimeStampMixin


class User(Base, TimeStampMixin):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True)  # garmin profile_id를 id로 사용
    email = Column(String(255), unique=True, nullable=False)
    display_name = Column(String(255))
    full_name = Column(String(255))
    oauth_token = Column(Text, nullable=False)
    oauth_token_secret = Column(Text, nullable=False)
    domain = Column(String(255), nullable=True)
    kakao_client_id = Column(String(255), nullable=True)

    # 관계 정의
    heart_rate_dailies = relationship(
        "HeartRateDaily", cascade="all, delete-orphan", back_populates="user"
    )
    stress_dailies = relationship(
        "StressDaily", cascade="all, delete-orphan", back_populates="user"
    )
    steps_dailies = relationship(
        "StepsDaily", cascade="all, delete-orphan", back_populates="user"
    )
    sleep_sessions = relationship(
        "SleepSession", cascade="all, delete-orphan", back_populates="user"
    )
    activities = relationship(
        "Activity", cascade="all, delete-orphan", back_populates="user"
    )
