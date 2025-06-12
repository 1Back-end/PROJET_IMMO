import os
import uuid
from fastapi import UploadFile, HTTPException
from docx import Document
import PyPDF2
from app.main.core.config import Config
from mimetypes import MimeTypes
from app.main.core.i18n import __


class FileUtils:
    def __init__(self, allowed_mime_types=None):
        """
        Initialize the FileUtils with allowed MIME types.
        If no allowed MIME types are provided, use a default list.
        """
        
        self.allowed_mime_types = allowed_mime_types or [
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'image/jpeg',
            'image/png',
            'image/gif',
            'image/bmp',
            'image/tiff'
        ]

    def save_temp_file(self, file: UploadFile) -> str:
        """Save the uploaded file temporarily and return the path."""
        # Check MIME type
        mime = MimeTypes()
        print("file: " + file.filename[-1])
        mime_type = mime.guess_type(file.filename)[0]

        print("mime_type: ",mime_type)
        if mime_type not in self.allowed_mime_types:
            raise HTTPException(status_code=400, detail="Invalid file type")

        file_name = f"{uuid.uuid4()}-{file.filename.replace(' ', '-')}"
        file_path = os.path.join(Config.UPLOADED_FILE_DEST, file_name)
        with open(file_path, 'wb') as f:
            f.write(file.file.read())
        return file_path
    
    def extract_text_from_file(self,file_path):
        """
        Extract text from a file. Supports .docx and .pdf formats.
        
        Args:
            file_path (str): The path to the file.
        
        Returns:
            str: The extracted text from the file.
        
        Raises:
            ValueError: If the file format is unsupported.
            Exception: If text extraction fails.
        """
        file_extension = os.path.splitext(file_path)[1].lower()
        print("file_extension",file_extension)
        
        if file_extension == ".docx":
            try:
                doc = Document(file_path)
                text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            except Exception as e:
                raise Exception(f"Failed to extract text from DOCX file: {e}")
        
        elif file_extension == ".pdf":
            try:
                text = ""
                with open(file_path, 'rb') as pdf_file:
                    pdf_reader = PyPDF2.PdfReader(pdf_file)
                    for page in pdf_reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text
            except Exception as e:
                raise HTTPException(status_code= 400, detail =__("this file is crypted, please upload an uncrypted file"))
        
        else:
            raise ValueError("Unsupported file format")
        
        return text or ""

    def delete_temp_file(self, file_path: str):
        """Delete the temporary file."""
        if os.path.exists(file_path):
            os.remove(file_path)
    
    def delete_file(self,upload_file: UploadFile):
        try:
            os.remove(upload_file.file.name)
            print(f"Deleted file: {upload_file.file.name}")
        except Exception as e:
            print(f"Failed to delete file: {e}")


file_utils = FileUtils()