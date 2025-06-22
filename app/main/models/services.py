from dataclasses import dataclass
from email.policy import default

from sqlalchemy.sql import func
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql.json import JSONB
from sqlalchemy import Column, ForeignKey, Integer, String, Text, DateTime, Boolean
from sqlalchemy import event
from app.main.models.db.base_class import Base
from enum import Enum


class ServiceStatus(str, Enum):
    active = 'active'
    inactive = 'inactive'

class Service(Base):
    __tablename__ = 'services'

    uuid : str = Column(String, primary_key=True,index=True)
    name : str = Column(String, index=True,unique=True,nullable=False)
    description : str = Column(String, index=True,nullable=True)
    status : str = Column(String,default=ServiceStatus.active, index=True,nullable=False)
    is_deleted : bool = Column(Boolean,default=False,nullable=False)

    added_by = Column(String, ForeignKey("users.uuid"), nullable=False)
    creator = relationship("User", foreign_keys=[added_by])

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    #def __init__(self):
        #return  f"Service(uuid={self.uuid}, name={self.name}, description={self.description}, status={self.status})"