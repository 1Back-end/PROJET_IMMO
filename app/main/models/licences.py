from datetime import datetime,timezone
from enum import Enum

from sqlalchemy import Column, ForeignKey, String, Text, DateTime, Boolean,Integer, func,String
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY
from app.main.models.db.base_class import Base
from sqlalchemy.orm import relationship

class LicenceStatus(str, Enum):
    pending = "pending"
    active = "active"
    expired = "expired"
    revoked = "revoked"

class License(Base):
    __tablename__ = 'licenses'
    uuid = Column(String, primary_key=True)
    license_key = Column(String, unique=True, nullable=False)

    organization_uuid = Column(String, ForeignKey("organisations.uuid",onupdate="CASCADE",ondelete="CASCADE"),nullable=False)
    organisation = relationship("Organisation", foreign_keys=[organization_uuid], backref="licenses")

    service_uuid = Column(String, ForeignKey("services.uuid",onupdate="CASCADE",ondelete="CASCADE"),nullable=False)
    service = relationship("Service", foreign_keys=[service_uuid], backref="licenses")

    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    status = Column(String, nullable=False,default=LicenceStatus.pending)
    encrypted_data = Column(Text, nullable=True)

    added_by = Column(String, ForeignKey("users.uuid"), nullable=False)
    creator = relationship("User", foreign_keys=[added_by],backref="licenses")

    is_deleted = Column(Boolean, nullable=False, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    @hybrid_property
    def remaining_days(self):
        if self.end_date and self.end_date > datetime.now(timezone.utc):
            return (self.end_date - datetime.now(timezone.utc)).days
        return 0

    @property
    def dynamic_status(self):
        if self.status == LicenceStatus.revoked:
            return LicenceStatus.revoked
        elif self.end_date < datetime.now(timezone.utc):
            return LicenceStatus.expired
        return LicenceStatus.active

    def update_status_from_dates(self):
        if self.status == LicenceStatus.revoked.value:
            return
        if self.end_date < datetime.now(timezone.utc):
            self.status = LicenceStatus.expired.value
        else:
            self.status = LicenceStatus.active.value

