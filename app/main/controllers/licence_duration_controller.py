from datetime import timedelta, datetime
from typing import Any
from fastapi import APIRouter, Depends, Body, HTTPException
from sqlalchemy.orm import Session
from app.main.core.dependencies import get_db, TokenRequired
from app.main import schemas, crud, models
from app.main.core.i18n import __
from app.main.core.config import Config
from app.main.core.dependencies import TokenRequired

router = APIRouter(prefix="/licence_duration", tags=["licence_duration"])

@router.post("/create",response_model=schemas.Msg)
async def create_licence_duration(
        *,
        db: Session = Depends(get_db),
        obj_in:schemas.LicenceDurationCrete,
        current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN", "ADMIN"]))
):
    crud.licence_duration.create(
        db=db,
        obj_in=obj_in,
        added_by=current_user.uuid
    )
    return {"message": __(key="licence-duration-created-success")}



@router.get("/get-all-licence-duration", response_model=None)
async def get(
    *,
    db: Session = Depends(get_db),
    page: int = 1,
    per_page: int = 25,
    current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN","ADMIN","OWNER"]))
):
    return crud.licence_duration.get_many(
        db,
        page,
        per_page,
    )

@router.get("/get_by_uuid",response_model=schemas.LicenceDurationModel)
async def get_licence_duration_by_uuid(
        *,
        db: Session = Depends(get_db),
        uuid:str,
        current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN", "ADMIN"]))
):
    return crud.licence_duration.get_by_uuid(
        db=db,
        uuid=uuid,
    )

@router.put("/update-licence-duration",response_model=schemas.Msg)
async def update_licence_duration(
        *,
        db: Session = Depends(get_db),
        obj_in:schemas.LicenceDurationUpdateStatus,
        current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN", "ADMIN"]))
):
    crud.licence_duration.update_status(
        db=db,
        uuid=obj_in.uuid,
        is_active=obj_in.is_active
    )
    return {"message":__(key="licence-duration-updated-status")}


@router.put("/update",response_model=schemas.Msg)
async def update_licence(
        *,
        db: Session = Depends(get_db),
        obj_in:schemas.LicenceDurationUpdate,
        current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN", "ADMIN"]))
):
    crud.licence_duration.update(
        db=db,
        obj_in=obj_in,
        added_by=current_user.uuid
    )
    return {"message":__(key="licence-duration-updated")}


@router.delete("/drop-delete",response_model=schemas.Msg)
async def drop_delete_licence(
        *,
        db: Session = Depends(get_db),
        obj_in:schemas.LicenceDurationDelete,
        current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN", "ADMIN"]))
):
    crud.licence_duration.drop_delete(
        db=db,
        uuid=obj_in.uuid
    )
    return {"message":__(key="licence-duration-deleted-success")}


@router.put("/soft-delete",response_model=schemas.Msg)
async def soft_delete_licence(
        *,
        db: Session = Depends(get_db),
        obj_in:schemas.LicenceDurationDelete,
        current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN", "ADMIN"]))
):
    crud.licence_duration.soft_delete(
        db=db,
        uuid=obj_in.uuid
    )
    return {"message":__(key="licence-duration-deleted-success")}