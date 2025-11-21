
# app/schemas/examinee.py
from pydantic import BaseModel, Field
from typing import List, Optional
# --- 蓝图结构 (Blueprint) ---
class BlueprintOption(BaseModel):
    """
    下发给客户端的选项结构
    """
    id: int # <--- 核心修改：直接下发 option.id
    option_text: str

class BlueprintQuestion(BaseModel):
    """
    下发给客户端的题目结构
    """
    id: int # <--- 核心修改：直接下发 question.id
    scene_identifier: Optional[str] = None
    prompt: str
    question_type: str
    score: int
    image_url: Optional[str] = None
    options: List[BlueprintOption]
    selected_option_ids: Optional[List[int]] = None
    score_awarded: int|None = None

class BlueprintProcedure(BaseModel):
    """
    下发给客户端的工序/点位结构
    """
    id: int # <--- 核心修改：直接下发 procedure.id
    name: str # <--- 核心修改：直接下发 procedure.name
    questions: List[BlueprintQuestion]

class AssessmentStartRequest(BaseModel):
    examinee_identifier: str = Field(..., min_length=1, description="考生标识符")

class AssessmentBlueprintResponse(BaseModel):
    """
    开始/继续考核的响应体 (最终版)
    """
    assessment_result_id: int
    procedures: List[BlueprintProcedure] # <--- 返回结构化的蓝图

# --- 提交答案的 Schema (SubmitAnswerRequest) ---
class SubmitAnswerRequest(BaseModel):
    examinee_identifier: str = Field(..., min_length=1, description="考生标识符") # <--- 新增，用于校验考生身份
    procedure_id: int # <--- 明确点位ID
    question_id: int # <--- 明确题目ID
    selected_option_ids: List[int] = Field(..., min_length=1)# <--- 核心修改：提交真实的 option.id

class SubmitAnswerResponse(BaseModel):
    status: str
    score_awarded: int
    is_correct: bool

# --- 结束考核的 Schema (FinishAssessmentRequest) ---
class FinishAssessmentRequest(BaseModel):
    examinee_identifier: str = Field(..., min_length=1, description="考生标识符") # <--- 新增，用于校验考生身份
