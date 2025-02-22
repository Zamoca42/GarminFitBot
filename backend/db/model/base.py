from datetime import datetime, timezone
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, DateTime

Base = declarative_base()

class TimeStampMixin:
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc)) 