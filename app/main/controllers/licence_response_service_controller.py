import uuid
from datetime import timedelta, datetime
from typing import Any
from fastapi import APIRouter, Depends, Body, HTTPException
from sqlalchemy.orm import Session
from app.main.core.dependencies import get_db, TokenRequired
from app.main import schemas, crud, models
from app.main.core.i18n import __
from app.main.core.config import Config
from app.main.core.dependencies import TokenRequired
from app.main.core.mail import send_new_request, send_notify_pending_request, send_expiration_email

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


@router.post("/extend",response_model=schemas.Msg)
async def extend_licence_response_service(
        *,
        db: Session = Depends(get_db),
        obj_in: schemas.LicenceRequestServiceExtend,
        current_user: models.User = Depends(TokenRequired(roles=["OWNER"]))
):

    crud.licence_response_service.extend_licence(
        db=db,
        obj_in=obj_in,
        added_by=current_user.uuid
    )
    return schemas.Msg(message=__(key="request-send-successfully"))


@router.post("/extend-licence",response_model=schemas.Msg)
async def create_licence_response_service_extend(
        *,
        db: Session = Depends(get_db),
        obj_in: schemas.LicenceRequestServiceExtend,
        current_user: models.User = Depends(TokenRequired(roles=["OWNER"]))
):

    crud.licence_response_service.extend_licence(
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
    current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN","ADMIN","EDIMESTRE"]))
):
    return crud.licence_response_service.get_many(
        db,
        page,
        per_page,
    )

@router.get("/get_all_requets", response_model=None)
def get_all_requests(
    *,
    db: Session = Depends(get_db),
    page: int = 1,
    per_page: int = 25,
    current_user: models.User = Depends(TokenRequired(roles=["OWNER"]))
):
    return crud.licence_response_service.get_my_requests(
        db,
        page,
        per_page,
        added_by=current_user.uuid
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

@router.post("/notify-pending", response_model=schemas.Msg)
def notify_pending_requests(db: Session = Depends(get_db)):
    pending_requests = db.query(models.LicenceRequestService).filter(
        models.LicenceRequestService.status == "pending"
    ).all()

    if not pending_requests:
        raise HTTPException(status_code=404, detail="Aucune demande en attente trouvée.")

    admins = db.query(models.User).filter(
        models.User.is_deleted == False,
        models.User.role.in_(["SUPER_ADMIN", "ADMIN", "EDIMESTRE"])
    ).all()

    for req in pending_requests:
        created_at_str = req.created_at.strftime("%d/%m/%Y %H:%M")
        owner_name = f"{req.creator.first_name} {req.creator.last_name}" if req.creator else "Inconnu"
        service_name = req.service.name if req.service else "Inconnu"
        licence_duration = req.licence_duration.key if req.licence_duration and req.licence_duration.key else "Non spécifié"

        for admin in admins:
            send_notify_pending_request(
                email_to=admin.email,
                title=req.type,
                licence_type=req.type,
                owner_name=owner_name,
                service_name=service_name,
                licence_duration=licence_duration,
                description=req.description or "",
                created_at=created_at_str,
                status="Non traitée"
            )

    return {"message": f"{len(pending_requests)} notifications envoyées avec succès."}



from sqlalchemy import or_

@router.post("/notify-expired-licenses")
def notify_expired_licenses_endpoint(db: Session = Depends(get_db)):
    now = datetime.utcnow()
    expired_licenses = db.query(models.License).filter(
        models.License.is_deleted == False,
        or_(
            (models.License.status == "active") &
            (models.License.expires_at != None) &
            (models.License.expires_at < now),
            models.License.status == "expired"
        )
    ).all()

    if not expired_licenses:
        raise HTTPException(status_code=404, detail="Aucune licence expirée à notifier.")

    count = 0
    for license in expired_licenses:
        if license.status == "active":
            license.status = "expired"
            db.add(license)

    db.commit()

    for license in expired_licenses:
        if license.creator and license.creator.email:
            expires_str = license.expires_at.strftime("%d/%m/%Y %H:%M UTC") if license.expires_at else "Date inconnue"
            send_expiration_email(
                email_to=license.creator.email,
                license_key=license.license_key,
                organisation_name=license.organisation.name if license.organisation else "Votre organisation",
                service_name=license.service.name if license.service else "Service",
                expires_at=expires_str,
            )
            count += 1

    return {"message": f"{count} licences expirées notifiées avec succès."}



@router.put("/cancel-request-licenses", response_model=schemas.Msg)
async def cancel_pending_requests(
        *,
        db: Session = Depends(get_db),
        obj_in: schemas.LicenceRequestCancel,
        current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN","ADMIN","EDIMESTRE"])),

):
    if current_user.deletion_code != obj_in.code:
        raise HTTPException(status_code=400, detail=__(key="invalid-code"))

    if datetime.now() > current_user.deletion_code_expires_at:
        current_user.deletion_code = None
        db.commit()
        raise HTTPException(status_code=400, detail=__(key="code-expired"))

    crud.licence_response_service.cancel_request_licence(
        db=db,
        request_uuid=obj_in.request_uuid
    )
    current_user.deletion_code = None
    current_user.deletion_code_expires_at = None
    db.commit()
    db.refresh(current_user)
    return schemas.Msg(message=__(key="request-cancelled"))
