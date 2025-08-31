import os
from datetime import timedelta, datetime, date
from typing import Any,Optional
from fastapi import APIRouter, Depends, Body, HTTPException,Query
from sqlalchemy.orm import Session
from starlette.responses import FileResponse

from app.main.core.dependencies import get_db, TokenRequired
from app.main import schemas, crud, models
from app.main.core.i18n import __
from app.main.core.config import Config
from app.main.core.dependencies import TokenRequired
from cryptography.hazmat.primitives.asymmetric import rsa

from app.main.core.mail import send_user_code_to_delete, send_user_code_to_confirmation
from app.main.core.security import generate_code

router = APIRouter(prefix="/licences", tags=["licences"])

@router.post("/send-otp-validation",response_model=schemas.Msg)
async def send_otp_validation(
        db: Session = Depends(get_db),
        current_user: models.User = Depends(TokenRequired(roles=["ADMIN","SUPER_ADMIN"]))
):
    owner = crud.user.get_by_email(db=db, email=current_user.email)
    if not owner:
        raise HTTPException(status_code=404, detail=__(key="user-not-found"))

    code = generate_code(length=12)
    code = str(code[0:5])
    print(f"Administrator Code Otp", code)
    owner.deletion_code = code
    owner.deletion_code_expires_at = datetime.utcnow() + timedelta(days=1)
    db.commit()
    db.refresh(owner)

    send_user_code_to_confirmation(
        email_to=owner.email,
        code=code,
        full_name=f"{owner.first_name} {owner.last_name}",
        expirate_at=owner.deletion_code_expires_at,
    )
    return {"message": "Un code a été envoyé à votre adresse e-mail."}


@router.post("/generate-licence", response_model=schemas.Msg)
async def generate_licence(
        *,
        db: Session = Depends(get_db),
        request:schemas.LicenceCreate,
        current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN","ADMIN"]))
):
    if current_user.deletion_code != request.code:
        raise HTTPException(status_code=400, detail=__(key="invalid-code"))

    if datetime.now() > current_user.deletion_code_expires_at:
        current_user.deletion_code = None
        db.commit()
        raise HTTPException(status_code=400, detail=__(key="code-expired"))

    existing_licence = db.query(models.License).filter(
        models.License.organization_uuid == request.organization_uuid,
        models.License.service_uuid == request.service_uuid,
        models.License.licence_duration_uuid == request.licence_duration_uuid,
        models.License.is_deleted == False
    ).first()
    if existing_licence:
        raise HTTPException(status_code=400, detail=__(key="service-already-has-this-duration-license"))

    licence_duration = crud.licence_duration.get_by_uuid(db=db, uuid=request.licence_duration_uuid)
    if not licence_duration:
        raise HTTPException(status_code=400, detail=__(key="licence-duration-not-found"))

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

    current_user.deletion_code = None
    current_user.deletion_code_expires_at = None
    db.commit()
    db.refresh(current_user)
    return schemas.Msg(message=__(key="licence-created-successfully"))


@router.get("/download")
async def download_license_file(
        *,
        license_uuid: str,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(TokenRequired(roles=["OWNER","SUPER_ADMIN","ADMIN","EDIMESTRE"]))
):
    license_obj = crud.licence.get_by_uuid(db=db, uuid=license_uuid)

    if not license_obj:
        raise HTTPException(status_code=404, detail=__(key="licence-not-found"))

    # Utilisez 'license_obj.added_by' pour construire le nom de fichier
    license_obj = crud.licence.get_by_uuid(db=db, uuid=license_uuid)

    if not license_obj:
        raise HTTPException(status_code=404, detail=__(key="licence-not-found"))

    # On récupère le nom du fichier depuis la DB
    file_name = license_obj.certificate_file  # champ à ajouter dans ton modèle License
    file_path = os.path.join("certificats", file_name)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=__(key="file-not-found"))

    # Retourne le fichier avec le bon nom
    return FileResponse(
        path=file_path,
        media_type="application/octet-stream",
        filename=file_name
    )
@router.get("/get-licence-by_uuid", response_model=schemas.Licence)
async def get_licence_by_uuid(
        *,
        db: Session = Depends(get_db),
        uuid:str,
        current_user: models.User = Depends(TokenRequired(roles=["OWNER","SUPER_ADMIN","ADMIN"]))
):
    return crud.licence.get_by_uuid(db=db, uuid=uuid)

