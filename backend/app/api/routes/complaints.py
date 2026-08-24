from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query, Form, File, UploadFile
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, require_admin
from app.core.database import get_db
from app.models.user import User
from app.schemas.complaint import (
    ComplaintResponse,
    ComplaintDetailResponse,
    ComplaintListResponse,
    ComplaintStatusUpdate,
    ComplaintPriorityUpdate,
    ComplaintStatusHistoryResponse,
)
from app.services import complaint_service
from app.services.storage_service import storage_service

router = APIRouter(tags=["Complaints"])


@router.post("/complaints", response_model=ComplaintResponse, status_code=status.HTTP_201_CREATED)
async def create_complaint(
    category_id: int = Form(...),
    description: str = Form(...),
    photo: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new complaint (Residents).
    Accepts multipart/form-data.
    """
    # Validations
    if category_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="category_id must be greater than 0"
        )
    if len(description) < 10 or len(description) > 2000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="description must be between 10 and 2000 characters"
        )

    photo_url = None
    if photo is not None and photo.filename:
        # Read file data to check validation and upload
        file_data = await photo.read()
        
        # Upload using the storage service
        try:
            photo_url = storage_service.upload_image(
                file_data=file_data,
                file_name=photo.filename,
                content_type=photo.content_type or "image/jpeg"
            )
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Image upload failed: {str(e)}"
            )

    try:
        complaint = complaint_service.create_complaint(
            db=db,
            category_id=category_id,
            description=description,
            photo_url=photo_url,
            resident_id=current_user.id
        )
        
        return ComplaintResponse(
            id=complaint.id,
            resident_id=complaint.resident_id,
            category_id=complaint.category_id,
            description=complaint.description,
            photo_url=complaint.photo_url,
            status=complaint.status.value,
            priority=complaint.priority.value,
            created_at=complaint.created_at,
            updated_at=complaint.updated_at,
            resolved_at=complaint.resolved_at,
            category_name=complaint.category.name,
            resident_name=complaint.resident.name,
        )
    except ValueError as e:
        # If fallback local upload occurred, clean it up
        if photo_url:
            storage_service.delete_image(photo_url)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/complaints/my", response_model=ComplaintListResponse)
def get_my_complaints(
    status_filter: str | None = Query(None, alias="status"),
    category_id: int | None = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get resident's own complaints (paginated).
    """
    skip = (page - 1) * limit
    complaints, total = complaint_service.get_complaints(
        db=db,
        resident_id=current_user.id,
        category_id=category_id,
        status=status_filter,
        skip=skip,
        limit=limit
    )
    
    complaint_responses = [
        ComplaintResponse(
            id=c.id,
            resident_id=c.resident_id,
            category_id=c.category_id,
            description=c.description,
            photo_url=c.photo_url,
            status=c.status.value,
            priority=c.priority.value,
            created_at=c.created_at,
            updated_at=c.updated_at,
            resolved_at=c.resolved_at,
            category_name=c.category.name,
            resident_name=c.resident.name,
        )
        for c in complaints
    ]
    
    return ComplaintListResponse(
        complaints=complaint_responses,
        total=total,
        page=page,
        limit=limit,
    )


@router.get("/complaints/{complaint_id}", response_model=ComplaintDetailResponse)
def get_complaint_detail(
    complaint_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get complaint details with full status history. Owner or Admin only."""
    complaint = complaint_service.get_complaint_by_id(db, complaint_id)
    if not complaint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Complaint not found")
    
    # Check ownership
    if not complaint_service.check_complaint_ownership(complaint, current_user.id, current_user.role.value):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own complaints"
        )
    
    # Prepare response with history
    return ComplaintDetailResponse(
        id=complaint.id,
        resident_id=complaint.resident_id,
        category_id=complaint.category_id,
        description=complaint.description,
        photo_url=complaint.photo_url,
        status=complaint.status.value,
        priority=complaint.priority.value,
        created_at=complaint.created_at,
        updated_at=complaint.updated_at,
        resolved_at=complaint.resolved_at,
        category_name=complaint.category.name,
        resident_name=complaint.resident.name,
        status_history=[
            ComplaintStatusHistoryResponse(
                id=h.id,
                old_status=h.old_status.value if h.old_status else None,
                new_status=h.new_status.value,
                changed_by=h.changed_by,
                note=h.note,
                created_at=h.created_at,
            )
            for h in complaint.status_history
        ],
    )


@router.get("/complaints/{complaint_id}/history", response_model=list[ComplaintStatusHistoryResponse])
def get_complaint_history(
    complaint_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get only the history logs for a complaint. Owner or Admin only."""
    complaint = complaint_service.get_complaint_by_id(db, complaint_id)
    if not complaint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Complaint not found")
    
    # Check ownership
    if not complaint_service.check_complaint_ownership(complaint, current_user.id, current_user.role.value):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view status history for your own complaints"
        )
    
    return [
        ComplaintStatusHistoryResponse(
            id=h.id,
            old_status=h.old_status.value if h.old_status else None,
            new_status=h.new_status.value,
            changed_by=h.changed_by,
            note=h.note,
            created_at=h.created_at,
        )
        for h in complaint.status_history
    ]


@router.get("/admin/complaints", response_model=ComplaintListResponse)
def get_admin_complaints(
    status_filter: str | None = Query(None, alias="status"),
    category_id: int | None = Query(None),
    priority: str | None = Query(None),
    overdue: bool | None = Query(None),
    from_date: datetime | None = Query(None),
    to_date: datetime | None = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    Get all complaints for administrator dashboard.
    Supports filtering and default ordering (overdue first, then older complaints first).
    """
    skip = (page - 1) * limit
    complaints, total = complaint_service.get_admin_complaints(
        db=db,
        status=status_filter,
        category_id=category_id,
        priority=priority,
        overdue=overdue,
        from_date=from_date,
        to_date=to_date,
        skip=skip,
        limit=limit
    )
    
    complaint_responses = [
        ComplaintResponse(
            id=c.id,
            resident_id=c.resident_id,
            category_id=c.category_id,
            description=c.description,
            photo_url=c.photo_url,
            status=c.status.value,
            priority=c.priority.value,
            created_at=c.created_at,
            updated_at=c.updated_at,
            resolved_at=c.resolved_at,
            category_name=c.category.name,
            resident_name=c.resident.name,
        )
        for c in complaints
    ]
    
    return ComplaintListResponse(
        complaints=complaint_responses,
        total=total,
        page=page,
        limit=limit,
    )


@router.patch("/admin/complaints/{complaint_id}/status", response_model=ComplaintResponse)
def update_complaint_status(
    complaint_id: int,
    request: ComplaintStatusUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Update complaint status (admin only)."""
    try:
        complaint = complaint_service.update_complaint_status(db, complaint_id, request, admin.id)
        
        return ComplaintResponse(
            id=complaint.id,
            resident_id=complaint.resident_id,
            category_id=complaint.category_id,
            description=complaint.description,
            photo_url=complaint.photo_url,
            status=complaint.status.value,
            priority=complaint.priority.value,
            created_at=complaint.created_at,
            updated_at=complaint.updated_at,
            resolved_at=complaint.resolved_at,
            category_name=complaint.category.name,
            resident_name=complaint.resident.name,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.patch("/admin/complaints/{complaint_id}/priority", response_model=ComplaintResponse)
def update_complaint_priority(
    complaint_id: int,
    request: ComplaintPriorityUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Update complaint priority (admin only)."""
    try:
        complaint = complaint_service.update_complaint_priority(db, complaint_id, request, admin.id)
        
        return ComplaintResponse(
            id=complaint.id,
            resident_id=complaint.resident_id,
            category_id=complaint.category_id,
            description=complaint.description,
            photo_url=complaint.photo_url,
            status=complaint.status.value,
            priority=complaint.priority.value,
            created_at=complaint.created_at,
            updated_at=complaint.updated_at,
            resolved_at=complaint.resolved_at,
            category_name=complaint.category.name,
            resident_name=complaint.resident.name,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))