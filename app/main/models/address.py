from datetime import datetime
from sqlalchemy import Column, ForeignKey, String, Text, DateTime, Boolean,Integer, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY
from app.main.models.db.base_class import Base


class Address(Base):
    
    """ Address Model for storing user addresses related details """

    __tablename__ = "addresses"
    
    uuid = Column(String, primary_key=True, unique=True)

    street: str = Column(String, nullable=False, default="")
    city: str = Column(String, nullable=False, default="")
    state: str = Column(String, default="")
    zipcode: str = Column(String, nullable=False, default="")
    country: str = Column(String, nullable=False, default="")
    apartment_number: str = Column(String, default="")
    additional_information: str = Column(String, default="")
     
    date_added: any = Column(DateTime, server_default=func.now())
    date_modified: any = Column(DateTime, server_default=func.now())


