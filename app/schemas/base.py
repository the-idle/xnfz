# app/schemas/base.py
from pydantic import BaseModel

class BaseSchema(BaseModel):
    class Config:
        orm_mode = True # 核心配置：允许 Pydantic 模型从 ORM 对象（我们的数据库模型）中读取数据