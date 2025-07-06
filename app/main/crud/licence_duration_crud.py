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
from app.main.schemas import LicenceDurationModel


class CRUDLicenceDurationModel(CRUDBase[models.LicenceDuration,schemas.LicenceDurationModel,schemas.LicenceDurationModelList]):

    @classmethod
    def get_by_uuid(cls,db:Session,*,uuid:str) -> Optional[LicenceDurationModel]:
        return db.query(models.LicenceDuration).filter(models.LicenceDuration.uuid == uuid).first()

    @classmethod
    def get_by_name(cls,db:Session,*,name:str) -> Optional[LicenceDurationModel]:
        return  db.query(models.LicenceDuration).filter(models.LicenceDuration.key==name).first()

    @classmethod
    def update_status(cls,db:Session,*,uuid:str,is_active:bool) -> Optional[LicenceDurationModel]:
        db_obj = cls.get_by_uuid(db,uuid=uuid)
        if not db_obj:
            raise HTTPException(status_code=404,detail=__(key="licence-duration-not-found"))
        db_obj.is_active = is_active
        db.commit()

    @classmethod
    def create(cls,db:Session,obj_in:schemas.LicenceDurationCrete,added_by:str):
        db_obj = models.LicenceDuration(
            uuid=str(uuid.uuid4()),
            key=obj_in.key,
            description=obj_in.description,
            price=obj_in.price,
            duration_days=obj_in.duration_days,
            added_by=added_by
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @classmethod
    def get_many(
            cls,
            db: Session,
            page: int = 1,
            per_page: int = 25,
    ):
        record_query = db.query(models.LicenceDuration).filter(models.LicenceDuration.is_deleted==False).order_by(models.LicenceDuration.created_at.desc())

        total = record_query.count()

        record_query = record_query.offset((page - 1) * per_page).limit(per_page)

        return schemas.LicenceDurationModelList(
            total=total,
            pages=math.ceil(total / per_page),
            per_page=per_page,
            current_page=page,
            data=record_query,
        )

    @classmethod
    def update(cls,db:Session,*,obj_in:schemas.LicenceDurationUpdate,added_by:str) -> Optional[LicenceDurationModel]:
        db_obj = cls.get_by_uuid(db=db, uuid=obj_in.uuid)
        if not db_obj:
            raise HTTPException(status_code=404, detail=__(key="licence-duration-not-found"))

        db_obj.key = obj_in.key if obj_in.key else db_obj.key
        db_obj.description = obj_in.description if obj_in.description else db_obj.description
        db_obj.duration_days = obj_in.duration_days if obj_in.duration_days else db_obj.duration_days
        db_obj.price = obj_in.price if obj_in.price else db_obj.price
        db_obj.added_by = added_by
        db.commit()
        db.refresh(db_obj)
        return db_obj


    @classmethod
    def soft_delete(cls,db:Session,*,uuid:str) -> Optional[LicenceDurationModel]:
        db_obj = cls.get_by_uuid(db=db, uuid=uuid)
        if not db_obj:
            raise HTTPException(status_code=404, detail=__(key="licence-duration-not-found"))
        db_obj.is_deleted = True
        db.commit()

    @classmethod
    def drop_delete(cls, db: Session, *, uuid: str) -> Optional[LicenceDurationModel]:
        db_obj = cls.get_by_uuid(db=db, uuid=uuid)
        if not db_obj:
            raise HTTPException(status_code=404, detail=__(key="licence-duration-not-found"))
        db.delete(db_obj)
        db.commit()


licence_duration = CRUDLicenceDurationModel(models.LicenceDuration)