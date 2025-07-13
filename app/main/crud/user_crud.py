import math
import bcrypt
from fastapi import HTTPException
from sqlalchemy import or_
import re
from typing import List, Optional, Union
import uuid
from app.main.core.i18n import __  # Pour la traduction / gestion des messages d'erreur
from app.main.core.security import generate_password, get_password_hash, verify_password  # Fonctions de gestion de mot de passe
from sqlalchemy.orm import Session
from app.main.crud.base import CRUDBase  # Base CRUD générique
from app.main import models, schemas,crud
from app.main.core.mail import send_account_creation_email  # Envoi mail à la création de compte


class CRUDUser(CRUDBase[models.User, schemas.UserCreate, schemas.UserUpdate]):

    @classmethod
    def get_by_phone_number(cls, db: Session, *, phone_number: str) -> Union[models.User, None]:
        return db.query(models.User).filter(models.User.phone_number == phone_number,models.User.is_deleted==False).first()

    @classmethod
    def get_by_email(cls, db: Session, *, email: str) -> Union[models.User, None]:
        return db.query(models.User).filter(models.User.email == email,models.User.is_deleted==False).first()

    @classmethod
    def get_by_uuid(cls, db: Session, *, uuid: str) -> Union[models.User, None]:
        return db.query(models.User).filter(models.User.uuid == uuid,models.User.is_deleted==False).first()

    @classmethod
    def create(cls, db: Session, *, obj_in: schemas.UserCreate) -> models.User:
        password: str = generate_password(8, 8)
        print(f"User password: {password}")

        new_user = models.User(
            uuid=str(uuid.uuid4()),
            email=obj_in.email,
            phone_number=obj_in.phone_number,
            password_hash=get_password_hash(password),
            first_name=obj_in.first_name,
            last_name=obj_in.last_name,
            role=obj_in.role,
            login = obj_in.login,
            avatar_uuid = obj_in.avatar_uuid

        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        send_account_creation_email(
            email_to=obj_in.email,
            first_name=obj_in.first_name,
            last_name=obj_in.last_name,
            password=password
        )
        return new_user  # Retourne l'utilisateur créé

    @classmethod
    def update_user(cls, db: Session, *, obj_in: schemas.UserUpdate):
        db_obj = cls.get_by_uuid(db=db, uuid=obj_in.uuid)
        if not db_obj:
            raise HTTPException(status_code=404, detail=__(key="user-not-found"))

        db_obj.first_name = obj_in.first_name if obj_in.first_name else db_obj.first_name
        db_obj.last_name = obj_in.last_name if obj_in.last_name else db_obj.last_name
        db_obj.email = obj_in.email if obj_in.email else db_obj.email
        db_obj.phone_number = obj_in.phone_number if obj_in.phone_number else db_obj.phone_number
        db_obj.login = obj_in.login if obj_in.login else db_obj.login
        db_obj.role = obj_in.role if obj_in.role else db_obj.role
        db_obj.avatar_uuid = obj_in.avatar_uuid if obj_in.avatar_uuid else db_obj.avatar_uuid

        db.flush()
        db.commit()
        db.refresh(db_obj)

        return db_obj

    @classmethod
    def update_profil(cls, db: Session, *, db_obj: models.User, obj_in: schemas.UserUpdateProfil) -> Optional[models.User]:
        db_obj.first_name = obj_in.first_name or db_obj.first_name
        db_obj.last_name = obj_in.last_name or db_obj.last_name
        db_obj.email = obj_in.email or db_obj.email
        db_obj.phone_number = obj_in.phone_number or db_obj.phone_number
        db_obj.login = obj_in.login or db_obj.login
        db_obj.avatar_uuid = obj_in.avatar_uuid or db_obj.avatar_uuid

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        return db_obj

    @classmethod
    def authenticate(cls, db: Session, *, email: str, password: str) -> Union[models.User, None]:
        db_obj: models.User = db.query(models.User).filter(models.User.email == email,models.User.is_deleted==False).first()
        if not db_obj:
            return None
        if not verify_password(password, db_obj.password_hash):
            return None

        return db_obj

    @classmethod
    def update(cls, db: Session, *, uuid: str, status: str) -> models.User:
        user = cls.get_by_uuid(db=db, uuid=uuid)
        if not user:
            raise HTTPException(status_code=404, detail=__(key="user-not-found"))
        user.status = status
        db.commit()

    @classmethod
    def get_all_users(cls, db: Session):
        return db.query(models.User).filter(
            models.User.is_deleted == False,
            models.User.role.in_(["ADMIN", "EDIMESTRE"])
        ).all()

    @classmethod
    def delete(cls, db: Session, *, uuid: str):
        user = cls.get_by_uuid(db=db, uuid=uuid)
        if not user:
            raise HTTPException(status_code=404, detail=__(key="user-not-found"))
        user.is_deleted = True
        db.commit()

    @classmethod
    def get_many(
        cls,
        db: Session,
        page: int = 1,
        per_page: int = 25,
    ):
        record_query = db.query(models.User).filter( models.User.is_deleted == False,models.User.role.in_(["ADMIN", "EDIMESTRE"]))

        total = record_query.count()

        record_query = record_query.offset((page - 1) * per_page).limit(per_page)

        return schemas.UserResponseList(
            total=total,
            pages=math.ceil(total / per_page),
            per_page=per_page,
            current_page=page,
            data=record_query,
        )


user = CRUDUser(models.User)
