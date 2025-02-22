from sqlalchemy import Column, String, JSON, BigInteger
from .base import Base, TimeStampMixin

class User(Base, TimeStampMixin):
    __tablename__ = 'users'

    id = Column(BigInteger, primary_key=True)  # garmin profile_id를 id로 사용
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    display_name = Column(String(255))
    full_name = Column(String(255))