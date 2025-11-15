# app/schemas/procedure.py
from pydantic import BaseModel
from typing import Optional

class ProcedureBase(BaseModel):
    name: str

class ProcedureCreate(ProcedureBase):
    pass # ID 从路径获取

class ProcedureUpdate(BaseModel):
    name: Optional[str] = None

class Procedure(ProcedureBase):
    id: int
    question_bank_id: int

    class Config:
        from_attributes = True