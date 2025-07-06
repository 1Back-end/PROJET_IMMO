from dataclasses import dataclass
from sqlalchemy.sql import func
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql.json import JSONB
from sqlalchemy import Column, ForeignKey, Integer, String, Text, DateTime, Boolean
from sqlalchemy import event
from app.main.models.db.base_class import Base
from enum import Enum


class UserRole(str, Enum):
    ADMIN = "ADMIN"
    EDIMESTRE = "EDIMESTRE"
    SUPER_ADMIN = "SUPER_ADMIN"
    OWNER = "OWNER"
    

class UserStatus(str, Enum):
    ACTIVED = "ACTIVED"
    UNACTIVED = "UNACTIVED"
    BLOCKED = "BLOCKED"


class User(Base):

    __tablename__ = "users"

    uuid = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    phone_number = Column(String(20), nullable=False, default="", index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False, default=UserRole.ADMIN)
    otp = Column(String(5), nullable=True, default="")
    otp_expired_at = Column(DateTime, nullable=True, default=None)  # OTP expiration date
    otp_password = Column(String(5), nullable=True, default="")  # OTP password
    otp_password_expired_at = Column(DateTime, nullable=True, default=None)  # OTP password expiration date
    status = Column(String, nullable=False, default=UserStatus.ACTIVED)  # User status
    created_at = Column(DateTime, default=func.now())  # Account creation timestamp
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())  # Last update timestamp
    is_deleted = Column(Boolean, default=False)  # Soft delete flag

    avatar_uuid: str = Column(String, ForeignKey('storages.uuid', ondelete="CASCADE", onupdate="CASCADE"),
                              nullable=True)
    avatar = relationship("Storage", foreign_keys=[avatar_uuid])

    login = Column(String, nullable=True)
    is_new_user = Column(Boolean, default=True)
    first_login_date = Column(DateTime, nullable=True, default=None)
    last_login_date = Column(DateTime, nullable=True, default=None)
    connexion_counter = Column(Integer, nullable=True, default=0)

    organisations = relationship("Organisation", back_populates="owner", uselist=False)


    def __repr__(self):
        return f"User('{self.first_name} {self.last_name}', '{self.email}')"



class UserActionValidation(Base):
    __tablename__ = 'user_action_validations'

    uuid: str = Column(String, primary_key=True)

    user_uuid: str = Column(String, ForeignKey('users.uuid'), nullable=True)
    code: str = Column(String, unique=False, nullable=True)
    expired_date: any = Column(DateTime, default=datetime.now())
    value: str = Column(String, default="", nullable=True)

    date_added: any = Column(DateTime, nullable=False, default=datetime.now())


