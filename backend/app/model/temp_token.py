from sqlalchemy import Column, DateTime, String

from core.db import Base, TimeStampMixin


class TempClientToken(Base, TimeStampMixin):
    __tablename__ = "temp_client_tokens"

    client_id = Column(String, primary_key=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
