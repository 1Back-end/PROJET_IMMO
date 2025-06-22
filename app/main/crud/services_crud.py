import math
from typing import Optional, List

from fastapi import HTTPException
import uuid

from sqlalchemy import or_

from app.main.core.i18n import __
from sqlalchemy.orm import Session
from app.main.crud.base import CRUDBase
from app.main import models, schemas,crud


class ServiceCRUD(CRUDBase[models.Service, schemas.ServiceCreate, schemas.ServiceUpdate]):

    @staticmethod
    def get_by_uuids(db: Session, uuids: List[str]):
        return db.query(models.Service).filter(
            models.Service.uuid.in_(uuids),  # Utilisation de 'in' pour filtrer plusieurs UUIDs
            models.Service.is_deleted == False
        ).all()

    @classmethod
    def get_by_uuid(cls,db:Session,*, uuid:str):
        return db.query(models.Service).filter(models.Service.uuid == uuid,models.Service.is_deleted==False).first()

    @classmethod
    def get_by_name(cls,db:Session,*, name:str):
        return db.query(models.Service).filter(models.Service.name==name,models.Service.is_deleted==False).first()

    @classmethod
    def create(cls,db:Session,*,obj_in:schemas.ServiceCreate,added_by:str):
        db_obj = models.Service(
            uuid =str(uuid.uuid4()),
            name = obj_in.name,
            description=obj_in.description,
            added_by=added_by
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

    @classmethod
    def update(cls,db:Session,*,obj_in:schemas.ServiceUpdate,added_by:str):
        db_obj = cls.get_by_uuid(db,uuid=obj_in.uuid)
        if not db_obj:
            raise HTTPException(status_code=404, detail=__(key="service-not-found"))

        db_obj.name = obj_in.name if obj_in.name else db_obj.name
        db_obj.description = obj_in.description if obj_in.description else db_obj.description
        db.commit()
        db.refresh(db_obj)
        return db_obj


    @classmethod
    def soft_delete(cls,db:Session,*,uuid:str):
        db_obj = cls.get_by_uuid(db,uuid=uuid)
        if not db_obj:
            raise HTTPException(status_code=404, detail=__(key="service-not-found"))

        service_used = db.query(models.OrganisationOwnerService).filter(
            models.OrganisationOwnerService.service_uuid==uuid,
            models.OrganisationOwnerService.is_deleted==False
        ).first()
        if service_used:
            raise HTTPException(status_code=404, detail=__(key="service-is-used"))

        db_obj.is_deleted = True
        db.commit()


    @classmethod
    def delete(cls, db:Session,*,uuid:str):
        db_obj = cls.get_by_uuid(db,uuid=uuid)
        if not db_obj:
            raise HTTPException(status_code=404, detail=__(key="service-not-found"))
        db.delete(db_obj)
        db.commit()

    @classmethod
    def update_status(cls,db:Session,*,uuid:str,status:str):
        db_obj = cls.get_by_uuid(db,uuid=uuid)
        if not db_obj:
            raise HTTPException(status_code=404, detail=__(key="service-not-found"))
        db_obj.status = status
        db.commit()

    @classmethod
    def get_many(
            cls,
            db: Session,
            page: int = 1,
            per_page: int = 5,
            order: Optional[str] = None,
            order_field: Optional[str] = None,
            keyword: Optional[str] = None,
            status: Optional[str] = None,
    ):
        record_query = db.query(models.Service).filter(models.Service.is_deleted == False)

        if keyword:
            record_query = record_query.filter(
                or_(
                    models.Service.name.ilike(f'%{keyword}%'),
                    models.Service.description.ilike(f'%{keyword}%'),

                )
            )

        if order and order_field and hasattr(models.Service, order_field):
            if order == "asc":
                record_query = record_query.order_by(getattr(models.Service, order_field).asc())
            else:
                record_query = record_query.order_by(getattr(models.Service, order_field).desc())
        if status:
            record_query = record_query.filter(models.Service.status.ilike(f'%{status}%'))

        total = record_query.count()

        record_query = record_query.offset((page - 1) * per_page).limit(per_page)

        return schemas.ServiceResponseList(
            total=total,
            pages=math.ceil(total / per_page),
            per_page=per_page,
            current_page=page,
            data=record_query,
        )



services = ServiceCRUD(models.Service)