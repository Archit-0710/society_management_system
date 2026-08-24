from datetime import datetime
from pydantic import BaseModel, Field


class ComplaintStatusHistoryResponse(BaseModel):
    id: int
    old_status: str | None
    new_status: str
    changed_by: int
    note: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class ComplaintResponse(BaseModel):
    id: int
    resident_id: int
    category_id: int
    description: str
    photo_url: str | None
    status: str
    priority: str
    created_at: datetime
    updated_at: datetime
    resolved_at: datetime | None
    
    # Include related data
    category_name: str | None = None
    resident_name: str | None = None

    class Config:
        from_attributes = True


class ComplaintDetailResponse(ComplaintResponse):
    """Extended complaint response with full history."""
    status_history: list[ComplaintStatusHistoryResponse] = []

    class Config:
        from_attributes = True


class ComplaintCreate(BaseModel):
    category_id: int = Field(..., gt=0)
    description: str = Field(..., min_length=10, max_length=2000)
    photo_url: str | None = Field(None, max_length=500)


class ComplaintStatusUpdate(BaseModel):
    """Update complaint status (admin only)."""
    status: str = Field(..., pattern="^(OPEN|IN_PROGRESS|RESOLVED)$")
    note: str | None = Field(None, max_length=500)


class ComplaintPriorityUpdate(BaseModel):
    """Update complaint priority (admin only)."""
    priority: str = Field(..., pattern="^(LOW|MEDIUM|HIGH)$")


class ComplaintListResponse(BaseModel):
    """Paginated complaint list response."""
    complaints: list[ComplaintResponse]
    total: int
    page: int
    limit: int