@router.put("/extend-licence", response_model=schemas.Msg)
async def extend_licence(
        *,
        db: Session = Depends(get_db),
        obj_in:schemas.ActivedLicence,
        current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN","ADMIN"]))
):
    if current_user.deletion_code != obj_in.code:
        raise HTTPException(status_code=400, detail=__(key="invalid-code"))

    if datetime.now() > current_user.deletion_code_expires_at:
        current_user.deletion_code = None
        db.commit()
        raise HTTPException(status_code=400, detail=__(key="code-expired"))

    crud.licence.extend_licence_service(
        db=db,
        licence_uuid=obj_in.licence_uuid,
        service_uuid=obj_in.service_uuid,
        licence_duration_uuid=obj_in.licence_duration_uuid,

    )
    current_user.deletion_code = None
    current_user.deletion_code_expires_at = None
    db.commit()
    db.refresh(current_user)
    return schemas.Msg(message=__(key="licence-prolonged"))


@router.put("/revoke_licence",response_model=schemas.Msg)
async def revoke_licence(
        *,
        db: Session = Depends(get_db),
        obj_in:schemas.RevokedLicence,
        current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN"]))
):
    if current_user.deletion_code != obj_in.code:
        raise HTTPException(status_code=400, detail=__(key="invalid-code"))

    if datetime.now() > current_user.deletion_code_expires_at:
        current_user.deletion_code = None
        db.commit()
        raise HTTPException(status_code=400, detail=__(key="code-expired"))

    crud.licence.revoke_licence(
        db=db,
        uuid=obj_in.uuid,
    )
    current_user.deletion_code = None
    current_user.deletion_code_expires_at = None
    return schemas.Msg(message=__(key="licence-revoked-successfully"))



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

@router.put("/soft-delete",response_model=schemas.Msg)
async def soft_delete_licence(
        *,
        db: Session = Depends(get_db),
        obj_in:schemas.DeleteLicence,
        current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN","ADMIN"]))
):
    crud.licence.soft_delete(
        db=db,
        uuid=obj_in.uuid
    )
    return schemas.Msg(message=__(key="licence-deleted-successfully"))

@router.delete("/drop_delete",response_model=schemas.Msg)
async def drop_delete_licence(
        *,
        db: Session = Depends(get_db),
        obj_in:schemas.RenouvelLicence,
        current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN","ADMIN"]))
):
    crud.licence.drop_delete(
        db=db,
        uuid=obj_in.uuid
    )
    return schemas.Msg(message=__(key="licence-deleted-successfully"))


@router.get("/get-all-licences", response_model=None)
async def get_all_licences_generator(
    *,
    db: Session = Depends(get_db),
    page: int = 1,
    per_page: int = 30,
    order: str = Query(None, enum=["ASC", "DESC"]),
    status: str = Query(None, enum=[st.value for st in models.LicenceStatus]),
    keyword: Optional[str] = None,
    order_field: Optional[str] = None,
    current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN","ADMIN","EDIMESTRE"]))
):
    return crud.licence.get_all_licence(
        db=db,
        page=page,
        per_page=per_page,
        order=order,
        status=status,
        order_field=order_field,  # Correction ici aussi
        keyword=keyword,
    )


@router.get("/get-all-licences-my-licence", response_model=None)
async def get_all_licence_for_my_organisation(
    *,
    db: Session = Depends(get_db),
    page: int = 1,
    per_page: int = 30,
    order: str = Query(None, enum=["ASC", "DESC"]),
    status: str = Query(None, enum=[st.value for st in models.LicenceStatus]),
    keyword: Optional[str] = None,
    order_field: Optional[str] = None,  # Correction de order_filed → order_field
    current_user: models.User = Depends(TokenRequired(roles=["OWNER"]))
):
    return crud.licence.get_all_my_licence(
        db=db,
        page=page,
        per_page=per_page,
        order=order,
        status=status,
        order_field=order_field,  # Correction ici aussi
        keyword=keyword,
        owner_uuid=current_user.uuid,
    )



@router.get("/check/{license_uuid}")
def check_licence(
        license_uuid: str,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(TokenRequired(roles=["OWNER"]))
):
    licence = db.query(models.License).filter(
        models.License.uuid == license_uuid,
        models.License.is_deleted == False,
        models.License.added_by==current_user.uuid,
    ).first()

    if not licence:
        raise HTTPException(status_code=404, detail=__(key="licence-not-found"))

    # Vérifie si expirée
    if licence.is_expired:
        licence.status = models.LicenceStatus.expired.value
        db.commit()
        return {"status": "expired", "expires_at": licence.expires_at}

    return {"status": licence.status, "expires_at": licence.expires_at}

