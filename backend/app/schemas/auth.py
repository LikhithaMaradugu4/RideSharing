from pydantic import BaseModel, EmailStr

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserInfo(BaseModel):
    user_id: int
    full_name: str
    role: str
    status: str

class LoginResponse(BaseModel):
    session_id: str
    user: UserInfo
