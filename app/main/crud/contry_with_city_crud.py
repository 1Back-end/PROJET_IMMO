import math
import bcrypt
from fastapi import HTTPException
from sqlalchemy import or_
import re
from typing import List, Optional, Union
import uuid
from app.main.core.i18n import __
from sqlalchemy.orm import Session, joinedload

from app.main.crud import CreateSchemaType, ModelType
from app.main.crud.base import CRUDBase
from app.main import models,schemas


class CountryWithCityCRUD(CRUDBase[models.Country,schemas.CountryWithOut,schemas.CountryWithUpdate]):
    @classmethod
    def get_by_country_name(cls, db: Session, country_name: str) -> Optional[models.Country]:
        return db.query(models.Country).filter(models.Country.name == country_name, models.Country.is_deleted == False).first()

    @classmethod
    def get_country_by_uuid(cls, db: Session, uuid: str) -> Optional[models.Country]:
        return db.query(models.Country).filter(models.Country.uuid == uuid, models.Country.is_deleted == False).first()

    @classmethod
    def get_by_city_name(cls, db: Session, city_name: str) -> Optional[models.City]:
        return db.query(models.City).join(models.Country).filter(models.City.name == city_name, models.Country.is_deleted == False).first()

    @classmethod
    def get_city_by_uuid(cls, db: Session, uuid: str) -> Optional[models.City]:
        return db.query(models.City).filter(models.City.uuid == uuid, models.City.is_deleted == False).first()

    @classmethod
    def create_country(cls, db: Session, obj_in: schemas.CountryWithCreate) -> Optional[models.Country]:
        existing_country = cls.get_by_country_name(db=db, country_name=obj_in.name)
        if existing_country:
            return existing_country
        db_obj = models.Country(
            uuid=str(uuid.uuid4()),
            code=obj_in.code,
            name=obj_in.name,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @classmethod
    def create_city(cls, db: Session, obj_in: schemas.CityCreate) -> Optional[models.City]:
        existing_city = cls.get_by_city_name(db=db, city_name=obj_in.name)
        if existing_city:
            return None
        db_obj = models.City(
            uuid=str(uuid.uuid4()),
            name=obj_in.name,
            latitude=obj_in.latitude,
            longitude=obj_in.longitude,
            altitude=obj_in.altitude,
            country_uuid=obj_in.country_uuid,
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
    ) -> schemas.CountryResponseList:
        record_query = (
            db.query(models.City)
            .join(models.Country)
            .options(joinedload(models.City.country))
            .filter(models.City.is_deleted == False, models.Country.is_deleted == False)
        )

        total = record_query.count()
        record_query = record_query.offset((page - 1) * per_page).limit(per_page)

        return schemas.CountryResponseList(
            total=total,
            pages=math.ceil(total / per_page),
            per_page=per_page,
            current_page=page,
            data=record_query
        )

    @classmethod
    def get_many_contry(
            cls,
            db: Session,
            page: int = 1,
            per_page: int = 5,
            order: Optional[str] = None,
            order_field: Optional[str] = None,
            keyword: Optional[str] = None,

    ):
        record_query = db.query(models.Country).filter(models.Country.is_deleted == False)

        if keyword:
            record_query = record_query.filter(
                or_(
                    models.Country.name.ilike(f'%{keyword}%'),
                    models.Country.code.ilike(f'%{keyword}%'),
                    models.Country.uuid.ilike(f'%{keyword}%'),

                )
            )

        if order and order_field and hasattr(models.Country, order_field):
            if order == "asc":
                record_query = record_query.order_by(getattr(models.Country, order_field).asc())
            else:
                record_query = record_query.order_by(getattr(models.Country, order_field).desc())

        total = record_query.count()

        record_query = record_query.offset((page - 1) * per_page).limit(per_page)

        return schemas.CountryResponseListSlim(
            total=total,
            pages=math.ceil(total / per_page),
            per_page=per_page,
            current_page=page,
            data=record_query,
        )


    @classmethod
    def get_city_by_contry_uuid(cls,db: Session,*, country_uuid: str) -> Optional[models.City]:
        return db.query(models.City).filter(models.City.country_uuid == country_uuid,models.City.is_deleted==False).all()


    @classmethod
    def get_all_country(cls,db:Session):
        return db.query(models.Country).filter(models.Country.is_deleted == False).all()


country_with_city = CountryWithCityCRUD(models.Country)