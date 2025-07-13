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

router = APIRouter(prefix="/licences", tags=["licences"])


@router.post("/generate-licence", response_model=schemas.Msg)
async def generate_licence(
        *,
        db: Session = Depends(get_db),
        request:schemas.LicenceCreate,
        current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN","ADMIN"]))
):
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
    return schemas.Msg(message=__(key="licence-created-successfully"))


@router.get("/download")
async def download_license_file(
        *,
        license_uuid: str,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(TokenRequired(roles=["OWNER"]))
):
    license_obj = crud.licence.get_by_uuid(db=db, uuid=license_uuid)

    if not license_obj:
        raise HTTPException(status_code=404, detail=__(key="licence-not-found"))
    license_key = license_obj.license_key

    file_path = f"certificats/{license_key}.txt"

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=__(key="file-not-found"))

    return FileResponse(path=file_path, media_type='application/octet-stream', filename=f"{license_key}.txt")

@router.get("/get-licence-by_uuid", response_model=schemas.Licence)
async def get_licence_by_uuid(
        *,
        db: Session = Depends(get_db),
        uuid:str,
        current_user: models.User = Depends(TokenRequired(roles=["OWNER","SUPER_ADMIN","ADMIN"]))
):
    return crud.licence.get_by_uuid(db=db, uuid=uuid)

@router.post("/actived-licence", response_model=schemas.Msg)
async def update_actived_licence(
        *,
        db: Session = Depends(get_db),
        obj_in:schemas.ActivedLicence,
        current_user: models.User = Depends(TokenRequired(roles=["OWNER"]))
):

    crud.licence.activate_service(
        db=db,
        licence_uuid=obj_in.licence_uuid,
        service_uuid=obj_in.service_uuid,
        encrypted_data = obj_in.encrypted_data
    )
    return schemas.Msg(message=__(key="licence-activate-successfully"))


@router.put("/revoke-licence",response_model=schemas.Msg)
async def revoke_licence(
        *,
        db: Session = Depends(get_db),
        obj_in:schemas.ActivedLicence,
        current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN"]))
):
    crud.licence.revoke_licence(
        db=db,
        licence_uuid=obj_in.licence_uuid,
        service_uuid=obj_in.service_uuid,
        encrypted_data = obj_in.encrypted_data
    )
    return schemas.Msg(message=__(key="licence-revoked-successfully"))


@router.post("/prolonged-licence", response_model=schemas.Msg)
async def prolonged_licence(
        *,
        db: Session = Depends(get_db),
        obj_in: schemas.ProlongedLicence,
        current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN"]))
):

    crud.licence.prolonge_licence(
        db=db,
        uuid=obj_in.uuid,
        number_of_days=obj_in.number_of_days
    )
    return schemas.Msg(message=__(key="licence-prolonged"))




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
    order_field: Optional[str] = None,  # Correction de order_filed → order_field
    #current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN","ADMIN"]))
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


