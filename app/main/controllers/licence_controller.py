from datetime import timedelta, datetime
from typing import Any
from fastapi import APIRouter, Depends, Body, HTTPException
from sqlalchemy.orm import Session
from app.main.core.dependencies import get_db, TokenRequired
from app.main import schemas, crud, models
from app.main.core.i18n import __
from app.main.core.config import Config
from app.main.core.dependencies import TokenRequired
from cryptography.hazmat.primitives.asymmetric import rsa

router = APIRouter(prefix="/licences", tags=["licences"])


@router.post("/generate-licence", response_model=schemas.Msg)
async def generate_licence(
        *,
        db: Session = Depends(get_db),
        request:schemas.LicenceCreate,
        current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN","ADMIN"]))
):
    organisation = crud.organisation.get_by_uuid(db=db, uuid=request.organization_uuid)
    if not organisation:
        raise HTTPException(status_code=404, detail=__(key="organisation-not-found"))

    service = crud.services.get_by_uuid(db=db, uuid=request.service_uuid)
    if not service:
        raise HTTPException(status_code=404, detail=__(key="service-not-found"))

    crud.licence.create(
        db=db,
        request=request,
        added_by=current_user.uuid
    )
    return schemas.Msg(message=__(key="licence-created-successfully"))



@router.put("/actived-licence", response_model=schemas.Msg)
async def update_actived_licence(
        *,
        db: Session = Depends(get_db),
        obj_in:schemas.ActivedLicence,
        current_user: models.User = Depends(TokenRequired(roles=["OWNER"]))
):
    licence = crud.licence.get_by_uuid(db=db, uuid=obj_in.uuid)
    if not licence:
        raise HTTPException(status_code=404, detail=__(key="licence-not-found"))
    if licence.owner_uuid != current_user.uuid:
        raise HTTPException(status_code=403, detail=__(key="not-allowed"))
    crud.licence.activate_service(
        db=db,
        uuid=obj_in.uuid,
        service_uuid=obj_in.service_uuid
    )
    return schemas.Msg(message=__(key="licence-activate-successfully"))


@router.put("/renouvel-licence", response_model=schemas.Msg)
async def update_renouvel_licence(
        *,
        db: Session = Depends(get_db),
        obj_in:schemas.RenouvelLicence,
        current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN","ADMIN"]))
):
    crud.licence.renouvel_licence(
        db=db,
        uuid=obj_in.uuid,
        new_start_date=obj_in.new_start_date
    )
    return schemas.Msg(message=__(key="licence-renouvel-successfully"))

