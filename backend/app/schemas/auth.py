from pydantic import BaseModel, EmailStr, Field, field_validator


class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=72)
    phone: str | None = Field(None, max_length=20)
    flat_no: str = Field(..., min_length=1, max_length=20)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., max_length=72)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class AuthMeResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: str | None
    flat_no: str | None
    role: str

    class Config:
        from_attributes = True