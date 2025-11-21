# app/schemas/question_bank.py
from pydantic import BaseModel
from typing import Optional
from pydantic import Field

class QuestionBankBase(BaseModel):
    name: str = Field(..., min_length=1, description="题库名称")

class QuestionBankCreate(QuestionBankBase):
    pass

class QuestionBankUpdate(QuestionBankBase):
    name: Optional[str] = Field(None, min_length=1)

class QuestionBank(QuestionBankBase):
    id: int
    platform_id: int

    class Config:
        from_attributes = True