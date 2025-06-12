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
from app.main import models, schemas
from app.main.core.mail import send_account_creation_email  # Envoi mail à la création de compte


class CRUDUser(CRUDBase[models.User, schemas.UserCreate, schemas.UserUpdate]):

    @classmethod
    def get_by_phone_number(cls, db: Session, *, phone_number: str) -> Union[models.User, None]:
        # Recherche un utilisateur par son numéro de téléphone
        return db.query(models.User).filter(models.User.phone_number == phone_number).first()

    @classmethod
    def get_by_email(cls, db: Session, *, email: str) -> Union[models.User, None]:
        # Recherche un utilisateur par son email
        return db.query(models.User).filter(models.User.email == email).first()

    @classmethod
    def get_by_uuid(cls, db: Session, *, uuid: str) -> Union[models.User, None]:
        # Recherche un utilisateur par son UUID
        return db.query(models.User).filter(models.User.uuid == uuid).first()

    @classmethod
    def create(cls, db: Session, *, obj_in: schemas.UserCreate) -> models.User:
        # Génère un mot de passe aléatoire de 8 caractères
        password: str = generate_password(8, 8)
        print(f"User password: {password}")  # Pour debug ou logs, attention à ne pas le faire en prod !

        # Crée un nouvel utilisateur avec un UUID unique et le mot de passe hashé
        new_user = models.User(
            uuid=str(uuid.uuid4()),              # Génération UUID
            email=obj_in.email,
            phone_number=obj_in.phone_number,
            password_hash=get_password_hash(password),  # Hash du mot de passe généré
            first_name=obj_in.first_name,
            last_name=obj_in.last_name,
            role=obj_in.role,
            login = obj_in.login,
            avatar_uuid = obj_in.avatar_uuid

        )
        db.add(new_user)    # Ajoute l'utilisateur à la session DB
        db.commit()         # Sauvegarde en base
        db.refresh(new_user)  # Rafraîchit l'objet pour récupérer toutes les données (id, dates, etc.)

        # Envoie un mail de création de compte avec les infos et mot de passe
        send_account_creation_email(
            email_to=obj_in.email,
            first_name=obj_in.first_name,
            last_name=obj_in.last_name,
            password=password
        )
        return new_user  # Retourne l'utilisateur créé

    @classmethod
    def update_user(cls, db: Session, *, obj_in: schemas.UserUpdate):
        # Met à jour les infos d'un utilisateur existant via UUID
        db_obj = cls.get_by_uuid(db=db, uuid=obj_in.uuid)
        if not db_obj:
            # Lève une erreur 404 si l'utilisateur n'existe pas
            raise HTTPException(status_code=404, detail=__(key="user-not-found"))

        # Met à jour uniquement les champs fournis dans obj_in
        db_obj.first_name = obj_in.first_name if obj_in.first_name else db_obj.first_name
        db_obj.last_name = obj_in.last_name if obj_in.last_name else db_obj.last_name
        db_obj.email = obj_in.email if obj_in.email else db_obj.email
        # Ici une petite coquille: tu as `if db_obj.phone_number else db_obj.phone_number` ça devrait être `if obj_in.phone_number else db_obj.phone_number`
        db_obj.phone_number = obj_in.phone_number if obj_in.phone_number else db_obj.phone_number
        db_obj.login = obj_in.login if obj_in.login else db_obj.login
        db_obj.role = obj_in.role if obj_in.role else db_obj.role
        db_obj.avatar_uuid = obj_in.avatar_uuid if obj_in.avatar_uuid else db_obj.avatar_uuid

        db.flush()   # Vide le buffer avant commit (optionnel mais parfois utile)
        db.commit()  # Sauvegarde les changements en base
        db.refresh(db_obj)  # Rafraîchit l'objet mis à jour

        return db_obj  # Retourne l'utilisateur mis à jour

    @classmethod
    def authenticate(cls, db: Session, *, email: str, password: str) -> Union[models.User, None]:
        # Authentifie un utilisateur avec email + mot de passe
        db_obj: models.User = db.query(models.User).filter(models.User.email == email).first()
        if not db_obj:
            return None  # Aucun utilisateur trouvé avec cet email

        # Vérifie si le mot de passe correspond au hash stocké
        if not verify_password(password, db_obj.password_hash):
            return None  # Mot de passe incorrect

        return db_obj  # Authentification réussie, retourne l'utilisateur

    @classmethod
    def update(cls, db: Session, *, uuid: str, status: str) -> models.User:
        # Met à jour uniquement le statut d'un utilisateur
        user = cls.get_by_uuid(db=db, uuid=uuid)
        if not user:
            raise HTTPException(status_code=404, detail=__(key="user-not-found"))
        user.status = status  # Mise à jour du statut
        db.commit()           # Sauvegarde

    @classmethod
    def get_all_users(cls, db: Session):
        # Récupère tous les utilisateurs non supprimés avec un rôle spécifique
        return db.query(models.User).filter(
            models.User.is_deleted == False,
            models.User.role.in_(["ADMIN", "EDIMESTRE","SUPER_ADMIN","BUREAU_ORDRE","SECRETAIRE"])
        ).all()

    @classmethod
    def delete(cls, db: Session, *, uuid: str):
        # Suppression logique (soft delete) d'un utilisateur par UUID
        user = cls.get_by_uuid(db=db, uuid=uuid)
        if not user:
            raise HTTPException(status_code=404, detail=__(key="user-not-found"))
        user.is_deleted = True  # Marque l'utilisateur comme supprimé
        db.commit()             # Sauvegarde

    @classmethod
    def get_many(
        cls,
        db: Session,
        page: int = 1,
        per_page: int = 25,
    ):
        record_query = db.query(models.User).filter( models.User.is_deleted == False,models.User.role.in_(["ADMIN", "EDIMESTRE","BUREAU_ORDRE","SECRETAIRE"]))

        total = record_query.count()  # Total des utilisateurs correspondant au filtre
        # Pagination avec offset et limit
        record_query = record_query.offset((page - 1) * per_page).limit(per_page)

        # Retourne une réponse paginée avec total, pages, page actuelle, nombre par page et liste des données
        return schemas.UserResponseList(
            total=total,
            pages=math.ceil(total / per_page),
            per_page=per_page,
            current_page=page,
            data=record_query,
        )


# Instance globale pour utilisation dans d'autres modules
user = CRUDUser(models.User)
