# app/schemas/question_bank.py
from pydantic import BaseModel
from typing import Optional

class QuestionBankBase(BaseModel):
    name: str

class QuestionBankCreate(QuestionBankBase):
    pass

class QuestionBankUpdate(QuestionBankBase):
    name: Optional[str] = None # 更新时，名称是可选的

class QuestionBank(QuestionBankBase):
    id: int
    platform_id: int

    class Config:
        from_attributes = True