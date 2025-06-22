from datetime import datetime
from sqlalchemy import Column, ForeignKey, String, Text, DateTime, Boolean,Integer, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY
from app.main.models.db.base_class import Base



class LicenceRequest(Base):
    __tablename__ = "notifications"

    uuid = Column(String, primary_key=True,index=True)

    title = Column(String,nullable=False)
    description = Column(String,nullable=False)
    is_deleted = Column(Boolean,nullable=False,default=False)
    is_read = Column(Boolean,nullable=False,default=False)
    send_by = Column(String,ForeignKey("users.uuid"), nullable=False)
    type = Column(String,nullable=True,index=True)
    sender = relationship("User", foreign_keys=[send_by])
    created_at = Column(DateTime,nullable=False,default=datetime.utcnow)
    updated_at = Column(DateTime,nullable=False,default=datetime.utcnow)
    