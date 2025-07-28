from datetime import timedelta, datetime
from typing import Any, Optional
from fastapi import APIRouter, Depends, Body, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.main.core.dependencies import get_db, TokenRequired
from app.main import schemas, crud, models
from app.main.core.i18n import __
from app.main.core.dependencies import TokenRequired
from app.main.core.mail import send_organisation_otp_to_user
from app.main.core.security import generate_code
from app.main.crud import services
from typing import Optional, Literal
from fastapi import Query

router = APIRouter(prefix="/organisations", tags=["organisations"])


@router.post("/create",response_model=schemas.Msg,status_code=201)
async def create_organisation(
        *,
        db: Session = Depends(get_db),
        obj_in : schemas.OrganisationCreate,
        background_tasks: BackgroundTasks
):
    exist_organisation_name = crud.organisation.get_by_name(db=db,name=obj_in.company_name)
    if exist_organisation_name :
        raise HTTPException(status_code=409,detail=__(key="the-organisation-name-already-exists"))

    exist_organisation_email = crud.organisation.get_by_email(db=db,email=obj_in.company_email)
    if exist_organisation_email :
        raise  HTTPException(status_code=409,detail=__(key="the-organisation-email-already-exists"))

    exist_organisation_phone_number = crud.organisation.get_by_phone_number(db=db,phone_number=obj_in.company_phone_number)
    if exist_organisation_phone_number :
        raise HTTPException(status_code=409,detail=__(key="the-organisation-phone-number-already-exists"))

    exist_owner_email = crud.user.get_by_email(db=db,email=obj_in.owner_email)
    if exist_owner_email :
        raise HTTPException(status_code=409,detail=__(key="the-owner-email-already-exists"))

    exist_owner_phone_number = crud.user.get_by_phone_number(db=db,phone_number=obj_in.owner_phone_number)
    if exist_owner_phone_number :
        raise HTTPException(status_code=409,detail=__(key="the-owner-phone-number-already-exists"))

    city = crud.country_with_city.get_city_by_uuid(
        db=db,
        uuid=obj_in.city_uuid
    )
    if not city:
        raise HTTPException(status_code=404,detail=__(key="city-not-found"))

    country = crud.country_with_city.get_country_by_uuid(
        db=db,
        uuid=obj_in.country_uuid
    )
    if not country:
        raise HTTPException(status_code=404,detail=__(key="country-not-found"))

    service_uuids = obj_in.service_uuids
    services = crud.services.get_by_uuids(db=db, uuids=service_uuids)

    if not services or len(services) != len(service_uuids):
        raise HTTPException(status_code=404, detail=__(key="service-not-found"))

    crud.organisation.create(db=db, obj_in=obj_in,background_tasks=background_tasks)
    return schemas.Msg(
        message=__(key="organisation-created-successfully"),
    )

@router.put("/update-status",response_model=schemas.Msg,status_code=200)
async def update_organisation_status(
        *,
        db: Session = Depends(get_db),
        obj_in : schemas.OrganisationUpdateStatus,
        current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN","ADMIN"]))
):
    if obj_in.status not in ["active","inactive"]:
        raise HTTPException(status_code=400,detail=__(key="status-not-found"))

    crud.organisation.update_status(
        db=db,
        uuid=obj_in.uuid,
        status=obj_in.status
    )
    return schemas.Msg(message=__(key="organisation-status-updated-successfully"))


@router.get("/get_all_organisations", response_model=None,status_code=200)
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
    return crud.organisation.get_many(
        db,
        page,
        per_page,
        order,
        order_field,
        keyword,
        status,
    )


@router.get("/get_all_services_for_my_organisations", response_model=None,status_code=200)
async def get_all_services(
    *,
    db: Session = Depends(get_db),
    page: int = 1,
    per_page: int = 5,
    order: Optional[str] = None,
    order_field: Optional[str] = None,
    keyword: Optional[str] = None,
    status: Optional[str] = None,
    current_user: models.User = Depends(TokenRequired(roles=["OWNER"]))
):
    return crud.organisation.get_by_owner_uuid(
        db,
        page,
        per_page,
        order,
        order_field,
        keyword,
        status,
        owner_uuid=current_user.uuid,
    )


@router.put("/soft-delete",response_model=schemas.Msg)
async def soft_delete_licence(
        *,
        db: Session = Depends(get_db),
        obj_in:schemas.OrganisationDelete,
        current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN", "ADMIN"]))
):
    crud.organisation.soft_delete(
        db=db,
        uuid=obj_in.uuid
    )
    return {"message":__(key="organisation-deleted-successfully")}


@router.post("/validate_account", response_model=schemas.Msg, status_code=201)
async def validate_account(
    *,
    db: Session = Depends(get_db),
    obj_in: schemas.OrganisationValidateAccount
):
    organisation = crud.organisation.get_by_email(db=db, email=obj_in.email)
    if not organisation:
        raise HTTPException(status_code=404, detail=__(key="organisation-not-found"))

    if not organisation.validation_account_otp or not organisation.validation_otp_expirate_at:
        raise HTTPException(status_code=400, detail=__(key="the-validation-account-otp-expired"))

    if organisation.validation_account_otp != obj_in.code_otp:
        raise HTTPException(status_code=400, detail=__(key="the-validation-account-otp-invalid"))

    if datetime.utcnow() > organisation.validation_otp_expirate_at:
        raise HTTPException(status_code=400, detail=__(key="the-validation-account-otp-expired"))

    organisation.status = "active"
    organisation.validation_account_otp = None
    organisation.validation_otp_expirate_at = None
    db.commit()

    return schemas.Msg(message=__("organisation-validated-successfully"))


@router.post("/resend-otp",response_model=schemas.Msg)
def resend_otp(
    email: str,
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    user = db.query(models.User).filter(
        models.User.email == email,
        models.User.is_deleted == False
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail=__(key="user-not-found"))

    organisation = db.query(models.Organisation).filter(
        models.Organisation.owner_uuid == user.uuid,
        models.Organisation.status == models.OrganisationStatus.inactive
    ).first()

    if not organisation:
        raise HTTPException(status_code=404, detail=__(key="organisation-not-found"))

    # Nouveau code OTP
    code = generate_code(length=12)[:6]
    otp_expiration = datetime.utcnow() + timedelta(days=1)

    organisation.validation_account_otp = code
    organisation.validation_otp_expirate_at = otp_expiration
    db.commit()

    # Envoi mail OTP
    background_tasks.add_task(
        send_organisation_otp_to_user,
        email_to=user.email,
        otp=code,
        expirate_at=otp_expiration
    )

    return {"message": "Un nouveau code OTP a été envoyé à votre adresse e-mail."}