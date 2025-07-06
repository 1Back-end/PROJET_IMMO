import math
import os
from datetime import datetime, date, timedelta

import bcrypt
from fastapi import HTTPException
from sqlalchemy import or_
import re
from typing import List, Optional, Union
import uuid
from app.main.core.i18n import __
from sqlalchemy.orm import Session
from app.main.core.mail import notify_owner_new_licence
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

        data_to_sign = f"{license_key}|{request.organization_uuid}|{request.service_uuid}|{request.licence_duration_uuid}".encode("utf-8")

        signature = cls.sign_license_data(data_to_sign)



        db_obj = models.License(
            uuid=str(uuid.uuid4()),
            license_key=license_key,
            organization_uuid=request.organization_uuid,
            service_uuid=request.service_uuid,
            licence_duration_uuid=request.licence_duration_uuid,
            encrypted_data=signature,
            added_by=added_by
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        cert_dir = "certificats"
        os.makedirs(cert_dir, exist_ok=True)

        # S'assurer que la signature est encodée en base64 au format PEM
        pem_signature = base64.b64encode(signature.encode("utf-8")).decode('utf-8')
        pem_formatted = f"-----BEGIN CERTIFICATE-----\n{pem_signature}\n-----END CERTIFICATE-----"

        cer_filename = f"{license_key}.txt"
        cer_path = os.path.join(cert_dir, cer_filename)

        # Écriture dans le fichier .cer
        with open(cer_path, "w", encoding="utf-8") as f:
            f.write(pem_formatted)

        #organisation = db.query(models.Organisation).filter(
            #models.Organisation.uuid == request.organization_uuid
        #).join(models.User).first()

        #if not organisation:
            #raise HTTPException(status_code=404, detail="Organisation not found")

        #owner = organisation.owner

        #notify_owner_new_licence(
            #email_to=owner.email,
            #name=f"{owner.first_name} {owner.last_name}",
            #licence=signature,
            #service=db_obj.service.name
        #)
        new_notification = models.LicenceRequest(
            uuid=str(uuid.uuid4()),
            title="Licence Générée",
            type="Demande de licence",
            description="Nouvelle licence générée",
            send_by=added_by
        )
        db.add(new_notification)
        db.commit()
        db.refresh(new_notification)
        return db_obj

    @classmethod
    def activate_service(cls, db: Session, *, service_uuid: str, licence_uuid: str, encrypted_data: str) -> Optional[
        models.License]:

        db_service = crud.services.get_by_uuid(db=db, uuid=service_uuid)
        if not db_service:
            raise HTTPException(status_code=404, detail=__(key="service-not-found"))

        if db_service.status == models.ServiceStatus.inactive:
            raise HTTPException(status_code=400, detail=__(key="service-inactive"))

        db_licence = cls.get_by_uuid(db=db, uuid=licence_uuid)
        if not db_licence:
            raise HTTPException(status_code=404, detail=__(key="licence-not-found"))

        if db_licence.status == models.LicenceStatus.expired:
            raise HTTPException(status_code=400, detail=__(key="licence-status-expired"))

        if db_licence.status == models.LicenceStatus.revoked:
            raise HTTPException(status_code=400, detail=__(key="licence-status-revoked"))

        db_licence.status = models.LicenceStatus.active
        db_licence.expires_at = datetime.utcnow() + timedelta(days=db_licence.licence_duration.duration_days)
        db_licence.encrypted_data = encrypted_data

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


    @classmethod
    def revoke_licence(cls,db:Session,*,licence_uuid:str,service_uuid:str) -> Optional[models.License]:
        db_service = crud.services.get_by_uuid(db=db, uuid=service_uuid)
        if not db_service:
            raise HTTPException(status_code=404, detail=__(key="service-not-found"))

        if db_service.status == models.ServiceStatus.inactive:
            raise HTTPException(status_code=400, detail=__(key="service-inactive"))

        db_licence = cls.get_by_uuid(db=db, uuid=licence_uuid)
        if not db_licence:
            raise HTTPException(status_code=404, detail=__(key="licence-not-found"))

        if db_licence.end_date < date.today():
            raise HTTPException(status_code=400, detail=__(key="licence-expired"))
        db_licence.status = models.ServiceStatus.inactive
        db.commit()


    @classmethod
    def soft_delete(cls,db:Session,*,uuid:str):
        obj_in = cls.get_by_uuid(db=db, uuid=uuid)
        if not obj_in:
            raise HTTPException(status_code=404, detail=__(key="licence-not-found"))
        obj_in.is_deleted = True
        db.commit()

    @classmethod
    def drop_delete(cls,db:Session,*,uuid:str):
        obj_in = cls.get_by_uuid(db=db, uuid=uuid)
        if not obj_in:
            raise HTTPException(status_code=404, detail=__(key="licence-not-found"))
        db.delete(obj_in)
        db.commit()

    @classmethod
    def get_all_licence(
            cls,
            db: Session,
            page: int = 1,
            per_page: int = 30,
            order: Optional[str] = None,
            order_field: Optional[str] = None,
            keyword: Optional[str] = None,
            status: Optional[str] = None,
    ):
        record_query = db.query(models.License).filter(models.License.is_deleted == False).order_by(models.License.created_at.desc())

        if keyword:
            record_query = record_query.filter(
                or_(
                    models.License.license_key.ilike(f'%{keyword}%'),
                    models.License.encrypted_data.ilike(f'%{keyword}%')

                )
            )
        if order and order_field and hasattr(models.License, order_field):
            if order == "asc":
                record_query = record_query.order_by(getattr(models.LicenceRequest, order_field).asc())
            else:
                record_query = record_query.order_by(getattr(models.License, order_field).desc())
        if status:
            record_query = record_query.filter(models.License.status == status)

        total = record_query.count()

        record_query = record_query.offset((page - 1) * per_page).limit(per_page).all()

        return schemas.LicenceResponseList(
            total=total,
            pages=math.ceil(total / per_page),
            per_page=per_page,
            current_page=page,
            data=record_query
        )

    @classmethod
    def get_all_my_licence(
            cls,
            db: Session,
            owner_uuid: Optional[str] = None,
            page: int = 1,
            per_page: int = 30,
            order: Optional[str] = None,
            order_field: Optional[str] = None,
            keyword: Optional[str] = None,
            status: Optional[str] = None,
    ):
        # On fait la jointure License -> Organisation
        record_query = db.query(models.License).join(models.Organisation).filter(
            models.License.is_deleted == False
        ).order_by(models.License.created_at.desc())

        if owner_uuid:
            record_query = record_query.filter(models.Organisation.owner_uuid == owner_uuid)

        if keyword:
            record_query = record_query.filter(
                or_(
                    models.License.license_key.ilike(f'%{keyword}%'),
                    models.License.encrypted_data.ilike(f'%{keyword}%')
                )
            )

        if order and order_field and hasattr(models.License, order_field):
            if order == "asc":
                record_query = record_query.order_by(getattr(models.License, order_field).asc())
            else:
                record_query = record_query.order_by(getattr(models.License, order_field).desc())

        if status:
            record_query = record_query.filter(models.License.status == status)

        total = record_query.count()

        record_query = record_query.offset((page - 1) * per_page).limit(per_page).all()

        return schemas.LicenceResponseList(
            total=total,
            pages=math.ceil(total / per_page),
            per_page=per_page,
            current_page=page,
            data=record_query
        )

    @classmethod
    def revoke_licence(cls,db:Session,*,uuid:str):
        db_obj = cls.get_by_uuid(db=db, uuid=uuid)
        if not db_obj:
            raise HTTPException(status_code=404, detail=__(key="licence-not-found"))
        db_obj.status = models.LicenceStatus.revoked
        db.commit()

    @classmethod
    def prolonge_licence(cls, db: Session, *, uuid: str, number_of_days: int):
        db_obj = cls.get_by_uuid(db=db, uuid=uuid)
        if not db_obj:
            raise HTTPException(status_code=404, detail=__(key="licence-not-found"))
        now = datetime.utcnow()
        if db_obj.expires_at and db_obj.expires_at > now:
            db_obj.expires_at += timedelta(days=number_of_days)
        else:
            db_obj.expires_at = now + timedelta(days=number_of_days)

        db_obj.status = models.LicenceStatus.prolonged
        db.commit()
        db.refresh(db_obj)
        return db_obj





licence = CRUDLicenses(models.License)