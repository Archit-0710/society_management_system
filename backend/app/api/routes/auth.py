from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, AuthMeResponse
from app.services.auth_service import register_user, authenticate_user, create_user_token

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new resident user."""
    try:
        user = register_user(db, request)
        token = create_user_token(user)
        return TokenResponse(access_token=token)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Login and receive JWT token."""
    user = authenticate_user(db, request)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    token = create_user_token(user)
    return TokenResponse(access_token=token)


@router.get("/me", response_model=AuthMeResponse)
def get_me(current_user = Depends(get_current_user)):
    """Get current authenticated user info."""
    return AuthMeResponse(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        phone=current_user.phone,
        flat_no=current_user.flat_no,
        role=current_user.role.value,
    )