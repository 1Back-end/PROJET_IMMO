from datetime import timedelta, datetime
from typing import Any, List
from fastapi import APIRouter, Depends, Body, HTTPException, Query
from sqlalchemy.orm import Session
from app.main.core.dependencies import get_db, TokenRequired
from app.main import schemas, crud, models
from app.main.core.i18n import __
from app.main.core.security import create_access_token, get_password_hash
from app.main.core.config import Config
from app.main.core.dependencies import TokenRequired

router = APIRouter(prefix="/users", tags=["users"])



@router.post("/register",response_model=schemas.Msg)
def register(
    *,
    db: Session = Depends(get_db),
    obj_in:schemas.UserCreate,
    # current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN"]))
):
    if obj_in.avatar_uuid:
        avatar = crud.storage_crud.get_file_by_uuid(db=db,file_uuid=obj_in.avatar_uuid)
        if not avatar:
            raise HTTPException(status_code=404, detail=__(key="avatar-not-found"))
    
    exist_phone = crud.user.get_by_phone_number(db=db, phone_number=obj_in.phone_number)
    if exist_phone:
        raise HTTPException(status_code=409, detail=__(key="phone_number-already-used"))

    exist_email = crud.user.get_by_email(db=db, email=obj_in.email)
    if exist_email:
        raise HTTPException(status_code=409, detail=__(key="email-already-used"))
    crud.user.create(
        db, obj_in=obj_in
    )
    return schemas.Msg(message=__(key="user-created-successfully"))


@router.put("/update",response_model=schemas.Msg)
def update(
    *,
    db: Session = Depends(get_db),
    obj_in:schemas.UserUpdate,
    current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN"]))
):
    if obj_in.avatar_uuid:
        avatar = crud.storage_crud.get_file_by_uuid(db=db,file_uuid=obj_in.avatar_uuid)
        if not avatar:
            raise HTTPException(status_code=404, detail=__(key="avatar-not-found"))
    crud.user.update_user(
        db, obj_in=obj_in
    )
    return schemas.Msg(message=__(key="user-updated-successfully"))

@router.put("/update-status",response_model=schemas.Msg)
def update_status(
    *,
    db: Session = Depends(get_db),
    obj_in:schemas.UpdateStatus,
    current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN"]))
):
    crud.user.update(
        db,
        uuid=obj_in.uuid,
        status=obj_in.status
    )
    return schemas.Msg(message=__(key="user-status-updated-successfully"))

@router.get("/get_all_users", response_model=List[schemas.User])
def get_user_list(
    *,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN"]))
):
   users = crud.user.get_all_users(db=db)
   return users
    
@router.put("/delete-user",response_model=schemas.Msg)
def delete_user(
    *,
    db: Session = Depends(get_db),
    obj_in:schemas.UserDelete,
    current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN"]))
):
    crud.user.delete(db=db, uuid=obj_in.uuid)
    return schemas.Msg(message=__(key="user-deleted-successfully"))

@router.get("/get_many", response_model=None)
def get(
    *,
    db: Session = Depends(get_db),
    page: int = 1,
    per_page: int = 25,
    current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN","ADMIN"]))
):
    """
    get administrator with all data by passing filters
    """
    
    return crud.user.get_many(
        db, 
        page, 
        per_page, 
    )

@router.get("/get_by_uuid",response_model=schemas.UserResponseInfo)
def get_user_by_uuid(
    *,
    db: Session = Depends(get_db),
    uuid:str,
    current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN","ADMIN"]))
):
    return crud.user.get_by_uuid(db=db,uuid=uuid)