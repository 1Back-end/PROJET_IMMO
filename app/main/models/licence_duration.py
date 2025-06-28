from datetime import datetime, timezone, date
from enum import Enum

from sqlalchemy import Column, ForeignKey, String, Text, DateTime, Boolean, Integer, func, String, Date
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY
from app.main.models.db.base_class import Base
from sqlalchemy.orm import relationship


class LicenceDuration(Base):
    __tablename__ = 'licence_duration'

    uuid: str = Column(String, primary_key=True)
    key: str = Column(String, nullable=False)
    duration_days: int = Column(Integer, nullable=False)
    description: str = Column(String, nullable=True)
    is_active: bool = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())