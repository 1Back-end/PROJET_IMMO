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
from app.main.schemas import LicenceRequestCreate


class CRUDLicenceRequestCRUD(CRUDBase[models.LicenceRequest, schemas.LicenceRequestCreate,schemas.LicenseRequest]):

    @classmethod
    def get_by_uuid(cls,db:Session,*,uuid:str) -> Optional[models.LicenceRequest]:
        return db.query(models.LicenceRequest).filter(models.LicenceRequest.uuid == uuid,models.LicenceRequest.is_deleted==False).first()

    @classmethod
    def create(cls,db:Session,obj_in:schemas.LicenceRequestCreate,send_by:str) -> Optional[models.LicenceRequest]:
        db_obj = models.LicenceRequest(
            uuid=str(uuid.uuid4()),
            title = obj_in.title,
            description = obj_in.description,
            send_by = send_by
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @classmethod
    def change_is_read(cls,db:Session,*,uuid:str) -> Optional[models.LicenceRequest]:
        db_obj = cls.get_by_uuid(db=db,uuid=uuid)
        if not db_obj:
            raise HTTPException(status_code=404,detail=__(key="licence-request-not-found"))
        db_obj.is_read = True
        db.commit()

    @classmethod
    def delete(cls,db:Session,*,uuid:str) -> Optional[models.LicenceRequest]:
        db_obj = cls.get_by_uuid(db=db,uuid=uuid)
        if not db_obj:
            raise HTTPException(status_code=404,detail=__(key="licence-request-not-found"))
        db.delete(db_obj)
        db.commit()

    @classmethod
    def soft_delete(cls,db:Session,*,uuid:str) -> Optional[models.LicenceRequest]:
        db_obj = cls.get_by_uuid(db=db,uuid=uuid)
        if not db_obj:
            raise  HTTPException(status_code=404,detail=__(key="licence-request-not-found"))
        db_obj.is_deleted = True
        db.commit()

    @classmethod
    def get_many(
            cls,
            db: Session,
            page: int = 1,
            per_page: int = 25,
    ):
        record_query = db.query(models.LicenceRequest).filter(models.LicenceRequest.is_deleted == False)

        total = record_query.count()

        record_query = record_query.offset((page - 1) * per_page).limit(per_page)

        return schemas.LicenceRequestResponseList(
            total=total,
            pages=math.ceil(total / per_page),
            per_page=per_page,
            current_page=page,
            data=record_query,
        )
    @classmethod
    def get_all_requests(cls,db:Session) -> List[models.LicenceRequest]:
        return db.query(models.LicenceRequest).filter(models.LicenceRequest.is_deleted == False).all()


licence_request = CRUDLicenceRequestCRUD(models.LicenceRequest)

