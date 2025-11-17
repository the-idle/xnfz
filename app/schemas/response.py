# app/schemas/response.py
from pydantic import BaseModel, Field
from typing import Generic, TypeVar, Optional, List

# 定义一个泛型类型变量，用于表示 data 字段的具体类型
DataType = TypeVar('DataType')

class UnifiedResponse(BaseModel, Generic[DataType]):
    """
    统一的 API 响应模型
    """
    code: int = Field(200, description="业务状态码, 200 表示成功")
    msg: str = Field("success", description="响应消息")
    data: Optional[DataType] = None # 实际的响应数据，可以是任何类型

    class Config:
        from_attributes = True