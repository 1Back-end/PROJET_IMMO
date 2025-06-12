import uuid
from datetime import timedelta, datetime
from typing import Any, Optional, List
from fastapi import APIRouter, Depends, Body, HTTPException, Query, File
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from starlette.requests import Request
from app.main.core.mail import send_reset_password_option2_email
from app.main.core.dependencies import get_db, TokenRequired
from app.main import schemas, crud, models
from app.main.core.i18n import __
from app.main.core.security import create_access_token, generate_code, get_password_hash,is_valid_password,verify_password
from app.main.core.config import Config
# from app.main.schemas.user import UserProfileResponse
# from app.main.utils.helper import check_pass, generate_randon_key

router = APIRouter(prefix="/authentification", tags=["authentification"])

@router.post("/login/administrator",  response_model=schemas.UserAuthentication)
async def login(
        obj_in:schemas.UserLogin,
        db: Session = Depends(get_db),
) -> Any:
    """
    Sign in with phone number and password
    """
    user = crud.user.authenticate(
        db, email=obj_in.email, password=obj_in.password
    )
    if not user:
        raise HTTPException(status_code=400, detail=__(key="auth-login-failed"))

    if user.status in [models.UserStatus.BLOCKED]:
        raise HTTPException(status_code=400, detail=__(key="auth-login-failed"))

    if user.status != models.UserStatus.ACTIVED:
        raise HTTPException(status_code=402, detail=__(key="user-not-activated"))
    
    access_token_expires = timedelta(minutes=Config.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    return {
        "user": user,
        "token": {
            "access_token": create_access_token(
                user.uuid, expires_delta=access_token_expires
            ),
            "token_type": "bearer",
        }
    }


@router.put("/change-password", response_model=schemas.UserAuthentication)
async def update_current_user_password(
    obj_in: schemas.UserChangePassword,
    db: Session = Depends(get_db),
    current_user: any = Depends(TokenRequired(let_new_user=True))
):
    current_user = crud.user.get_by_email(db=db, email=obj_in.email)
    if not current_user:
        raise HTTPException(status_code=404, detail=__("user-not-found"))
    # Vérifier l'ancien mot de passe
    if not verify_password(obj_in.current_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail=__("incorrect-current-password"))

    # Empêcher d'utiliser le même mot de passe
    if verify_password(obj_in.new_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail=__("different-password-required"))

    # Valider le nouveau mot de passe
    if not is_valid_password(obj_in.new_password):
        raise HTTPException(status_code=400, detail=__("invalid-password"))
    current_user.password_hash = get_password_hash(obj_in.new_password)

    # Marquer l'utilisateur comme non nouveau si applicable
    if current_user.is_new_user:
        current_user.is_new_user = False

    db.commit()
    db.refresh(current_user)
    access_token_expires = timedelta(minutes=Config.ACCESS_TOKEN_EXPIRE_MINUTES)

    return {
        "user": current_user,
        "token": {
            "access_token": create_access_token(
                current_user.uuid, expires_delta=access_token_expires
            ),
            "token_type": "bearer",
        }
    }



@router.get("/me/administrator", summary="Get current user", response_model=schemas.UserProfile)
def get_current_user(
        current_user: any = Depends(TokenRequired()),
):
    """
    Get current user
    """
    return current_user

@router.post("/start-reset-password/administrator", response_model=schemas.Msg)
def start_reset_password(
        obj_in:schemas.ResetPasswordOption2Step1,
        db: Session = Depends(get_db),

) -> schemas.Msg:
    """
    Start reset password with phone number
    """
    user = crud.user.get_by_email(db=db,email=obj_in.email)
    if not user:
        raise HTTPException(status_code=404, detail=__(key="user-not-found"))

    code = generate_code(length=12)
    code= str(code[0:5]) 
    print(f"Administrator Code Otp",code)
    user.otp_password = code
    user.otp_password_expired_at = datetime.now() + timedelta(hours=24)
    db.commit()
    db.refresh(user)
    full_name = f"{user.first_name} {user.last_name}"
    send_reset_password_option2_email(email_to=obj_in.email,otp=code,name=full_name)
    

    return schemas.Msg(message=__(key="reset-password-started"))

@router.post("/check-otp-password/administrator", summary="Check OTP password", response_model=schemas.Msg)
def check_otp_password(
        obj_in:schemas.ResetPasswordOption2Step2,
        db: Session = Depends(get_db),
) -> schemas.Msg:
    """
    Check OTP password
    """
    user = crud.user.get_by_email(db=db, email=obj_in.email)
    if not user:
        raise HTTPException(status_code=404, detail=__(key="user-not-found"))

    if user.otp_password != obj_in.otp:
        raise HTTPException(status_code=400, detail=__(key="otp-invalid"))
    
    if user.otp_password_expired_at < datetime.now():
        raise HTTPException(status_code=400, detail=__(key="otp-expired"))

    return schemas.Msg(message=__(key="otp-valid"))

@router.post("/reset-password/administrator", summary="Reset password", response_model=schemas.Msg)
def reset_password(
        obj_in:schemas.ResetPasswordOption3Step3,
        db: Session = Depends(get_db),
) -> schemas.Msg:
    """
    Reset password
    """
    user = crud.user.get_by_email(db=db, email=obj_in.email)
    if not user:
        raise HTTPException(status_code=404, detail=__("user-not-found"))

    if user.otp_password != obj_in.otp:
        raise HTTPException(status_code=400, detail=__("otp-invalid"))

    if user.otp_password_expired_at < datetime.now():
        raise HTTPException(status_code=400, detail=__("otp-expired"))
    
    if not is_valid_password(password=obj_in.new_password):
        raise HTTPException(
            status_code=400,
            detail=__("invalid-password")
        )
    user.password_hash = get_password_hash(password=obj_in.new_password)
    user.otp_password = None
    user.otp_password_expired_at = None
    db.commit()
    db.refresh(user)

    return schemas.Msg(message=__(key="password-reset-successfully"))



@router.delete("/logout",response_model= schemas.Msg,status_code= 200)
def logout(
    *,
    db: Session = Depends(get_db),
    request: Request,
    current_user: Any = Depends(TokenRequired(roles=[])),
) -> Any:
    """
        Logout admininstrator session
    """
    user_token = (request.headers["authorization"]).split("Bearer")[1].strip()
    db.add(models.BlacklistToken(token=user_token, uuid=str(uuid.uuid4())))
    db.commit()

    return {"message": __("Ok")}