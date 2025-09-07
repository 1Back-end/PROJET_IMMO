import os
from pydantic_settings import BaseSettings
from typing import ClassVar, Optional,Dict,Any
from pydantic import EmailStr, validator

# from pydantic import Base EmailStr,validator


def get_secret(secret_name, default):
    try:
        with open('/run/secrets/{0}'.format(secret_name), 'r') as secret_file:
            return secret_file.read().strip()
    except IOError:
        return os.getenv(secret_name, default)

class ConfigClass(BaseSettings):
    SECRET_KEY: str = get_secret("SECRET_KEY", 'H5zMm7XtCKNsab88JQCLkaY4d8hExSjghGyaJDy12M')
    ALGORITHM: str = get_secret("ALGORITHM", 'HS256')

    ADMIN_KEY: str = get_secret("ADMIN_KEY", "Key2025")
    ADMIN_USERNAME: str = get_secret("ADMIN_USERNAME", "admin_tools")
    ADMIN_PASSWORD: str = get_secret("ADMIN_PASSWORD", "XfT89KzLpQ")


    # 60 minutes * 24 hours * 355 days = 365 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(get_secret("ACCESS_TOKEN_EXPIRE_MINUTES", 30 * 24 * 365))
    REFRESH_TOKEN_EXPIRE_MINUTES: int = int(get_secret("REFRESH_TOKEN_EXPIRE_MINUTES", 60 * 24 * 365))

    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = get_secret("EMAIL_RESET_TOKEN_EXPIRE_HOURS", 8)

    # SQLALCHEMY_DATABASE_URL: str = get_secret("SQLALCHEMY_DATABASE_URL", 'postgresql://base_api_v2:Lcy96xP66EMBbrrr@dbe.comii.de:6020/sanctions_db_dev')
    SQLALCHEMY_DATABASE_URL: str = get_secret("SQLALCHEMY_DATABASE_URL", 'postgresql://postgres:2002@localhost:5432/generate_license_api')

    SQLALCHEMY_POOL_SIZE: int = 100
    SQLALCHEMY_MAX_OVERFLOW: int = 0
    SQLALCHEMY_POOL_TIMEOUT: int = 30
    SQLALCHEMY_POOL_RECYCLE: int = get_secret("SQLALCHEMY_POOL_RECYCLE", 3600)
    SQLALCHEMY_ENGINE_OPTIONS: dict = {
        "pool_pre_ping": True,
        "pool_recycle": SQLALCHEMY_POOL_RECYCLE,
    }

    CLOUDINARY_CLOUD_NAME:str = get_secret("CLOUDINARY_NAME","do8fpzhen")
    CLOUDINARY_API_KEY:str = get_secret("CLOUDINARY_API_KEY","839879112629286")
    CLOUDINARY_API_SECRET:str = get_secret("CLOUDINARY_API_SECRET","jSQC_LoynIqEqDd81fJY1gTATVI")
    CLOUDINARY_API_SECURE:bool = get_secret("CLOUDINARY_API_SECURE", True)
    IMAGE_MEDIUM_WIDTH: int = get_secret("IMAGE_MEDIUM_WIDTH", 600)
    IMAGE_THUMBNAIL_WIDTH: int = get_secret("IMAGE_THUMBNAIL_WIDTH", 300)
    UPLOADED_FILE_DEST: str = get_secret("UPLOADED_FILE_DEST", "uploads")


    MAILTRAP_USERNAME :str = get_secret("MAILTRAP_USERNAME", "987982cf606b48")
    MAILTRAP_PASSWORD :str = get_secret("MAILTRAP_PASSWORD", "c08cbffad8f6c7")
    MAILTRAP_HOST: ClassVar[str] = "smtp.mailtrap.io"
    MAILTRAP_PORT: ClassVar[int] = 587
    EMAILS_FROM_CLOUDINARY: str = get_secret("EMAILS_FROM_CLOUDINARY", "laurentalphonsewilfried@gmail.com")

    PREFERRED_LANGUAGE: str = get_secret("PREFERRED_LANGUAGE", 'fr')
    API_V1_STR: str = get_secret("API_V1_STR", "/api/v1")
    
    PROJECT_NAME: str = get_secret("PROJECT_NAME", "API GENERATE LICENCE SIAH CONSULTING")
    PROJECT_VERSION: str = get_secret("PROJECT_VERSION", "0.0.1")

    # Redis config
    REDIS_HOST: str = get_secret("REDIS_HOST", "localhost")  # redis_develop
    REDIS_PORT: int = get_secret("REDIS_PORT", 6379)
    REDIS_DB: int = get_secret("REDIS_DB", 2)
    REDIS_CHARSET: str = get_secret("REDIS_CHARSET", "UTF-8")
    REDIS_DECODE_RESPONSES: bool = get_secret("REDIS_DECODE_RESPONSES", True)

    SMTP_TLS: bool = get_secret("SMTP_TLS", True)
    SMTP_SSL: bool = get_secret("SMTP_SSL", False)
    SMTP_PORT: Optional[int] = int(get_secret("SMTP_PORT", 587))
    SMTP_HOST: Optional[str] = get_secret("SMTP_HOST", "smtp.gmail.com")
    SMTP_USER: Optional[str] = get_secret("SMTP_USER", "laurentalphonsewilfried@gmail.com")
    SMTP_PASSWORD: Optional[str] = get_secret("SMTP_PASSWORD", "viuessfzwqnwneil")
    EMAILS_FROM_EMAIL: Optional[EmailStr] = get_secret("EMAILS_FROM_EMAIL", "laurentalphonsewilfried@gmail.com")
    EMAILS_FROM_NAME: Optional[str] = get_secret("EMAILS_FROM_NAME", "SIAH CONSULTING")

    @validator("EMAILS_FROM_NAME")
    def get_project_name(cls, v: Optional[str], values: Dict[str, Any]) -> str:
        if not v:
            return values["PROJECT_NAME"]
        return v

    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = int(get_secret("EMAIL_RESET_TOKEN_EXPIRE_HOURS", 48))
    EMAILS_ENABLED: bool = get_secret("EMAILS_ENABLED", True) in ["True", True]
    EMAIL_TEMPLATES_DIR: str = "{}/app/main/templates/emails/render".format(os.getcwd())

    @validator("EMAILS_ENABLED", pre=True)
    def get_emails_enabled(cls, v: bool, values: Dict[str, Any]) -> bool:
        return bool(
            values.get("SMTP_HOST")
            and values.get("SMTP_PORT")
            and values.get("EMAILS_FROM_EMAIL")
        )

    LOCAL: bool = os.getenv("LOCAL", True)

    class Config:
        case_sensitive = True


Config = ConfigClass()
