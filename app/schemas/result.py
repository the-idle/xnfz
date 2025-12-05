# app/schemas/result.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List
from typing import Optional

# --- 新增：选项快照 ---
class OptionSnapshot(BaseModel):
    id: int
    option_text: str
    is_correct: bool

# --- 新增：题目快照 ---
class QuestionSnapshot(BaseModel):
    prompt: str
    question_type: str
    score: int
    options: List[OptionSnapshot]


class AnswerLogDetail(BaseModel):
    question_id: int
    score_awarded: int
    answered_at: datetime
    selected_option_ids: List[int]

    question: Optional[QuestionSnapshot] = None 

    class Config:
        from_attributes = True

class AssessmentResultDetail(BaseModel):
    id: int
    total_score: Optional[int] = Field(0, description="总分")
    start_time: datetime
    end_time: Optional[datetime] = None
    examinee_identifier: str
    answer_logs: List[AnswerLogDetail]

    class Config:
        from_attributes = True