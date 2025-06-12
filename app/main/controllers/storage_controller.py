from datetime import date, datetime
import os
from typing import Optional
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.orm import Session
from app.main.core.config import Config
from app.main.schemas.file import StorageCreate,FileSlim,FileList
from app.main.crud.storage_crud import store_file,get_file_by_public_id,get_file_by_uuid,get_files
from app.main.schemas.msg import Msg
from app.main.utils.file import file_utils
import uuid
from app.main.utils.uploads import download_and_save_file, get_access_control, get_file_url, update_access_control, upload_to_cloudinary
from app.main.core.dependencies import get_db, TokenRequired
from app.main import models
MAX_TOKENS = 4096

router = APIRouter(prefix="/storages", tags=["storages"])

@router.post("/upload",response_model = FileSlim, status_code=200)
async def upload_file(
        *,
        db: Session = Depends(get_db),
        file: UploadFile = File(...),
        
):
    """
    Upload a file.
    """
    try:
        # Save the file temporarily
        temp_file_path = file_utils.save_temp_file(file)
        
        # Upload to Cloudinary
        public_id = str(uuid.uuid4())
        upload_result = upload_to_cloudinary(temp_file_path, public_id)

        # Delete the temporary file
        file_utils.delete_temp_file(temp_file_path)

        # Prepare file data for database
        file_data = StorageCreate(
            uuid = str(uuid.uuid4()),
            file_name=file.filename,
            cloudinary_file_name=upload_result.get("original_filename"),
            url=upload_result.get("secure_url"),
            mimetype=f"{upload_result.get('resource_type')}/{upload_result.get('format')}",
            format=upload_result.get("format"),
            public_id=upload_result.get("public_id"),
            version=upload_result.get("version"),
            width=upload_result.get("width"),
            height=upload_result.get("height"),
            size=upload_result.get("bytes"),
        )

        # Store file data in the database
        stored_file = store_file(db, file_data)

        return stored_file
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.get("/get/{public_id}",response_model = FileSlim, status_code=200)
def get_file(
    *,
    public_id: str, 
    db: Session = Depends(get_db),
    # current_user: models.User = Depends(dependencies.TokenRequired())

    ):
    """
    Get file from Cloudinary
    """
    # Retrieve file metadata from the database
    file_record = get_file_by_public_id(db=db, public_id=public_id)
    if not file_record:
        raise HTTPException(
            status_code=404,
            detail="File not found"
        )
        
    url = get_file_url(public_id = file_record.public_id)
    if not url:  # If the file doesn't exist in Cloudinary
        raise HTTPException(
            status_code=404,
            detail="File not found"
        )
    # Generate the secure URL for the file
    return  file_record



@router.get("/{public_id}/get", status_code=200)
def get_file(
    *,
    public_id: str, 
    db: Session = Depends(get_db),

    ):
    """
    Get file from Cloudinary
    """
    # Retrieve file metadata from the database
    file_record = get_file_by_public_id(db, public_id)
    if not file_record:
        raise HTTPException(
            status_code=404,
            detail="File not found"
        )
    # Generate the secure URL for the file
    url = get_file_url(file_record.public_id)
    if not url:  # If the file doesn't exist in Cloudinary
        raise HTTPException(
            status_code=404,
            detail="File not found"
        )

    return RedirectResponse(url = url)
    
        
@router.get("/documents",response_model = FileList, status_code=200)
def get_files_from_db(
    public_id: Optional[str] = None,
    keyword: Optional[str] = None,
    page: int = 1,
    per_page: int = 30,
    order:str = "desc",
    order_filed:str = "date_added",
    # date_added: Optional[date] = None,  # to filter by date_added in the range (start_date, end_date)
    document_type:Optional[str]=None,
    db: Session = Depends(get_db),
    
    ):

    """
    Get files with pagination by passing filters
    """
    
    return get_files(
        public_id=public_id,
        keyword=keyword,
        page=page,
        per_page=per_page,
        order=order,
        order_filed=order_filed,
        document_type=document_type,
        db = db,
        
    )
