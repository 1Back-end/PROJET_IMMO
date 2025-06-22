import math
import bcrypt
from fastapi import HTTPException
from sqlalchemy import or_
import re
from typing import List, Optional, Union
import uuid
from app.main.core.i18n import __
from sqlalchemy.orm import Session, joinedload
from app.main.crud.base import CRUDBase
from app.main import models,schemas
from app.main.schemas import OrganisationBase
from app.main.core.security import get_password_hash, verify_password


class OrganisationCRUD(CRUDBase[models.Organisation,schemas.OrganisationBase,schemas.OrganisationCreate]):

    @staticmethod
    def get_by_uuids(db: Session, uuids: List[str]):
        return db.query(models.Organisation).filter(
            models.Organisation.uuid.in_(uuids),  # Utilisation de 'in' pour filtrer plusieurs UUIDs
            models.Organisation.is_deleted == False
        ).all()

    @classmethod
    def get_by_uuid(cls,db:Session,*,uuid:str) -> Optional[models.Organisation]:
        return db.query(models.Organisation).filter(models.Organisation.uuid == uuid,models.Organisation.is_deleted==False).first()


    @classmethod
    def get_by_name(cls,db:Session,*,name:str) -> Optional[models.Organisation]:
        return db.query(models.Organisation).filter(models.Organisation.name==name,models.Organisation.is_deleted==False).first()

    @classmethod
    def get_by_email(cls,db:Session,*,email:str) -> Optional[models.Organisation]:
        return  db.query(models.Organisation).filter(models.Organisation.email==email,models.Organisation.is_deleted==False).first()

    @classmethod
    def get_by_phone_number(cls,db:Session,*,phone_number:str) -> Optional[models.Organisation]:
        return db.query(models.Organisation).filter(models.Organisation.phone_number==phone_number,models.Organisation.is_deleted==False).first()

    @classmethod
    def create(cls, db: Session, obj_in: schemas.OrganisationCreate) -> Optional[models.Organisation]:
        import uuid

        # Création du User (propriétaire)
        user_uuid = str(uuid.uuid4())
        new_user = models.User(
            uuid=user_uuid,
            first_name=obj_in.owner_first_name,
            last_name=obj_in.owner_last_name,
            email=obj_in.owner_email,
            phone_number=obj_in.owner_phone_number,
            password_hash=get_password_hash(obj_in.owner_password),
            role=models.UserRole.OWNER
        )
        db.add(new_user)

        # Création de l'adresse
        address_uuid = str(uuid.uuid4())
        new_address = models.Address(
            uuid=address_uuid,
            country=obj_in.company_country,
            city=obj_in.company_city,
            state=obj_in.company_state,
            zipcode=obj_in.company_zipcode
        )
        db.add(new_address)

        # Création de la notification
        new_notification = models.LicenceRequest(
            uuid=str(uuid.uuid4()),
            title="Création d'une organisation",
            description=f"Une nouvelle organisation '{obj_in.company_name}' a été créée par {obj_in.owner_first_name} {obj_in.owner_last_name}.",
            send_by=user_uuid,
            type="création d’organisation"
        )
        db.add(new_notification)

        # Commit des trois premières entités
        db.commit()
        db.refresh(new_user)
        db.refresh(new_address)
        db.refresh(new_notification)

        # Création de l'organisation
        organisation_uuid = str(uuid.uuid4())
        db_obj = models.Organisation(
            uuid=organisation_uuid,
            name=obj_in.company_name,
            email=obj_in.company_email,
            phone_number=obj_in.company_phone_number,
            description=obj_in.company_description,
            address_uuid=address_uuid,
            owner_uuid=user_uuid,
            status=models.OrganisationStatus.inactive
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        # Création des liens Organisation-Service pour chaque service_uuid
        for service_uuid in obj_in.service_uuids:
            link = models.OrganisationOwnerService(
                uuid=str(uuid.uuid4()),
                owner_uuid=new_user.uuid,
                organisation_uuid=db_obj.uuid,
                service_uuid=service_uuid
            )
            db.add(link)

        # Commit final des liens
        db.commit()

        return db_obj

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
        record_query = db.query(models.Organisation).options(
            joinedload(models.Organisation.owner_services).joinedload(models.OrganisationOwnerService.service),
            joinedload(models.Organisation.address),
            joinedload(models.Organisation.owner)
        ).filter(
            models.Organisation.is_deleted == False
        )

        if keyword:
            record_query = record_query.filter(
                or_(
                    models.Organisation.name.ilike(f'%{keyword}%'),
                    models.Organisation.description.ilike(f'%{keyword}%'),
                    models.Organisation.uuid.ilike(f'%{keyword}%'),
                    models.Organisation.phone_number.ilike(f'%{keyword}%'),
                    models.Organisation.description.ilike(f'%{keyword}%'),

                )
            )

        if order and order_field and hasattr(models.Organisation, order_field):
            if order == "asc":
                record_query = record_query.order_by(getattr(models.Organisation, order_field).asc())
            else:
                record_query = record_query.order_by(getattr(models.Organisation, order_field).desc())
        if status:
            record_query = record_query.filter(models.Organisation.status.ilike(f'%{status}%'))

        total = record_query.count()

        record_query = record_query.offset((page - 1) * per_page).limit(per_page)


        return schemas.OrganisationResponseList(
            total=total,
            pages=math.ceil(total / per_page),
            per_page=per_page,
            current_page=page,
            data=record_query,
        )


    @classmethod
    def update_status(cls,db:Session,uuid:str,status:str):
        db_obj = cls.get_by_uuid(db=db,uuid=uuid)
        if not db_obj:
            raise HTTPException(status_code=404,detail=__(key="organisation-not-found"))
        db_obj.status = status
        db.commit()


    @classmethod
    def update(cls,db:Session,*,obj_in:schemas.OrganisationUpdate,updated_by:str):
        db_obj = cls.get_by_uuid(uuid=obj_in.uuid)
        if not db_obj:
            raise HTTPException(status_code=404,detail=__(key="organisation-not-found"))
        db_obj.name = obj_in.company_name if obj_in.company_name else obj_in.name
        db_obj.email = obj_in.company_email if obj_in.company_email else obj_in.email
        db_obj.phone_number = obj_in.company_number if obj_in.company_number else obj_in.phone_number
        db_obj.description = obj_in.company_description if obj_in.company_description else obj_in.description




organisation = OrganisationCRUD(models.Organisation)