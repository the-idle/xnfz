# app/schemas/question.py
from pydantic import BaseModel, Field
from typing import List, Optional



# --- Option Schemas ---
class OptionBase(BaseModel):
    option_text: str
    is_correct: bool

class OptionCreate(OptionBase):
    pass

class Option(OptionBase):
    id: int

    class Config:
        from_attributes = True

# --- Question Schemas ---
class QuestionBase(BaseModel):
    prompt: str
    question_type: str = Field(..., description="e.g., 'SINGLE_CHOICE' or 'MULTIPLE_CHOICE'")
    scene_identifier: Optional[str] = None
    score: int
    image_url: Optional[str] = None

class QuestionCreate(QuestionBase):
    # 创建问题时，必须同时提供它的选项列表
    options: List[OptionCreate]

class QuestionUpdate(BaseModel):
    # 更新时，所有字段都是可选的
    prompt: Optional[str] = None
    question_type: Optional[str] = None
    scene_identifier: Optional[str] = None
    score: Optional[int] = None
    image_url: Optional[str] = None
    # 注意：更新选项通常是一个更复杂的操作（单独的端点），这里我们先简化
    
class Question(QuestionBase):
    id: int
    procedure_id: int
    # 从数据库读取时，自动加载关联的选项
    options: List[Option] = []

    class Config:
        from_attributes = True