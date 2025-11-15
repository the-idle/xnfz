# app/schemas/user.py
from pydantic import BaseModel

# --- User Schemas ---
class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

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