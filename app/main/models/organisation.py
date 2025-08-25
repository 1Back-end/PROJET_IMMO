from sqlalchemy.sql import func
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy import Column, ForeignKey, String, DateTime, Boolean, nullslast
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

    country_uuid = Column(String, ForeignKey('countries.uuid', ondelete="SET NULL", onupdate="CASCADE"), nullable=True, index=True)
    city_uuid = Column(String, ForeignKey("cities.uuid", ondelete="SET NULL", onupdate="CASCADE"), nullable=True, index=True)

    owner_uuid = Column(String, ForeignKey("users.uuid", ondelete="SET NULL", onupdate="CASCADE"), nullable=False, index=True)

    # Relations
    country = relationship("Country", back_populates="organisations", passive_deletes=True)
    city = relationship("City", back_populates="organisations",passive_deletes=True)
    owner = relationship("User", back_populates="organisations", passive_deletes=True)
    owner_services = relationship("OrganisationOwnerService", back_populates="organisation", cascade="all, delete-orphan")

    validation_account_otp = Column(String, nullable=True)
    validation_otp_expirate_at = Column(DateTime, nullable=True)

    additional_information: str = Column(String, default="",nullable=True)

    status = Column(String, nullable=False, default=OrganisationStatus.inactive.value)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    is_deleted = Column(Boolean, default=False, nullable=False)


class OrganisationOwnerService(Base):
    __tablename__ = "organisation_owner_service"

    uuid = Column(String, primary_key=True, index=True)

    owner_uuid = Column(String, ForeignKey("users.uuid", ondelete="SET NULL", onupdate="CASCADE"), nullable=False, index=True)
    organisation_uuid = Column(String, ForeignKey("organisations.uuid", ondelete="SET NULL", onupdate="CASCADE"), nullable=False, index=True)
    service_uuid = Column(String, ForeignKey("services.uuid", ondelete="SET NULL", onupdate="CASCADE"), nullable=False, index=True)

    # Relations
    owner = relationship("User", backref="organisation_services", passive_deletes=True)
    organisation = relationship("Organisation", back_populates="owner_services", passive_deletes=True)
    service = relationship("Service", backref="organisation_owners", passive_deletes=True)

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    is_deleted = Column(Boolean, default=False, nullable=False)
