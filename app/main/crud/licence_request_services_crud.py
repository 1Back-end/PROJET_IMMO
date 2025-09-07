import math
import bcrypt
from fastapi import HTTPException
from sqlalchemy import or_
import re
from typing import List, Optional, Union
import uuid
from app.main.core.i18n import __
from sqlalchemy.orm import Session

from app.main.core.mail import send_new_request, send_new_request_extend, send_user_accepted_request, \
    send_user_declined_request
from app.main.crud.base import CRUDBase
from app.main import models,schemas,crud
from app.main.schemas import LicenceRequestCreate


class CRUDLicenceRequestService(CRUDBase[models.LicenceRequestService,schemas.LicenceRequestUpdate,schemas.LicenceRequestServiceResponseList]):

    @classmethod
    def get_by_uuid(cls,db:Session,*,uuid:str) -> Optional[models.LicenceRequestService]:
        return db.query(models.LicenceRequestService).filter(models.LicenceRequestService.uuid == uuid,models.LicenceRequestService.is_deleted==False).first()

    @classmethod
    def create(cls, db: Session, *, obj_in: schemas.LicenceRequestCreate, added_by: str) -> Optional[models.LicenceRequestService]:

        existing_request = db.query(models.LicenceRequestService).filter(
            models.LicenceRequestService.service_uuid == obj_in.service_uuid,
            models.LicenceRequestService.licence_duration_uuid == obj_in.licence_duration_uuid,
            models.LicenceRequestService.added_by == added_by,
            models.LicenceRequestService.status == "pending"
        ).first()

        if existing_request:
            raise HTTPException(
                status_code=400,
                detail="Une demande similaire est déjà en attente de traitement."
            )
        # Création de la demande de licence
        db_obj = models.LicenceRequestService(
            uuid=str(uuid.uuid4()),
            service_uuid=obj_in.service_uuid,
            licence_duration_uuid=obj_in.licence_duration_uuid,
            description=obj_in.description,
            type="Demande de Licence",
            added_by=added_by
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        new_notification = models.LicenceRequest(
            uuid=str(uuid.uuid4()),
            title = "Demande de Licence",
            description = "Nouvelle demande de Licence",
            is_read = False,
            send_by = added_by,
            type =  "Demande de Licence"
        )
        db.add(new_notification)
        db.commit()
        db.refresh(new_notification)

        # Envoi d’email aux administrateurs (sans créer d’enregistrement de notification)
        admins = db.query(models.User).filter(
            models.User.is_deleted == False,
            models.User.role.in_(["SUPER_ADMIN"])
        ).all()

        for admin in admins:
            send_new_request(
                email_to=admin.email,
                title="Demande de Licence",
                type="Demande de Licence",
                description=obj_in.description
            )

        return db_obj



    @classmethod
    def cancel_request_licence(cls,db:Session,*,request_uuid:str):
        db_obj = crud.licence_response_service.get_by_uuid(db=db,uuid=request_uuid)
        if not db_obj:
            raise HTTPException(status_code=404,detail="Licence request not found")
        db_obj.status = models.LicenceRequestServiceStatus.declined

        new_notification = models.LicenceRequest(
            uuid=str(uuid.uuid4()),
            title = "Annulation de la demande de licence",
            description = "Annulation de la demande de licence",
            is_read = False,
            type = "Annulation de licence",
            send_by= db_obj.added_by,
        )
        db.add(new_notification)
        db.commit()
        db.refresh(new_notification)


    @classmethod
    def extend_licence(cls, db: Session, *, obj_in: schemas.LicenceRequestServiceExtend, added_by: str) -> Optional[
        models.LicenceRequestService]:

        licence_duration  = crud.licence_duration.get_by_uuid(db=db, uuid=obj_in.licence_duration_uuid)
        if not licence_duration:
            raise HTTPException(status_code=404, detail=__(key="licence-duration-not-found"))

        licence = crud.licence.get_by_uuid(db=db, uuid=obj_in.licence_uuid)
        if not licence:
            raise HTTPException(status_code=404, detail=__(key="licence-not-found"))


        db_obj = models.LicenceRequestService(
            uuid=str(uuid.uuid4()),
            service_uuid=obj_in.service_uuid,
            licence_duration_uuid=obj_in.licence_duration_uuid,
            description=obj_in.description,
            type="Prolongement de licence",
            licence_uuid = obj_in.licence_uuid,
            added_by=added_by
        )
        db.add(db_obj)

        # Création de la notification
        new_notification = models.LicenceRequest(
            uuid=str(uuid.uuid4()),
            title="Prolongement de licence",
            type="Prolongement de licence",
            description=obj_in.description,
            send_by=added_by
        )
        db.add(new_notification)
        db.commit()
        db.refresh(db_obj)

        # Envoi d’email aux administrateurs
        admins = db.query(models.User).filter(
            models.User.is_deleted == False,
            models.User.role.in_(["SUPER_ADMIN"])
        ).all()

        for admin in admins:
            send_new_request_extend(
                email_to=admin.email,
                title="Prolongement de licence",
                type="Prolongement de licence",
                description=obj_in.description,
                number_of_days=licence_duration.duration_days
            )

        return db_obj

    @classmethod
    def get_many(
            cls,
            db: Session,
            page: int = 1,
            per_page: int = 25,
    ):
        record_query = db.query(models.LicenceRequestService).filter(models.LicenceRequestService.is_deleted == False).order_by(models.LicenceRequestService.created_at.desc())

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
    def get_my_requests(
            cls,
            db: Session,
            page: int = 1,
            per_page: int = 25,
            added_by: str = None,
    ):
        record_query = db.query(models.LicenceRequestService).filter(models.LicenceRequestService.is_deleted == False,models.LicenceRequestService.added_by == added_by)

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
        user = db.query(models.User).filter(models.User.uuid==db_obj.added_by).first()
        if not user:
            raise HTTPException(status_code=404,detail=__(key="user-not-found"))

        if status == "accepted":
            db_obj.is_accepted = True
            new_notification = models.LicenceRequest(
                uuid=str(uuid.uuid4()),
                title="Demande ou prolongation de licence approuvée",
                description= "Nouvelle Demande ou prolongation de licence approuvée",
                send_by= db_obj.added_by,
                type="Nouvelle Demande ou prolongation de licence"
            )
            db.add(new_notification)
            db.commit()
            db.refresh(db_obj)
            send_user_accepted_request(
                email_to=user.email,
                title=db_obj.type,
                full_name=f"{user.last_name} {user.first_name}",
                request_date=db_obj.created_at
            )

        elif status == "declined":
            db_obj.is_declined = True
            new_notification = models.LicenceRequest(
                uuid=str(uuid.uuid4()),
                title="Demande ou prolongation de licence rejetté",
                description="Nouvelle Demande ou prolongation de licence rejetté",
                send_by=db_obj.added_by,
                type="Nouvelle Demande ou prolongation de rejetté"
            )
            db.add(new_notification)
            db.commit()
            db.refresh(db_obj)

            send_user_declined_request(
                email_to=user.email,
                title=db_obj.type,
                full_name=f"{user.last_name} {user.first_name}",
                request_date=db_obj.created_at
            )

        db_obj.status = status
        db.commit()




licence_response_service = CRUDLicenceRequestService(models.LicenceRequestService)
