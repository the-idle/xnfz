# app/schemas/assessment.py
from pydantic import BaseModel
from typing import List
from datetime import datetime
from typing import Optional
from pydantic import Field
import pytz 
from datetime import timezone
from pydantic import validator


# --- Option Schemas ---
class OptionBase(BaseModel):
    option_text: str
    is_correct: bool

class OptionCreate(OptionBase):
    pass

class Option(OptionBase):
    id: int

    class Config:
        orm_mode = True

# --- Question Schemas ---
class QuestionBase(BaseModel):
    prompt: str
    question_type: str # 这里暂时用 str，后面可以映射为 Enum
    scene_identifier: Optional[str] = None
    score: int
    image_url: str | None = None

class QuestionCreate(QuestionBase):
    options: List[OptionCreate] # 创建问题时，必须同时创建它的选项

class Question(QuestionBase):
    id: int
    options: List[Option] = [] # 从数据库读取问题时，自动带上它的所有选项

    class Config:
        orm_mode = True

# --- Schema for Unity Client ---
class QuestionForExaminee(BaseModel):
    """专门为考生（Unity客户端）设计的题目数据结构，隐藏了 is_correct 答案信息"""
    question_id: int
    scene_identifier:Optional[str] = None
    prompt: str
    question_type: str
    score: int
    image_url: str | None = None 
    options: List['OptionForExaminee']

class OptionForExaminee(BaseModel):
    """专门为考生设计的选项数据结构"""
    option_id: int
    text: str # 字段名可以更友好

# 重新构建 QuestionForExaminee 以解决前向引用
# QuestionForExaminee.update_forward_refs(OptionForExaminee=OptionForExaminee)


# --- Assessment & Result Schemas ---
class AssessmentStart(BaseModel):
    examinee_identifier: str

class SubmitAnswer(BaseModel):
    question_id: int
    selected_option_ids: List[int]

class AnswerResponse(BaseModel):
    status: str
    score_awarded: int

class AssessmentResult(BaseModel):
    total_score: int
    start_time: datetime
    end_time: datetime | None

    class Config:
        orm_mode = True


# app/schemas/assessment.py
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class AssessmentBase(BaseModel):
    title: str = Field(..., min_length=1, description="考核标题")
    start_time: datetime
    end_time: datetime

    # --- 核心修改：只解析格式，不改时区，不减8小时 ---
    @validator('start_time', 'end_time', pre=True)
    def parse_datetime(cls, v):
        if isinstance(v, str):
            # 兼容 Element Plus 发送的 "YYYY-MM-DD HH:mm:ss" 格式
            try:
                return datetime.strptime(v, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                # 兼容 ISO 格式
                return datetime.fromisoformat(v.replace('Z', ''))
        return v

class AssessmentCreate(AssessmentBase):
    question_bank_id: int # <--- 核心修改

class AssessmentUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, description="考核标题")
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    question_bank_id: Optional[int] = None

    # --- 核心修改：只解析格式，不改时区 ---
    @validator('start_time', 'end_time', pre=True, always=True)
    def parse_datetime_update(cls, v):
        if v is None: return v
        if isinstance(v, str):
            try:
                return datetime.strptime(v, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                return datetime.fromisoformat(v.replace('Z', ''))
        return v

class Assessment(AssessmentBase):
    id: int
    question_bank_id: int

    class Config:
        from_attributes = True