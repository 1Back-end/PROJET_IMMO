import math
import bcrypt
from fastapi import HTTPException
from sqlalchemy import or_
import re
from typing import List, Optional, Union
import uuid
from app.main.core.i18n import __
from sqlalchemy.orm import Session
from app.main.crud.base import CRUDBase
from app.main import models,schemas

class CRUDAddress(CRUDBase[models.Address,schemas.AddressBase,schemas.AddressUpdate]):

    def get_by_uuid(cls,db:Session,*,uuid:str):
        return db.query(models.Address).filter(models.Address.uuid == uuid).first()
    
    def create(cls,db:Session,*,obj_in:schemas.AddressCreate):
        new_address = models.Address(
            uuid = str(uuid.uuid4()),
            street= obj_in.street,
            city= obj_in.city,
            state= obj_in.state,
            zipcode= obj_in.zipcode,
            country= obj_in.country,
            apartment_number= obj_in.apartment_number,
            additional_information= obj_in.additional_information
        )
        db.add(new_address)
        db.commit()
        db.refresh(new_address)
        return new_address
    
    def update(cls,db:Session,*,obj_in:schemas.AddressUpdate):
        address = cls.get_by_uuid(db=db,uuid=obj_in.uuid)
        if address is None:
            raise HTTPException(status_code=404,detail=__(key="address-not-found"))
        address.street = obj_in.street if obj_in.street else address.street
        address.city = obj_in.city if obj_in.city else address.city
        address.state = obj_in.state if obj_in.state else address.state
        address.zipcode = obj_in.zipcode if obj_in.zipcode else address.zipcode
        address.country = obj_in.country if obj_in.country else address.country
        address.apartment_number = obj_in.apartment_number if obj_in.apartment_number else address.apartment_number
        address.additional_information = obj_in.additional_information if obj_in.additional_information else address.additional_information
        db.flush()
        db.commit()
        db.refresh(address)
        return address
    
address = CRUDAddress(models.Address)