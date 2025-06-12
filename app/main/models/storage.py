from dataclasses import dataclass
from sqlalchemy.sql import func
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql.json import JSONB
from sqlalchemy import Column, ForeignKey, Integer, String, Text, DateTime
from sqlalchemy import event
from app.main.models.db.base_class import Base

@dataclass
class Storage(Base):
    """
    Storage Model for storing file-related details in the database.

    Attributes:
        uuid (str): Unique identifier for the storage entry.
        file_name (str): The name of the file.
        summary (str): A brief summary of the file.
        cloudinary_file_name (str): Cloudinary-specific file name.
        url (str): URL for accessing the file.
        mimetype (str): MIME type of the file.
        format (str): Format of the file (e.g., image, video).
        public_id (str): Public identifier used by Cloudinary or another storage provider.
        version (int): Version number of the file.
        width (int): Width of the file (if applicable).
        height (int): Height of the file (if applicable).
        size (int): Size of the file in bytes.
        thumbnail (JSONB): Thumbnail data in JSON format.
        medium (JSONB): Medium-sized image data in JSON format.
        date_added (datetime): Timestamp when the file was added to storage.
        date_modified (datetime): Timestamp when the file was last modified.
    """
    
    __tablename__ = "storages"

    uuid: str = Column(String, primary_key=True, unique=True)  # Unique identifier for the storage entry
    file_name: str = Column(Text, default="", nullable=True)  # Name of the file
    summary: Text = Column(Text, default="", nullable=True)  # File summary
    cloudinary_file_name: str = Column(Text, default="", nullable=True)  # Cloudinary-specific file name
    url: str = Column(Text, default="", nullable=True)  # URL for accessing the file
    mimetype: str = Column(Text, default="", nullable=True)  # MIME type of the file
    format: str = Column(Text, default="", nullable=True)  # Format of the file
    public_id: str = Column(Text, default="", nullable=True)  # Public identifier for storage services
    version: int = Column(Integer, nullable=True)  # Version of the file
    width: int = Column(Integer, default=0, nullable=True)  # Width of the file (if applicable)
    height: int = Column(Integer, default=0, nullable=True)  # Height of the file (if applicable)
    size: int = Column(Integer, default=0, nullable=True)  # Size of the file in bytes
    thumbnail: any = Column(JSONB, default={}, nullable=True)  # Thumbnail in JSON format
    medium: any = Column(JSONB, default={}, nullable=True)  # Medium-sized image data in JSON format
    date_added: any = Column(DateTime, server_default=func.now())  # Timestamp when the file was added
    date_modified: any = Column(DateTime, server_default=func.now(), onupdate=func.now())  # Last modified timestamp
