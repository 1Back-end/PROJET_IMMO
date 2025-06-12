from datetime import date
import math
from typing import Any, Dict, Optional, Union
from sqlalchemy import or_
from sqlalchemy.orm import Session
# from app.main.crud.base import CRUDBase
from app.main.models.storage import Storage
import uuid
from app.main.schemas.file import FileAdd, File
from app.main.utils.file import FileUtils
# from app.main import crud
# from app.main.utils.qrcode import CreateQrcode
from app.main.models.storage import Storage
from app.main.schemas.file import FileList, StorageCreate



def store_file(db: Session, file_data: StorageCreate) -> Storage:
        """Store file metadata in the database."""
        db_file = Storage(**file_data.dict())
        db.add(db_file)
        db.commit()
        db.refresh(db_file)
        return db_file

def get_file_by_public_id(db: Session, public_id: str) -> Storage:
        """Retrieve file metadata by public_id."""
        return db.query(Storage).filter(Storage.public_id == public_id).first()
    
def get_file_by_uuid(db: Session, file_uuid: str) -> Storage:
        """Retrieve file metadata by file_uuid."""
        return db.query(Storage).filter(Storage.uuid == file_uuid).first()

def get_files(
            db: Session,
            public_id: Optional[uuid.UUID] = None,
            keyword: Optional[str] = None,
            page: int = 1,
            per_page: int = 30,
            order:str = "desc",
            order_filed:str = "date_added",
            # date_added: Optional[date] = None,  # to filter by date_added in the range (start_date, end_date)
            document_type:Optional[str]=None
    )->list[Storage]:
        
        """Retrieve all file metadata."""
        
        query = db.query(Storage)
        
        if public_id:
            query = query.filter(Storage.public_id == public_id)
        
        if document_type:
            query = query.filter(Storage.format.ilike('%' + str(document_type) + '%') )
        
        if keyword:
            query = query.filter(
                or_(
                    Storage.format.ilike('%' + str(keyword) + '%'),
                    Storage.file_name.ilike('%' + str(keyword) + '%'),
                    Storage.cloudinary_file_name.ilike('%' + str(keyword) + '%'),
                    Storage.public_id.ilike('%' + str(keyword) + '%'),
                )
            )

        query = query.order_by(Storage.date_added.desc()) if order == "desc" else query.order_by(Storage.date_added.asc())
        
        total = query.count()
        query = query.offset((page - 1) * per_page).limit(per_page)

        return FileList(
            total=total,
            pages=math.ceil(total/per_page),
            per_page=per_page,
            current_page=page,
            data=query,
        )


