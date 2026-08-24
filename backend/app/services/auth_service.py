from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password, create_access_token
from app.models.user import User, UserRole
from app.schemas.auth import RegisterRequest, LoginRequest


def register_user(db: Session, request: RegisterRequest) -> User:
    """Register a new resident user."""
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise ValueError("Email already registered")
    
    # Create new user (always RESIDENT for public registration)
    hashed_pw = hash_password(request.password)
    new_user = User(
        name=request.name,
        email=request.email,
        password_hash=hashed_pw,
        phone=request.phone,
        flat_no=request.flat_no,
        role=UserRole.RESIDENT,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def authenticate_user(db: Session, request: LoginRequest) -> User | None:
    """Authenticate user and return User if valid, None otherwise."""
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        return None
    if not verify_password(request.password, user.password_hash):
        return None
    return user


def create_user_token(user: User) -> str:
    """Create JWT token for authenticated user."""
    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role.value,
    }
    return create_access_token(token_data)