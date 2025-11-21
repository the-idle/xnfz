# app/schemas/procedure.py
from pydantic import BaseModel
from typing import Optional

from pydantic import Field

class ProcedureBase(BaseModel):
    name: str = Field(..., min_length=1, description="工序/点位名称")

class ProcedureCreate(ProcedureBase):
    pass # ID 从路径获取

class ProcedureUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1)

class Procedure(ProcedureBase):
    id: int
    question_bank_id: int

    class Config:
        from_attributes = True