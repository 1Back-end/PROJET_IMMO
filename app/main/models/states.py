from datetime import datetime
from operator import index

from sqlalchemy import Column, ForeignKey, String, Text, DateTime, Boolean,Integer, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY
from app.main.models.db.base_class import Base



class States(Base):
    __tablename__ = "states"

    uuid : str = Column(String, primary_key=True,index=True)
    code : str = Column(String,nullable=True,index=True)
    name : str = Column(String,nullable=True,index=True)
    is_deleted : bool = Column(Boolean,nullable=True,index=True,default=False)
    created_at = Column(DateTime, default=func.now())  # Account creation timestamp
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())  # Last update timestamp