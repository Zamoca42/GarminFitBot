from sqlalchemy import Column, Integer, String, JSON
from .base import Base, TimeStampMixin

class User(Base, TimeStampMixin):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    garmin_tokens = Column(JSON) 