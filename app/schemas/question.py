# app/schemas/question.py
from pydantic import BaseModel, Field
from typing import List, Optional



# --- Option Schemas ---
class OptionBase(BaseModel):
    option_text: str = Field(..., min_length=1, description="选项文字")
    is_correct: bool

class OptionCreate(OptionBase):
    pass

class Option(OptionBase):
    id: int

    class Config:
        from_attributes = True

# --- Question Schemas ---
class QuestionBase(BaseModel):
    prompt: str= Field(..., min_length=1, description="题干")
    question_type: str = Field(..., description="问题类型，e.g., 'SINGLE_CHOICE' or 'MULTIPLE_CHOICE' or 'TRUE_FALSE'")
    scene_identifier: Optional[str] = None
    score: int
    image_url: Optional[str] = None

class QuestionCreate(QuestionBase):
    # 创建问题时，必须同时提供它的选项列表
    options: List[OptionCreate] = Field(..., min_length=1)

class QuestionUpdate(BaseModel):
    # 更新时，所有字段都是可选的
    prompt: Optional[str] = Field(None, min_length=1)
    question_type: Optional[str] = None
    scene_identifier: Optional[str] = None
    score: Optional[int] = None
    image_url: Optional[str] = None
    # 注意：更新选项通常是一个更复杂的操作（单独的端点），这里我们先简化
    options: Optional[List[OptionCreate]] = Field(None, min_length=1)
    
class Question(QuestionBase):
    id: int
    procedure_id: int
    # 从数据库读取时，自动加载关联的选项
    options: List[Option] = []

    class Config:
        from_attributes = True