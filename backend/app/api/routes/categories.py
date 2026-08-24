from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, require_admin
from app.core.database import get_db
from app.schemas.category import CategoryResponse, CategoryCreate, CategoryUpdate
from app.services import category_service

router = APIRouter(tags=["Categories"])


@router.get("/categories", response_model=list[CategoryResponse])
def get_categories(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """Get all active categories (authenticated users)."""
    categories = category_service.get_active_categories(db)
    return categories


@router.post("/admin/categories", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    request: CategoryCreate,
    db: Session = Depends(get_db),
    admin = Depends(require_admin)
):
    """Create a new category (admin only)."""
    try:
        category = category_service.create_category(db, request)
        return category
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.patch("/admin/categories/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    request: CategoryUpdate,
    db: Session = Depends(get_db),
    admin = Depends(require_admin)
):
    """Update a category and/or changes its active state (admin only)."""
    try:
        category = category_service.update_category(db, category_id, request)
        return category
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))