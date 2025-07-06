from datetime import timedelta, datetime
from typing import Any
from fastapi import APIRouter, Depends, Body, HTTPException
from sqlalchemy.orm import Session
from app.main.core.dependencies import get_db, TokenRequired
from app.main import schemas, crud, models
from app.main.core.i18n import __
from app.main.core.config import Config
from app.main.core.dependencies import TokenRequired

router = APIRouter(prefix="/licence_response_service", tags=["licence_response_service"])


@router.post("/create",response_model=schemas.Msg)
async def create_licence_response_service(
        *,
        db: Session = Depends(get_db),
        obj_in: schemas.LicenceRequestCreate,
        current_user: models.User = Depends(TokenRequired(roles=["OWNER"]))
):
    crud.licence_response_service.create(
        db=db,
        obj_in=obj_in,
        added_by=current_user.uuid
    )
    return schemas.Msg(message=__(key="request-send-successfully"))


@router.get("/get_many", response_model=None)
def get(
    *,
    db: Session = Depends(get_db),
    page: int = 1,
    per_page: int = 25,
    #current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN","ADMIN"]))
):
    return crud.licence_response_service.get_many(
        db,
        page,
        per_page,
    )


@router.put("/update-licence-request-status",response_model=schemas.Msg)
async def update_licence_request_status(
        *,
        db: Session = Depends(get_db),
        obj_in: schemas.LicenceRequestUpdateStatus,
        current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN"]))
):
    if obj_in.status not in ["accepted", "declined"]:
        raise HTTPException(status_code=400, detail=__(key="invalid-status"))
    crud.licence_response_service.update_status(
        db=db,
        licence_uuid=obj_in.uuid,
        status=obj_in.status
    )
    return schemas.Msg(message=__(key="request-update-successfully"))


@router.get("/get_by_uuid",response_model=schemas.LicenceRequestServiceResponse)
async def get_licence_response(
        *,
        db: Session = Depends(get_db),
        uuid:str,
        #current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN"]))
):
    return crud.licence_response_service.get_by_uuid(
        db=db,
        uuid=uuid,
    )