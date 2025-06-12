

from pydantic import BaseModel, Field, ConfigDict
from typing import Any, Optional, Text

from app.main.schemas.base import DataList

class FileUpload(BaseModel):
    file_name: Optional[str] = None
    base_64: Optional[Any] = None

class FileResize(BaseModel):
    file_name: Optional[str] = None
    url: Optional[str] = None

class FileAdd(BaseModel):
    base_64: Any

class FileSlim(BaseModel):
    uuid:str
    file_name: str
    url: str
    format: Optional[str]
    model_config = ConfigDict(from_attributes=True)



class File(BaseModel):
    uuid:str
    file_name: str
    cloudinary_file_name:str
    url: str
    format: Optional[str]
    mimetype: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    size: Optional[int] = None
    thumbnail: Optional[FileResize] = None
    medium: Optional[FileResize] = None


    model_config = ConfigDict(from_attributes=True)


class StorageCreate(BaseModel):
    uuid:str
    file_name: str = Field(..., description="Le nom du fichier")
    cloudinary_file_name: Optional[str] = Field(None, description="Le nom du fichier sur Cloudinary")
    url: str = Field(..., description="L'URL sécurisée du fichier")
    mimetype: Optional[str] = Field(None, description="Le type MIME du fichier")
    format: Optional[str] = Field(None, description="Le format du fichier")
    public_id: Optional[str] = Field(None, description="L'identifiant public du fichier")
    version: Optional[int] = Field(None, description="La version du fichier")
    width: Optional[int] = Field(None, description="La largeur du fichier")
    height: Optional[int] = Field(None, description="La hauteur du fichier")
    size: Optional[int] = Field(None, description="La taille du fichier en octets")

    model_config = ConfigDict(from_attributes=True)

class FileSlim(BaseModel):
    uuid: str
    public_id: str
    file_name: str
    summary:Optional[Text]
    width:int
    height:int
    size:int
    cloudinary_file_name: str
    url: str
    format: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class FileSlim1(BaseModel):
    file_name: str
    width:int
    height:int
    size:int
    url: str
    format: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class FileSlim2(BaseModel):
    file_name: str
    format: Optional[str] = None
    url: str
    model_config = ConfigDict(from_attributes=True)

class FileList(DataList):
    data: list[FileSlim] = []

class OpenAIUploadFile(BaseModel):
    filename: str
    bytes:int
    mimetype: Optional[str] = None
    purpose:str ="assistants"

