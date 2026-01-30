"""
Authentication Schemas (Pydantic)
追溯: REQ-012, REQ-013
"""
from pydantic import BaseModel, EmailStr, Field


class UserRegisterRequest(BaseModel):
    """用戶註冊請求"""
    email: EmailStr
    password: str = Field(..., min_length=8)
    username: str = Field(..., min_length=2, max_length=100)


class UserLoginRequest(BaseModel):
    """用戶登入請求"""
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    """認證回應"""
    user_id: str
    email: str
    username: str
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """用戶資訊回應"""
    user_id: str
    email: str
    username: str
    role: str
    created_at: str
    
    class Config:
        from_attributes = True
