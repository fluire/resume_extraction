from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ResumeUploadMetadata(BaseModel):
    filename: str = Field(..., description="Original filename of the uploaded PDF")
    content_type: str = Field(..., description="MIME type of the uploaded file")
    upload_time: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of upload")
    file_size: int = Field(..., description="Size of the file in bytes")
    uploader_id: Optional[str] = Field(None, description="ID of the user who uploaded the file") 