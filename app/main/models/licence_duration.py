from datetime import datetime, timezone, date
from enum import Enum

from sqlalchemy import Column, ForeignKey, String, Text, DateTime, Boolean, Integer, func, String, Date, Float
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
    price : float = Column(Float, nullable=True)
    description: str = Column(String, nullable=True)
    is_active: bool = Column(Boolean, default=True)
    is_deleted: bool = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    added_by = Column(String, ForeignKey("users.uuid"), nullable=True)
    creator = relationship("User", foreign_keys=[added_by])
