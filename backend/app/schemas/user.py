import re
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional


def validate_e164_phone(phone: Optional[str]) -> Optional[str]:
    """
    Validate and normalize phone number to E.164 format.
    
    E.164 format: +[country code][subscriber number]
    - Starts with +
    - 7-15 digits total (after +)
    - Example: +14155551234, +919876543210
    """
    if phone is None:
        return None
    
    # Remove any whitespace
    phone = phone.strip()
    
    # If empty after strip, return None
    if not phone:
        return None
    
    # Normalize: ensure starts with +
    if not phone.startswith('+'):
        phone = '+' + phone
    
    # Validate E.164 format
    pattern = r'^\+[1-9][0-9]{6,14}$'
    if not re.match(pattern, phone):
        raise ValueError(
            f"Phone number must be in E.164 format (e.g., +14155551234). "
            f"Got: {phone}"
        )
    
    return phone


class CreateUserRequest(BaseModel):
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    role: str
    country_code: str
    city_id: Optional[int] = None
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        return validate_e164_phone(v)

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





















