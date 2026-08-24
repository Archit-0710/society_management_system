from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, require_admin
from app.core.database import get_db
from app.models.user import User
from app.schemas.notice import NoticeResponse, NoticeCreate, NoticeUpdate
from app.services import notice_service

router = APIRouter(tags=["Notices"])


@router.get("/notices", response_model=list[NoticeResponse])
def get_notices(
    page: int = 1,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all notices (authenticated users). Important notices appear first."""
    skip = (page - 1) * limit
    notices = notice_service.get_notices(db, skip=skip, limit=limit)
    
    return [
        NoticeResponse(
            id=n.id,
            title=n.title,
            content=n.content,
            is_important=n.is_important,
            created_by=n.created_by,
            created_at=n.created_at,
            updated_at=n.updated_at,
            author_name=n.author.name,
        )
        for n in notices
    ]


@router.get("/notices/{notice_id}", response_model=NoticeResponse)
def get_notice_detail(
    notice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get notice details (authenticated users)."""
    notice = notice_service.get_notice_by_id(db, notice_id)
    if not notice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notice not found")
    
    return NoticeResponse(
        id=notice.id,
        title=notice.title,
        content=notice.content,
        is_important=notice.is_important,
        created_by=notice.created_by,
        created_at=notice.created_at,
        updated_at=notice.updated_at,
        author_name=notice.author.name,
    )


@router.post("/admin/notices", response_model=NoticeResponse, status_code=status.HTTP_201_CREATED)
def create_notice(
    request: NoticeCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Create a new notice (admin only)."""
    notice = notice_service.create_notice(db, request, admin.id)
    
    return NoticeResponse(
        id=notice.id,
        title=notice.title,
        content=notice.content,
        is_important=notice.is_important,
        created_by=notice.created_by,
        created_at=notice.created_at,
        updated_at=notice.updated_at,
        author_name=notice.author.name,
    )


@router.patch("/admin/notices/{notice_id}", response_model=NoticeResponse)
def update_notice(
    notice_id: int,
    request: NoticeUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Update a notice (admin only)."""
    try:
        notice = notice_service.update_notice(db, notice_id, request)
        
        return NoticeResponse(
            id=notice.id,
            title=notice.title,
            content=notice.content,
            is_important=notice.is_important,
            created_by=notice.created_by,
            created_at=notice.created_at,
            updated_at=notice.updated_at,
            author_name=notice.author.name,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/admin/notices/{notice_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_notice(
    notice_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Delete a notice (admin only)."""
    try:
        notice_service.delete_notice(db, notice_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))