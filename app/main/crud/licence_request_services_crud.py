import math
import bcrypt
from fastapi import HTTPException
from sqlalchemy import or_
import re
from typing import List, Optional, Union
import uuid
from app.main.core.i18n import __
from sqlalchemy.orm import Session

from app.main.core.mail import send_new_request, send_new_request_extend
from app.main.crud.base import CRUDBase
from app.main import models,schemas
from app.main.schemas import LicenceRequestCreate


class CRUDLicenceRequestService(CRUDBase[models.LicenceRequestService,schemas.LicenceRequestUpdate,schemas.LicenceRequestServiceResponseList]):

    @classmethod
    def get_by_uuid(cls,db:Session,*,uuid:str) -> Optional[models.LicenceRequestService]:
        return db.query(models.LicenceRequestService).filter(models.LicenceRequestService.uuid == uuid,models.LicenceRequestService.is_deleted==False).first()

    @classmethod
    def create(cls, db: Session, *, obj_in: schemas.LicenceRequestCreate, added_by: str) -> Optional[
        models.LicenceRequestService]:
        # Création de la demande de licence
        db_obj = models.LicenceRequestService(
            uuid=str(uuid.uuid4()),
            service_uuid=obj_in.service_uuid,
            licence_duration_uuid=obj_in.licence_duration_uuid,
            description=obj_in.description,
            type=obj_in.type,
            added_by=added_by
        )
        db.add(db_obj)

        # Création de la notification
        new_notification = models.LicenceRequest(
            uuid=str(uuid.uuid4()),
            title=obj_in.type,
            type=obj_in.type,
            description=obj_in.description,
            send_by=added_by
        )
        db.add(new_notification)
        db.commit()
        db.refresh(db_obj)

        # Envoi d’email aux administrateurs
        admins = db.query(models.User).filter(
            models.User.is_deleted == False,
            models.User.role.in_(["SUPER_ADMIN", "ADMIN", "EDIMESTRE"])
        ).all()

        for admin in admins:
            send_new_request(
                email_to=admin.email,
                title=obj_in.type,
                type=obj_in.type,
                description=obj_in.description
            )

        return db_obj

    @classmethod
    def extend_licence(cls, db: Session, *, obj_in: schemas.LicenceRequestServiceExtend, added_by: str) -> Optional[
        models.LicenceRequestService]:
        # Création de la demande de licence
        db_obj = models.LicenceRequestService(
            uuid=str(uuid.uuid4()),
            service_uuid=obj_in.service_uuid,
            licence_duration_uuid=obj_in.licence_duration_uuid,
            description=obj_in.description,
            type="Nouvelle demande de prolongation de licence",
            number_of_days=obj_in.number_of_days,
            added_by=added_by
        )
        db.add(db_obj)

        # Création de la notification
        new_notification = models.LicenceRequest(
            uuid=str(uuid.uuid4()),
            title="Nouvelle demande de prolongation de licence",
            type=" Nouvelle demande de prolongation de licence",
            description=obj_in.description,
            send_by=added_by
        )
        db.add(new_notification)
        db.commit()
        db.refresh(db_obj)

        # Envoi d’email aux administrateurs
        admins = db.query(models.User).filter(
            models.User.is_deleted == False,
            models.User.role.in_(["SUPER_ADMIN", "ADMIN", "EDIMESTRE"])
        ).all()

        for admin in admins:
            send_new_request_extend(
                email_to=admin.email,
                title="Nouvelle demande de prolongation de licence",
                type="Nouvelle demande de prolongation de licence",
                description=obj_in.description,
                number_of_days=obj_in.number_of_days
            )

        return db_obj

    @classmethod
    def get_many(
            cls,
            db: Session,
            page: int = 1,
            per_page: int = 25,
    ):
        record_query = db.query(models.LicenceRequestService).filter(models.LicenceRequestService.is_deleted == False,)

        total = record_query.count()

        record_query = record_query.offset((page - 1) * per_page).limit(per_page)

        return schemas.LicenceRequestServiceResponseList(
            total=total,
            pages=math.ceil(total / per_page),
            per_page=per_page,
            current_page=page,
            data=record_query,
        )

    @classmethod
    def update_status(cls, db: Session, *, licence_uuid: str, status: str) -> Optional[models.LicenceRequest]:
        db_obj = cls.get_by_uuid(db=db, uuid=licence_uuid)
        if not db_obj:
            raise HTTPException(status_code=404, detail=__(key="licence-request-not-found"))

        db_obj.status = status

        if status == models.LicenceRequestServiceStatus.accepted:
            title = "Demande de licence acceptée"
            description = "Votre demande de licence a été acceptée."
            type = "Demande acceptée"
        elif status == models.LicenceRequestServiceStatus.declined:
            title = "Demande de licence rejetée"
            description = "Votre demande de licence a été rejetée. Veuillez contacter l'administration pour plus de détails."
            type = "Demande rejéttée"

        new_message = models.LicenceRequest(
            uuid=str(uuid.uuid4()),  # ← fonctionne maintenant correctement
            title=title,
            type=type,
            description=description,
            send_by=db_obj.added_by
        )

        db.add(new_message)
        db.commit()
        db.refresh(db_obj)
        return db_obj





licence_response_service = CRUDLicenceRequestService(models.LicenceRequestService)
