# app/schemas/user.py
from pydantic import BaseModel, Field
from typing import Optional

# --- User Schemas ---
class UserBase(BaseModel):
    username: str = Field(..., min_length=1, description="用户名")

class UserCreate(UserBase):
    password: str=Field(..., min_length=6)
    is_superuser: bool = False

class UserUpdate(BaseModel):
    password: Optional[str] = Field(None, min_length=6)
    is_superuser: Optional[bool] = None

class User(UserBase):
    id: int
    is_superuser: bool

    class Config:
        orm_mode = True

# --- Token Schemas (用于登录认证) ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    sub: str | None = None