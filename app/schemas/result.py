# app/schemas/result.py
from pydantic import BaseModel
from datetime import datetime
from typing import List
from typing import Optional

class AnswerLogDetail(BaseModel):
    question_id: int
    score_awarded: int
    answered_at: datetime

    class Config:
        from_attributes = True

class AssessmentResultDetail(BaseModel):
    id: int
    total_score: int
    start_time: datetime
    end_time: Optional[datetime] = None
    examinee_identifier: str
    answer_logs: List[AnswerLogDetail]

    class Config:
        from_attributes = True