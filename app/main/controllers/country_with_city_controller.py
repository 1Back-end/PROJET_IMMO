from datetime import timedelta, datetime
from typing import Any, Optional, List
from fastapi import APIRouter, Depends, Body, HTTPException,UploadFile, File
from sqlalchemy.orm import Session
from app.main.core.dependencies import get_db, TokenRequired
from app.main import schemas, crud, models
from app.main.core.i18n import __
from app.main.core.config import Config
from app.main.core.dependencies import TokenRequired
import csv
from io import StringIO

router = APIRouter(prefix="/uploads_contry_with_city", tags=["uploads_contry_with_city"])

@router.post("/upload-country-cities",response_model=schemas.Msg)
async def upload_country_city_file(
        file: UploadFile = File(...),
        db: Session = Depends(get_db),
        current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN","ADMIN"]))
):
    content = await file.read()
    decoded = content.decode("utf-8")
    reader = csv.reader(StringIO(decoded), delimiter=";")

    count_countries = 0
    count_cities = 0

    for row in reader:
        if len(row) >= 6:
            # Exemple ligne : "1";"Afghanistan";"Kabul";"34.5166667";"69.1833344";"1808.0"
            _, country_name, city_name, lat, lon, alt = row

            # Créer ou récupérer le pays
            country = crud.country_with_city.get_by_country_name(db=db, country_name=country_name)
            if not country:
                country_schema = schemas.CountryWithCreate(name=country_name, code=country_name[:3].upper())
                country = crud.country_with_city.create_country(db=db, obj_in=country_schema)
                count_countries += 1

            # Créer la ville si elle n’existe pas
            city_schema = schemas.CityCreate(
                name=city_name,
                latitude=float(lat),
                longitude=float(lon),
                altitude=float(alt),
                country_uuid=country.uuid,
            )
            result = crud.country_with_city.create_city(db=db, obj_in=city_schema)
            if result:
                count_cities += 1

    return schemas.Msg(message=f"{count_countries} pays ajoutés, {count_cities} villes ajoutées (sans doublons).")



@router.get("/get_all_uploads_contry_with_city", response_model=None)
def get(
    *,
    db: Session = Depends(get_db),
    page: int = 1,
    per_page: int = 25,
    current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN","ADMIN","EDIMESTRE"]))
):
    return crud.country_with_city.get_many(
        db,
        page,
        per_page,
    )

@router.get("/get_all_contry_for_user_or_admin", response_model=None)
async def get_all_contry_for_user_or_admin(
    *,
    db: Session = Depends(get_db),
    page: int = 1,
    per_page: int = 5,
    order: Optional[str] = None,
    order_field: Optional[str] = None,
    keyword: Optional[str] = None,
    #current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN","ADMIN","EDIMESTRE"]))
):
    return crud.country_with_city.get_many_contry(
        db,
        page,
        per_page,
        order,
        order_field,
        keyword,
    )


@router.get("/get_all_city_for_country",response_model=List[schemas.CitySlim])
async def get_all_city_for_country(
        *,
        db: Session = Depends(get_db),
        country_uuid:str,
):
    data = crud.country_with_city.get_city_by_contry_uuid(
        db=db,
        country_uuid=country_uuid,
    )
    if not data:
        raise HTTPException(status_code=404,detail=__(key="city-not-found-for-country"))
    return data

@router.get("/get_all_country_list",response_model=List[schemas.CountrySlim])
async def get_all_country_list(
        *,
        db: Session = Depends(get_db),
):
    data = crud.country_with_city.get_all_country(
        db=db,
    )
    if not data:
        raise HTTPException(status_code=404,detail=__(key="country-not-found"))
    return data