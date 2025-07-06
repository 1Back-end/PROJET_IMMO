from datetime import datetime
from sqlalchemy import Column, ForeignKey, String, Text, DateTime, Boolean,Integer, func
from sqlalchemy.orm import relationship
from app.main.models.db.base_class import Base
from enum import Enum


class LicenceRequqestStatus(str,Enum):
    pending = "pending"
    accepted = "accepted"
    declined = "declined"

class LicenceRequest(Base):
    __tablename__ = "notifications"

    uuid = Column(String, primary_key=True,index=True)

    title = Column(String,nullable=False)
    description = Column(String,nullable=True)
    is_deleted = Column(Boolean,nullable=False,default=False)
    is_read = Column(Boolean,nullable=False,default=False)

    send_by = Column(String,ForeignKey("users.uuid"), nullable=False)
    owner = relationship("User", foreign_keys=[send_by])

    type = Column(String,nullable=True,index=True)

    status = Column(String,nullable=True,index=True,default=LicenceRequqestStatus.pending)
    created_at = Column(DateTime,nullable=False,default=datetime.utcnow)
    updated_at = Column(DateTime,nullable=False,default=datetime.utcnow)
    