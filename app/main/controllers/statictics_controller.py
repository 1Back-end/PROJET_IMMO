from datetime import timedelta, datetime
from typing import Any
from fastapi import APIRouter, Depends, Body, HTTPException
from sqlalchemy import func
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
    current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN","ADMIN"]))
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
        current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN","ADMIN"]))
):
    total_services = db.query(models.Service).filter(models.Service.is_deleted == False).count()
    return {"total_services": total_services}


@router.get("/stats/licence-durations")
async def licence_duration_stats(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN","ADMIN"]))
):
    results = (
        db.query(
            models.LicenceDuration.key,
            func.count(models.License.uuid).label("total")
        )
        .join(models.License, models.License.licence_duration_uuid == models.LicenceDuration.uuid)
        .filter(models.License.is_deleted == False)
        .group_by(models.LicenceDuration.key)
        .order_by(func.count(models.License.uuid).desc())
        .all()
    )

    return {"durations": [{"duration": r[0], "count": r[1]} for r in results]}


@router.get("/licence_durations_by_status", status_code=200)
async def licence_durations_by_status(
        db: Session = Depends(get_db),
        current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN","ADMIN"]))
):
    # Récupérer le nombre et la dernière date d'expiration pour chaque statut
    stats = db.query(
        models.License.status,
        func.count(models.License.uuid),
        func.max(models.License.expires_at)  # date approximative
    ).filter(
        models.License.is_deleted == False,
        models.License.status != None
    ).group_by(models.License.status).all()

    # Convertir en dict pour remplir les statuts manquants
    data = {status: {"count": 0, "expires_at": None} for status in models.LicenceStatus}

    for status, count, expires_at in stats:
        data[status] = {"count": count, "expires_at": expires_at}

    # Préparer le résultat
    result = [
        {"status": status.value, "count": data[status.value]["count"], "date": data[status.value]["expires_at"]}
        for status in models.LicenceStatus
    ]

    return result