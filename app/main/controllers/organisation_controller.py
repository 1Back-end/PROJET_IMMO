from datetime import timedelta, datetime
from typing import Any, Optional
from fastapi import APIRouter, Depends, Body, HTTPException
from sqlalchemy.orm import Session
from app.main.core.dependencies import get_db, TokenRequired
from app.main import schemas, crud, models
from app.main.core.i18n import __
from app.main.core.dependencies import TokenRequired
from app.main.crud import services
from typing import Optional, Literal
from fastapi import Query

router = APIRouter(prefix="/organisations", tags=["organisations"])


@router.post("/create",response_model=schemas.Msg,status_code=201)
async def create_organisation(
        *,
        db: Session = Depends(get_db),
        obj_in : schemas.OrganisationCreate,
):
    exist_organisation_name = crud.organisation.get_by_name(db=db,name=obj_in.company_name)
    if exist_organisation_name :
        raise HTTPException(status_code=409,detail=__(key="the-organisation-name-already-exists"))

    exist_organisation_email = crud.organisation.get_by_email(db=db,email=obj_in.company_email)
    if exist_organisation_email :
        raise  HTTPException(status_code=409,detail=__(key="the-organisation-email-already-exists"))

    exist_organisation_phone_number = crud.organisation.get_by_phone_number(db=db,phone_number=obj_in.company_phone_number)
    if exist_organisation_phone_number :
        raise HTTPException(status_code=409,detail=__(key="the-organisation-phone-number-already-exists"))

    exist_owner_email = crud.user.get_by_email(db=db,email=obj_in.owner_email)
    if exist_owner_email :
        raise HTTPException(status_code=409,detail=__(key="the-owner-email-already-exists"))

    exist_owner_phone_number = crud.user.get_by_phone_number(db=db,phone_number=obj_in.owner_phone_number)
    if exist_owner_phone_number :
        raise HTTPException(status_code=409,detail=__(key="the-owner-phone-number-already-exists"))

    service_uuids = obj_in.service_uuids
    services = crud.services.get_by_uuids(db=db, uuids=service_uuids)

    if not services or len(services) != len(service_uuids):
        raise HTTPException(status_code=404, detail=__(key="service-not-found"))

    crud.organisation.create(db=db, obj_in=obj_in)
    return schemas.Msg(message=__(key="organisation-created-successfully"))

@router.put("/update-status",response_model=schemas.Msg,status_code=200)
async def update_organisation_status(
        *,
        db: Session = Depends(get_db),
        obj_in : schemas.OrganisationUpdateStatus,
        current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN","ADMIN"]))
):
    if obj_in.status not in ["active","inactive"]:
        raise HTTPException(status_code=400,detail=__(key="status-not-found"))

    crud.organisation.update_status(
        db=db,
        uuid=obj_in.uuid,
        status=obj_in.status
    )
    return schemas.Msg(message=__(key="organisation-status-updated-successfully"))


@router.get("/get_all_services", response_model=None,status_code=200)
async def get_all_services(
    *,
    db: Session = Depends(get_db),
    page: int = 1,
    per_page: int = 5,
    order: Optional[str] = None,
    order_field: Optional[str] = None,
    keyword: Optional[str] = None,
    status: Optional[str] = None,
    #current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN","ADMIN"]))
):
    return crud.organisation.get_many(
        db,
        page,
        per_page,
        order,
        order_field,
        keyword,
        status,
    )


@router.get("/get_all_services_for_my_organisations", response_model=None,status_code=200)
async def get_all_services(
    *,
    db: Session = Depends(get_db),
    page: int = 1,
    per_page: int = 5,
    order: Optional[str] = None,
    order_field: Optional[str] = None,
    keyword: Optional[str] = None,
    status: Optional[str] = None,
    current_user: models.User = Depends(TokenRequired(roles=["OWNER"]))
):
    return crud.organisation.get_by_owner_uuid(
        db,
        page,
        per_page,
        order,
        order_field,
        keyword,
        status,
        owner_uuid=current_user.uuid,
    )




