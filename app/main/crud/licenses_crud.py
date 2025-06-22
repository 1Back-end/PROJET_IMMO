import math
from datetime import datetime

import bcrypt
from fastapi import HTTPException
from sqlalchemy import or_
import re
from typing import List, Optional, Union
import uuid
from app.main.core.i18n import __
from sqlalchemy.orm import Session
from app.main.crud.base import CRUDBase
from app.main import models,schemas,crud
from app.main.core.security import  generate_license_key
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives import serialization
import base64



class CRUDLicenses(CRUDBase[models.License,schemas.LicenceCreate,schemas.LicenseResponse]):
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    @classmethod
    def get_by_uuid(cls,db:Session,*,uuid:str) -> Optional[models.License]:
        return db.query(models.License).filter(models.License.uuid == uuid,models.License.is_deleted==False).first()

    @classmethod
    def get_by_organisation(cls,db:Session,*,organisation_uuid:str) -> Optional[models.License]:
        return db.query(models.License).filter(models.License.organization_uuid==organisation_uuid,models.License.is_deleted==False).all()

    @classmethod
    def sign_license_data(cls, data: bytes) -> str:
        signature = cls.private_key.sign(
            data,
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        return base64.b64encode(signature).decode()

    @classmethod
    def create(cls, db: Session, *, request: schemas.LicenceCreate, added_by: str) -> Optional[models.License]:
        license_key = generate_license_key()

        data_to_sign = f"{license_key}|{request.organization_uuid}|{request.service_uuid}|{request.start_date}|{request.end_date}".encode("utf-8")

        signature = cls.sign_license_data(data_to_sign)

        db_obj = models.License(
            uuid=str(uuid.uuid4()),
            license_key=license_key,
            organization_uuid=request.organization_uuid,
            service_uuid=request.service_uuid,
            start_date=request.start_date,
            end_date=request.end_date,
            encrypted_data=signature,
            added_by=added_by,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @classmethod
    def activate_service(cls, db: Session, *, service_uuid: str, licence_uuid: str) -> Optional[models.License]:
        db_service = crud.services.get_by_uuid(db=db, uuid=service_uuid)
        if not db_service:
            raise HTTPException(status_code=404, detail=__(key="service-not-found"))

        if db_service.status == models.ServiceStatus.inactive:
            raise HTTPException(status_code=400, detail=__(key="service-inactive"))

        db_licence = cls.get_by_uuid(db=db, uuid=licence_uuid)
        if not db_licence:
            raise HTTPException(status_code=404, detail=__(key="licence-not-found"))

        if db_service.organization_uuid != db_licence.organization_uuid:
            raise HTTPException(status_code=400, detail=__(key="licence-organization-mismatch"))

        if db_service.service_uuid != db_licence.service_uuid:
            raise HTTPException(status_code=400, detail=__(key="licence-service-mismatch"))

        if db_licence.end_date < datetime.utcnow():
            raise HTTPException(status_code=400, detail=__(key="licence-expired"))

        if db_licence.status == models.LicenceStatus.expired:
            raise HTTPException(status_code=400, detail=__(key="licence-status-expired"))

        if db_licence.status == models.LicenceStatus.revoked:
            raise HTTPException(status_code=400, detail=__(key="licence-status-revoked"))

        db_service.status = models.ServiceStatus.active
        db.commit()


    @classmethod
    def renouvel_licence(cls,db:Session,*,licence_uuid:str,new_start_date:datetime) -> Optional[models.License]:
        db_licence = cls.get_by_uuid(db=db, uuid=licence_uuid)
        if not db_licence:
            raise HTTPException(status_code=404, detail=__(key="licence-not-found"))

        if db_licence.status == models.LicenceStatus.revoked:
            raise HTTPException(status_code=400, detail=__(key="licence-status-revoked"))

        today = datetime.utcnow()
        old_end_date = db_licence.end_date

        if old_end_date < today:
            raise HTTPException(status_code=400, detail=__(key="licence-already-expired"))

        remaining_duration = old_end_date - today

        new_end_date = new_start_date + remaining_duration

        db_licence.end_date = new_end_date
        db.commit()





licence = CRUDLicenses(models.License)