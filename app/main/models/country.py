from datetime import datetime
from sqlalchemy import Column, ForeignKey, String, Text, DateTime, Boolean, Integer, func, Float
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY
from app.main.models.db.base_class import Base


class Country(Base):
    __tablename__ = "countries"

    uuid = Column(String, primary_key=True, index=True)
    code = Column(String, index=True, nullable=True)
    name = Column(String, index=True, nullable=True)

    is_deleted = Column(Boolean, nullable=True, index=True, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relations
    cities = relationship("City", back_populates="country", cascade="all, delete",passive_deletes=True)
    organisations = relationship("Organisation", back_populates="country",cascade="all, delete",passive_deletes=True)



class City(Base):
    __tablename__ = "cities"

    uuid = Column(String, primary_key=True, index=True)
    name = Column(String, index=True, nullable=True)
    latitude = Column(Float, index=True, nullable=True)
    longitude = Column(Float, index=True, nullable=True)
    altitude = Column(Float, index=True, nullable=True)

    country_uuid = Column(String, ForeignKey("countries.uuid", ondelete="CASCADE", onupdate="CASCADE"), nullable=True)
    is_deleted = Column(Boolean, nullable=True, index=True, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relations
    country = relationship("Country", back_populates="cities")
    organisations = relationship("Organisation", back_populates="city")