# @router.get("/resume/chat-gpt/{file_public_uuid}",response_model = None, status_code=200)
# async def resume_file_using_chatgpt(
#     *,
#     file_public_id:str,
#     message:str =__("resume-file"),
#     language:str,
#     current_user: models.User = Depends(dependencies.TokenRequired()),
#     db: Session = Depends(dependencies.get_db)
#     ):

#     """
#     Resume document 
#     """
#     # Retrieve file metadata from the database
#     file_record = storage.get_file_by_public_id(db, file_public_id)
    
#     if not file_record:
#         raise HTTPException(
#             status_code=404,
#             detail="File not found"
#         )
    
#     file_secure_url = get_file_url(public_id=file_record.public_id)
#     print('File-secure-url: %s' % file_secure_url)
#     if not file_secure_url:
#         raise HTTPException(
#             status_code=400,
#             detail="Failed to generate file URL"
#         )
#     print("file-secure-url: " + file_secure_url)

    
#     file = download_and_save_file(file_record.url)

#     # Sauvegarder le fichier en utilisant save_temp_file
#     file_path = file_utils.save_temp_file(file)

#     # Step 1: Upload the file to chatgpt server
#     uploaded_file = await open_ai_utils.upload_with_chatgpt(file_path)
#     print("uploaded_file1234",uploaded_file)

#     file_id = uploaded_file.id
#     combined_prompt =f"{message}:{file_id}.",

#     # Resume document using OpenAI
#     response_text = await open_ai_utils.summarize_with_chatgpt(
#         language = language,
#         message = combined_prompt,
#         max_tokens = MAX_TOKENS - 500
#     )

#     file_utils.delete_temp_file(file_path)
#     file_record.summary = response_text
    
#     return response_text

# @router.get("/resume/{file_public_uuid}",response_model = None, status_code=200)
# async def resume_file_using_hugging_face(
#     *,
#     file_public_id:str,
#     # current_user: models.User = Depends(TokenRequired()),
#     db: Session = Depends(get_db)
#     ):

#     """
#     Resume document 
#     """
#     # Retrieve file metadata from the database
#     file_record = get_file_by_public_id(db, file_public_id)

    
#     if not file_record:
#         raise HTTPException(
#             status_code=404,
#             detail="File not found"
#         )
    
#     # if file_record.summary:
#     #     return file_record.summary
    
#     file_secure_url = get_file_url(public_id=file_record.public_id)
#     print('File-secure-url: %s' % file_secure_url)
#     if not file_secure_url:
#         raise HTTPException(
#             status_code=400,
#             detail="Failed to generate file URL"
#         )
#     print("file-secure-url: " + file_secure_url)

    
#     file = download_and_save_file(file_record.url)

#     # Sauvegarder le fichier en utilisant save_temp_file
#     file_path = file_utils.save_temp_file(file)

#     extracted_text = file_utils.extract_text_from_file(file_path)
#     # print("len12",len(extracted_text))
#     # summarized_text = await huggin_face_utils.summarize_with_hugging_face(
#     #     document_text=extracted_text,
#     #     min_lenght= 30,
#     #     max_length=500
#     # )
#     print(extracted_text)
#     summarized_text = summarize(file.filename, extracted_text, count=100)
    
#     file_utils.delete_temp_file(file_path)
#     file_utils.delete_file(file)
#     file_record.summary = summarized_text
#     db.commit()
    
#     return ' '.join(summarized_text)

@router.delete("",response_model = Msg, status_code=200)
async def delete(
    *,
    file_public_id:str,
    db: Session = Depends(get_db),
    # current_user: models.User = Depends(dependencies.TokenRequired(roles =["administrator"]))
    current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN","ADMIN"]))

    ):

    """
    delete document
    """
    # Retrieve file metadata from the database
    file_record = get_file_by_public_id(db, file_public_id)
    db.delete(file_record)
    db.commit()
    return {"message": __("document-deleted-successfully")}
    
    

    
