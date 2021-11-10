from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class AttachmentBase (BaseModel):
    file_name: str = Field(alias="fileName")
    file_key: str = Field(alias="fileKey")
    file_url: str = Field(alias="fileUrl")
    file_size: str = Field(alias="fileSize")
    upload_date: datetime = Field(alias="uploadDate")
    source_system: Optional[str] = Field(alias="sourceSystem")
    data_id: Optional[str] = Field(alias="dataId")

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


class AttachmentCreate(AttachmentBase):
    pass


class AttachmentItem(AttachmentBase):
    id: int
