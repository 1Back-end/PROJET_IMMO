from datetime import datetime
from pydantic import BaseModel,EmailStr,ConfigDict
from typing import Optional
from app.main.models.user import UserRole
from app.main.schemas.file import FileSlim2
 
class AddedBy(BaseModel):
    uuid: str
    email: EmailStr
    first_name:str
    last_name:str
    phone_number:Optional[str]=None
    role:UserRole

    model_config = ConfigDict(from_attributes=True)


class AddedBySlim(BaseModel):
    first_name:str
    last_name:str
    role :str
    phone_number:Optional[str]=None
    model_config = ConfigDict(from_attributes=True)

class UserBase(BaseModel):
    email:EmailStr
    phone_number:str
    first_name:str
    last_name:str
    role:str
    login:Optional[str]=None
    avatar_uuid:Optional[str]=None
    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    uuid:str
    email:Optional[EmailStr]=None
    phone_number:Optional[str]=None
    first_name:Optional[str]=None
    last_name:Optional[str]=None
    role:Optional[str]=None
    login:Optional[str]=None
    avatar_uuid:Optional[str]=None
    model_config = ConfigDict(from_attributes=True)

class UserResponseInfo(BaseModel):
    uuid:str
    email:EmailStr
    phone_number:str
    first_name:str
    last_name:str
    role:str
    login:Optional[str]=None
    is_new_user :Optional[bool]=None
    avatar:Optional[FileSlim2]=None
    model_config = ConfigDict(from_attributes=True)


class UserCreate(UserBase):
    pass


class UserDelete(BaseModel):
    uuid:str
    

class UserResponse(UserBase):
    uuid:str

class Token(BaseModel):
    access_token: Optional[str] = None
    token_type: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class UserAuthentication(BaseModel):
    user: UserResponseInfo
    token: Optional[Token] = None
    model_config = ConfigDict(from_attributes=True)

class User(BaseModel):
    uuid:str
    email:EmailStr
    phone_number:str
    first_name:str
    last_name:str
    login:Optional[str]=None
    created_at: datetime
    updated_at: datetime
    avatar:Optional[FileSlim2]=None
    status : str
    role :str
    model_config = ConfigDict(from_attributes=True)



class UserDetail(User):
    uuid: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserProfile(BaseModel):
    email:EmailStr
    phone_number:str
    first_name:str
    last_name:str
    role:UserRole
    login:Optional[str]=None
    avatar:Optional[FileSlim2]=None

class ResetPasswordOption2Step1(BaseModel):
    email: EmailStr

class ResetPasswordOption2Step2(BaseModel):
    email: str
    otp: str

class ResetPasswordOption3Step3(BaseModel):
    email: str
    otp: str
    new_password:str
class UpdateStatus(BaseModel):
    uuid: str
    status: str


class UserChangePassword(BaseModel):
    email:str
    current_password:str
    new_password: str

class UserResponseList(BaseModel):
    total: int
    pages: int
    per_page: int
    current_page:int
    data: list[User]

    model_config = ConfigDict(from_attributes=True)