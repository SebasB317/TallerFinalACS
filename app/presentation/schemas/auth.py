from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class RegisterRequest(BaseModel):
    """Esquema para registro de usuario"""
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None

class LoginRequest(BaseModel):
    """Esquema para login"""
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    """Esquema para respuesta con token"""
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: str

class UserResponse(BaseModel):
    """Esquema para respuesta de usuario"""
    id: str
    email: str
    full_name: Optional[str] = None
    is_active: bool
    
    class Config:
        from_attributes = True
