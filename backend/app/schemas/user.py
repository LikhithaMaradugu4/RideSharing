from pydantic import BaseModel, EmailStr
from typing import Optional

class CreateUserRequest(BaseModel):
    full_name: str
    email: EmailStr
    phone: Optional[str]
    role: str
    country_code: str
    city_id: Optional[int]

class UserResponse(BaseModel):
    user_id: int
    full_name: str
    email: Optional[str]
    phone: Optional[str]
    role: str
    status: str

    class Config:
        orm_mode = True


class ProfileResponse(BaseModel):
    user_id: int
    full_name: str
    phone: str
    gender: Optional[str]
    city_id: Optional[int]
    country_code: str

    class Config:
        from_attributes = True


class ProfileUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    gender: Optional[str] = None
    city_id: Optional[int] = None





















