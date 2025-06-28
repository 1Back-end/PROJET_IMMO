from datetime import datetime, timezone, date
from enum import Enum

from sqlalchemy import Column, ForeignKey, String, Text, DateTime, Boolean, Integer, func, String, Date
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
    deleted = "deleted"
    prolonged = "prolonged"

class License(Base):
    __tablename__ = 'licenses'
    uuid = Column(String, primary_key=True)
    license_key = Column(String, unique=True, nullable=False)

    organization_uuid = Column(String, ForeignKey("organisations.uuid",onupdate="CASCADE",ondelete="CASCADE"),nullable=False)
    organisation = relationship("Organisation", foreign_keys=[organization_uuid], backref="licenses")

    service_uuid = Column(String, ForeignKey("services.uuid",onupdate="CASCADE",ondelete="CASCADE"),nullable=False)
    service = relationship("Service", foreign_keys=[service_uuid], backref="licenses")

    licence_duration_uuid = Column(String, ForeignKey("licence_duration.uuid", onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    licence_duration = relationship("LicenceDuration", foreign_keys=[licence_duration_uuid], backref="licenses")

    status = Column(String, nullable=False,default=LicenceStatus.pending)
    encrypted_data = Column(Text, nullable=True)

    added_by = Column(String, ForeignKey("users.uuid"), nullable=False)
    creator = relationship("User", foreign_keys=[added_by],backref="licenses")
    expires_at = Column(DateTime, nullable=True)

    is_deleted = Column(Boolean, nullable=False, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    @hybrid_property
    def is_expired(self):
        if self.status != "active":
            return False
        if not self.expires_at:
            return None  # renvoie None si la date est vide
        return datetime.utcnow() > self.expires_at




