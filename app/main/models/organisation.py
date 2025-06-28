
from sqlalchemy.sql import func
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy import Column, ForeignKey, Integer, String, Text, DateTime, Boolean
from app.main.models.db.base_class import Base
from enum import Enum

class OrganisationStatus(str, Enum):
    active = "active"
    inactive = "inactive"
    closed = "closed"

class Organisation(Base):
    __tablename__ = 'organisations'

    uuid = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    email = Column(String, nullable=False, index=True)
    phone_number = Column(String, nullable=False, index=True)
    description = Column(String, nullable=True, index=True)
    address_uuid = Column(String, ForeignKey("address.uuid", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    owner_uuid = Column(String, ForeignKey("users.uuid", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)

    # Relations
    address = relationship("Address", backref="organisations")
    owner = relationship("User", back_populates="organisations")
    owner_services = relationship("OrganisationOwnerService", back_populates="organisation")

    status = Column(String, nullable=False, default=OrganisationStatus.inactive)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    is_deleted = Column(Boolean, default=False)

class OrganisationOwnerService(Base):
    __tablename__ = "organisation_owner_service"

    uuid = Column(String, primary_key=True, index=True)

    owner_uuid = Column(String, ForeignKey("users.uuid", ondelete="CASCADE"), nullable=False)
    organisation_uuid = Column(String, ForeignKey("organisations.uuid", ondelete="CASCADE"), nullable=False)
    service_uuid = Column(String, ForeignKey("services.uuid", ondelete="CASCADE"), nullable=False)

    # Relations
    owner = relationship("User", backref="organisation_services")
    organisation = relationship("Organisation", back_populates="owner_services")
    service = relationship("Service", backref="organisation_owners")

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    is_deleted = Column(Boolean, default=False)
