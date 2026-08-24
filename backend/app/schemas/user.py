from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    name: str
    email: EmailStr
    phone: str | None = None
    flat_no: str | None = None


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: str | None
    flat_no: str | None
    role: str

    class Config:
        from_attributes = True