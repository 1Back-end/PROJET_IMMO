from datetime import timedelta, datetime
from typing import Any
from fastapi import APIRouter, Depends, Body, HTTPException
from sqlalchemy.orm import Session
from app.main.core.dependencies import get_db, TokenRequired
from app.main import schemas, crud, models
from app.main.core.i18n import __
from app.main.core.config import Config
from app.main.core.dependencies import TokenRequired

router = APIRouter(prefix="/address", tags=["address"])

@router.post("/create",response_model=schemas.Msg)
async def create_address(
    *,
    db: Session = Depends(get_db),
    obj_in : schemas.AddressCreate,
    current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN","ADMIN"]))
):
    crud.address.create(db=db,obj_in=obj_in)
    return schemas.Msg(message=__(key="address-created-successfully"))


@router.put("/edit",response_model=schemas.Msg)
def update_address(
    *,
    db: Session = Depends(get_db),
    obj_in : schemas.AddressUpdate,
    current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN","ADMIN"]))
):
    crud.address.update(db=db,obj_in=obj_in)
    return schemas.Msg(message=__(key="address-updated-successfully"))

@router.get("",response_model=schemas.Address)
def get_address(
    *,
    db: Session = Depends(get_db),
    obj_in:schemas.AddressInfo,
    current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN","ADMIN"]))
):
    return crud.address.get_by_uuid(db=db,uuid=obj_in.uuid)