# app/schemas/platform.py
from pydantic import BaseModel
from typing import Optional
from pydantic import Field

# 在 platforms.py 的顶部
from app.schemas import platform as platform_schema

# 基础模型，包含所有平台共有的字段
class PlatformBase(BaseModel):
    name: str = Field(..., min_length=1, description="平台名称")
    description: Optional[str] = None

# 创建平台时使用的模型 (继承自 Base)
class PlatformCreate(PlatformBase):
    pass

# 更新平台时使用的模型 (所有字段都是可选的)
class PlatformUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1)
    description: Optional[str] = None

# 从数据库读取平台数据时使用的模型 (包含 id)
class Platform(PlatformBase):
    id: int

    class Config:
        from_attributes = True # Pydantic V2 中 orm_mode 的新名称