from sqlalchemy import BigInteger, Column, String, Text

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
