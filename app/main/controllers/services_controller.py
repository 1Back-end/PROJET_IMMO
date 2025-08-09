from datetime import timedelta, datetime
from typing import Any, Optional
from fastapi import APIRouter, Depends, Body, HTTPException
from sqlalchemy.orm import Session
from app.main.core.dependencies import get_db, TokenRequired
from app.main import schemas, crud, models
from app.main.core.i18n import __
from app.main.core.dependencies import TokenRequired

router = APIRouter(prefix="/services", tags=["services"])

@router.post("/create",response_model=schemas.Msg)
async  def create_services(
        *,
        db: Session = Depends(get_db),
        obj_in: schemas.ServiceCreate,
        current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN","ADMIN"]))
):
    exist_service = crud.services.get_by_name(db=db, name=obj_in.name)
    if exist_service:
        raise HTTPException(
            status_code=409,
            detail=__(key="service-already-exists")
        )


    crud.services.create(
        db=db,
        obj_in=obj_in,
        added_by=current_user.uuid
    )
    return schemas.Msg(message=__(key="service-created-successfully"))


@router.put("/update",response_model=schemas.Msg)
async def update_services(
        *,
        db: Session = Depends(get_db),
        obj_in: schemas.ServiceUpdate,
        current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN","ADMIN"]))
):
    crud.services.update(
        db=db,
        obj_in=obj_in,
        added_by=current_user.uuid,
    )
    return schemas.Msg(message=__(key="service-updated-successfully"))

@router.delete("/delete",response_model=schemas.Msg)
async def delete_services(
        *,
        db: Session = Depends(get_db),
        obj_in: schemas.ServiceDelete,
        current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN"]))
):
    crud.services.delete(
        db=db,
        obj_in=obj_in,
    )
    return schemas.Msg(message=__(key="service-deleted-successfully"))


@router.put("/soft-delete",response_model=schemas.Msg)
async def soft_delete_services(
        *,
        db: Session = Depends(get_db),
        obj_in: schemas.ServiceDelete,
        current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN"]))
):
    crud.services.soft_delete(
        db=db,
        uuid=obj_in.uuid,
    )
    return schemas.Msg(message=__(key="service-deleted-successfully"))


@router.put("/update-status",response_model=schemas.Msg)
async def update_services_status(
        *,
        db: Session = Depends(get_db),
        obj_in: schemas.ServiceUpdateStatus,
        current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN","ADMIN"]))
):
    if obj_in.status not in ["active", "inactive"]:
        raise HTTPException(status_code=400, detail=__(key="status-invalid"))
    crud.services.update_status(
        db=db,
        uuid=obj_in.uuid,
        status=obj_in.status
    )
    return schemas.Msg(message=__(key="status-service-updated-successfully"))


@router.get("/get_by_uuid",response_model=schemas.Service)
async def get_service_by_uuid(
        *,
        db: Session = Depends(get_db),
        uuid:str,
        current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN","ADMIN"]))
):
    service = crud.services.get_by_uuid(db=db, uuid=uuid)
    if not service:
        raise HTTPException(status_code=404, detail=__(key="service-not-found"))
    return service



@router.get("/get_all_services", response_model=None)
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
    return crud.services.get_many(
        db,
        page,
        per_page,
        order,
        order_field,
        keyword,
        status,
    )