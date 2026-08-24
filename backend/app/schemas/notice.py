from datetime import datetime
from pydantic import BaseModel, Field


class NoticeResponse(BaseModel):
    id: int
    title: str
    content: str
    is_important: bool
    created_by: int
    created_at: datetime
    updated_at: datetime
    
    # Include author name
    author_name: str | None = None

    class Config:
        from_attributes = True


class NoticeCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1, max_length=5000)
    is_important: bool = False


class NoticeUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=255)
    content: str | None = Field(None, min_length=1, max_length=5000)
    is_important: bool | None = None