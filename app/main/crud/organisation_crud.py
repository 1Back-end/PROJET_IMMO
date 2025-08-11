import math
from datetime import datetime, timedelta
import random
from app.main.core.mail import notify_new_company, send_organisation_otp, send_user_code_to_delete
from fastapi import HTTPException, BackgroundTasks
from sqlalchemy import or_
from typing import List, Optional, Union
import uuid
from app.main.core.i18n import __
from sqlalchemy.orm import Session, joinedload
from app.main.crud.base import CRUDBase
from app.main import models,schemas,crud
from app.main.core.security import get_password_hash, verify_password, generate_code


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
    def soft_delete(cls,db:Session,*,uuid:str) -> Optional[models.Organisation]:
        db_obj = cls.get_by_uuid(db,uuid=uuid)
        if not db_obj:
            raise HTTPException(status_code=404,detail=__(key="organisation-not-found"))
        db_obj.is_deleted = True
        owner = crud.user.get_by_uuid(db=db,uuid=db_obj.owner_uuid)
        if not owner:
            raise HTTPException(status_code=404,detail=__(key="organisation-not-found"))
        owner.is_deleted = True
        owner.status = models.UserStatus.UNACTIVED
        db.commit()



    @classmethod
    def create(cls, db: Session, obj_in: schemas.OrganisationCreate, background_tasks: BackgroundTasks) -> Optional[
        models.Organisation]:
        user_uuid = str(uuid.uuid4())
        new_user = models.User(
            uuid=user_uuid,
            first_name=obj_in.owner_first_name,
            last_name=obj_in.owner_last_name,
            email=obj_in.owner_email,
            phone_number=obj_in.owner_phone_number,
            password_hash=get_password_hash(obj_in.owner_password),
            role=models.UserRole.OWNER,
            is_new_user=False
        )
        db.add(new_user)

        new_notification = models.LicenceRequest(
            uuid=str(uuid.uuid4()),
            title="Création d'une organisation",
            description=f"Une nouvelle organisation '{obj_in.company_name}' a été créée par {obj_in.owner_first_name} {obj_in.owner_last_name}.",
            send_by=user_uuid,
            type="Création d’organisation"
        )
        db.add(new_notification)

        db.commit()
        db.refresh(new_user)
        db.refresh(new_notification)

        # Génération OTP
        code = generate_code(length=12)
        otp_code = str(code[0:6])
        print(f"OTP code: {otp_code}")
        otp_expiration = datetime.utcnow() + timedelta(days=1)

        new_org = models.Organisation(
            uuid=str(uuid.uuid4()),
            name=obj_in.company_name,
            email=obj_in.company_email,
            phone_number=obj_in.company_phone_number,
            description=obj_in.company_description,
            country_uuid=obj_in.country_uuid,
            city_uuid=obj_in.city_uuid,
            owner_uuid=user_uuid,
            status=models.OrganisationStatus.inactive,
            validation_account_otp=otp_code,
            validation_otp_expirate_at=otp_expiration,
            additional_information=obj_in.additional_information,
        )
        db.add(new_org)
        db.commit()
        db.refresh(new_org)

        for service_uuid in obj_in.service_uuids:
            link = models.OrganisationOwnerService(
                uuid=str(uuid.uuid4()),
                owner_uuid=user_uuid,
                organisation_uuid=new_org.uuid,
                service_uuid=service_uuid
            )
            db.add(link)

        db.commit()

        # Envoi email OTP
        background_tasks.add_task(
            send_organisation_otp,
            email_to=new_user.email,
            otp=otp_code,
            expirate_at=otp_expiration
        )

        # Notifications admin
        admins = db.query(models.User).filter(
            models.User.is_deleted == False,
            models.User.role.in_(["ADMIN", "EDIMESTRE", "SUPER_ADMIN"])
        ).all()

        for admin in admins:
            background_tasks.add_task(
                notify_new_company,
                email_to=admin.email,
                title="Création d'une organisation",
                description=f"Une nouvelle organisation '{obj_in.company_name}'",
                created_by=f"{new_user.first_name} {new_user.last_name}"
            )

        return new_org

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
            joinedload(models.Organisation.owner)
        ).filter(
            models.Organisation.is_deleted == False
        ).order_by(models.Organisation.created_at.desc())

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
    def get_by_owner_uuid(
            cls,
            db: Session,
            page: int = 1,
            per_page: int = 5,
            order: Optional[str] = None,
            order_field: Optional[str] = None,
            keyword: Optional[str] = None,
            status: Optional[str] = None,
            owner_uuid: Optional[str] = None,
    ):
        record_query = db.query(models.Organisation).options(
            joinedload(models.Organisation.owner_services).joinedload(models.OrganisationOwnerService.service),
            joinedload(models.Organisation.owner)
        ).filter(
            models.Organisation.is_deleted == False,
            models.Organisation.owner_uuid == owner_uuid
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
        db_obj.additional_information = obj_in.additional_information if obj_in.additional_information else obj_in.additional_information

    @classmethod
    def get_all_service_by_owners(cls, db: Session, *, owner_uuid: str):
        services = (
            db.query(models.Service)
            .join(models.OrganisationOwnerService, models.Service.uuid == models.OrganisationOwnerService.service_uuid)
            .filter(models.OrganisationOwnerService.owner_uuid == owner_uuid,
                    models.OrganisationOwnerService.is_deleted == False)
            .all()
        )
        return services



organisation = OrganisationCRUD(models.Organisation)