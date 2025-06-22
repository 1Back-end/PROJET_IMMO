from typing import Any, List
from fastapi import APIRouter, Depends, Body, HTTPException
from sqlalchemy.orm import Session
from app.main.core.dependencies import get_db, TokenRequired
from app.main import schemas, crud, models
from app.main.core.i18n import __
from app.main.core.config import Config
from app.main.core.dependencies import TokenRequired

router = APIRouter(prefix="/requets", tags=["requets"])

@router.post("/create", response_model=schemas.Msg)
async def create_license_request(
        *,
        db: Session = Depends(get_db),
        obj_in: schemas.LicenceRequestCreate,
        current_user: models.User = Depends(TokenRequired(roles=["OWNER"]))
):
    crud.licence_request.create(
        db=db,
        obj_in=obj_in,
        send_by=current_user.uuid
    )
    return schemas.Msg(message=__(key="request-send-successfully"))



@router.put("/licence-request-is-read",response_model=schemas.Msg)
async def licence_request_is_read(
        *,
        db: Session = Depends(get_db),
        obj_in: schemas.LicenceRequestIsRead,
        current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN"]))
):
    crud.licence_request.change_is_read(
        db=db,
        uuid=obj_in.uuid,
    )
    return schemas.Msg(message=__(key="request-read-successfully"))

@router.delete("/drop-delete-licence-request",response_model=schemas.Msg)
async def licence_request_drop_delete(
        *,
        db: Session = Depends(get_db),
        obj_in: schemas.LicenceRequestIsRead,
        current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN"]))
):
    crud.licence_request.delete(
        db=db,
        uuid=obj_in.uuid,
    )
    return schemas.Msg(message=__(key="request-deleted-successfully"))

@router.put("/soft-delete-licence-request",response_model=schemas.Msg)
async def licence_request_soft_delete(
        *,
        db: Session = Depends(get_db),
        obj_in: schemas.LicenceRequestIsRead,
        current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN"]))
):
    crud.licence_request.soft_delete(
        db=db,
        uuid=obj_in.uuid,
    )
    return schemas.Msg(message=__(key="request-deleted-successfully"))


@router.get("/get_all_licence_request", response_model=None)
def get(
    *,
    db: Session = Depends(get_db),
    page: int = 1,
    per_page: int = 25,
    current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN","ADMIN"]))
):
    return crud.licence_request.get_many(
        db,
        page,
        per_page,
    )


@router.get("/get_all_request_clients", response_model=List[schemas.LicenseResponse])
async def get_all_request_clients(
        db: Session = Depends(get_db),
        current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN"]))
):
    return crud.licence_request.get_all_requests(
        db=db
    )