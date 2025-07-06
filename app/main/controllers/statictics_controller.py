from datetime import timedelta, datetime
from typing import Any
from fastapi import APIRouter, Depends, Body, HTTPException
from sqlalchemy.orm import Session
from app.main.core.dependencies import get_db, TokenRequired
from app.main import schemas, crud, models
from app.main.core.i18n import __
from app.main.core.config import Config
from app.main.core.dependencies import TokenRequired

router = APIRouter(prefix="/statistics", tags=["statistics"])


@router.get("/count-users", summary="Nombre total d'utilisateurs", description="Renvoie le nombre total d'utilisateurs valides selon leur rôle.")
async def count_users(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN"]))
):
    total_users = db.query(models.User).filter(
        models.User.role.in_(["ADMIN", "EDIMESTRE"]),
        models.User.is_deleted == False
    ).count()

    return {"total_users": total_users}


@router.get("/count-organisations")
async def count_organisations(
        db: Session = Depends(get_db),
        current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN"]))
):
    total_organisations = db.query(models.Organisation).filter(models.Organisation.is_deleted == False).count()
    return {"total_organisations": total_organisations}


@router.get("/count-services")
async def count_services(
        db: Session = Depends(get_db),
        current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN"]))
):
    total_services = db.query(models.Service).filter(models.Service.is_deleted == False).count()
    return {"total_services": total_services}