from datetime import datetime
from email.policy import default

from sqlalchemy import Column, ForeignKey, String, Text, DateTime, Boolean,Integer, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY
from app.main.models.db.base_class import Base
from enum import Enum

class LicenceRequestServiceStatus(str,Enum):
    pending = "pending"
    accepted = "accepted"
    declined = "declined"
    prolonged = "prolonged"

    

class LicenceRequestService(Base):
    __tablename__ = 'licence_request_services'


    uuid:str = Column(String, primary_key=True,index=True)

    service_uuid = Column(String, ForeignKey("services.uuid", ondelete="SET NULL", onupdate="CASCADE"), nullable=False)
    service = relationship("Service", foreign_keys=[service_uuid], backref="licence_request_services")

    licence_duration_uuid = Column(String, ForeignKey("licence_duration.uuid", ondelete="SET NULL", onupdate="CASCADE"),nullable=False)
    licence_duration = relationship("LicenceDuration", foreign_keys=[licence_duration_uuid], backref="licence_request_services")

    licence_uuid = Column(String,ForeignKey("licenses.uuid", ondelete="SET NULL", onupdate="CASCADE",use_alter=True),nullable=True)
    licence = relationship("License",foreign_keys=[licence_uuid],  backref="licence_request_services")

    status = Column(String, nullable=False, default=LicenceRequestServiceStatus.pending)

    type = Column(String, nullable=False)


    added_by = Column(String, ForeignKey("users.uuid",ondelete="SET NULL", onupdate="CASCADE"), nullable=False)
    creator = relationship("User", foreign_keys=[added_by], backref="licence_request_services")

    description:str = Column(Text, nullable=True)

    counter_generation:int = Column(Integer, nullable=True,default=0)
    counter_prolongation = Column(Integer, nullable=True,default=0)

    is_accepted = Column(Boolean, nullable=True,default=False)
    is_prolonged = Column(Boolean, nullable=True,default=False)


    is_deleted = Column(Boolean, nullable=False, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)