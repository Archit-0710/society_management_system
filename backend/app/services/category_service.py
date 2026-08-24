from sqlalchemy.orm import Session

from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate


def get_active_categories(db: Session) -> list[Category]:
    """Get all active categories."""
    return db.query(Category).filter(Category.is_active == True).all()


def get_all_categories(db: Session) -> list[Category]:
    """Get all categories (admin only)."""
    return db.query(Category).all()


def get_category_by_id(db: Session, category_id: int) -> Category | None:
    """Get category by ID."""
    return db.query(Category).filter(Category.id == category_id).first()


def create_category(db: Session, request: CategoryCreate) -> Category:
    """Create a new category."""
    # Check for duplicate name
    existing = db.query(Category).filter(Category.name == request.name).first()
    if existing:
        raise ValueError("Category with this name already exists")
    
    category = Category(
        name=request.name,
        description=request.description,
        is_active=True,
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def update_category(db: Session, category_id: int, request: CategoryUpdate) -> Category:
    """Update a category."""
    category = get_category_by_id(db, category_id)
    if not category:
        raise ValueError("Category not found")
    
    # Check for duplicate name if name is being changed
    if request.name and request.name != category.name:
        existing = db.query(Category).filter(Category.name == request.name).first()
        if existing:
            raise ValueError("Category with this name already exists")
    
    # Update fields
    if request.name is not None:
        category.name = request.name
    if request.description is not None:
        category.description = request.description
    if request.is_active is not None:
        category.is_active = request.is_active
    
    db.commit()
    db.refresh(category)
    return category