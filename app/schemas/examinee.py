# # app/schemas/examinee.py
# from pydantic import BaseModel, Field

# from typing import List, Optional

# # --- 用于返回给 Unity 客户端的选项和题目结构 ---
# class OptionForExaminee(BaseModel):
#     """
#     选项 Schema (隐藏 is_correct)
#     """
#     option_id: int= Field(alias='id')
#     option_text: str

#     class Config:
#         from_attributes = True # 确保 orm_mode 开启

# class QuestionForExaminee(BaseModel):
#     """
#     题目 Schema (隐藏 is_correct)
#     """
#     question_id: int = Field(alias='id')
#     scene_identifier: str
#     prompt: str
#     question_type: str
#     score: int
#     image_url: Optional[str] = None
#     options: List[OptionForExaminee]
#     class Config:
#         from_attributes = True # 确保 orm_mode 开启

# # --- 用于开始/继续考核的 API 模型 ---
# class AssessmentStartRequest(BaseModel):
#     """
#     开始/继续考核的请求体
#     """
#     examinee_identifier: str # 机位号/座位号

# class AssessmentSessionResponse(BaseModel):
#     """
#     开始/继续考核的响应体
#     """
#     assessment_result_id: int
#     questions_to_answer: List[QuestionForExaminee]

# # --- 用于提交答案的 API 模型 ---
# class SubmitAnswerRequest(BaseModel):
#     """
#     提交答案的请求体
#     """
#     question_id: int
#     selected_option_ids: List[int]

# class SubmitAnswerResponse(BaseModel):
#     """
#     提交答案的响应体
#     """
#     status: str
#     score_awarded: int
#     is_correct: bool # 告知客户端本次回答是否正确

# app/schemas/examinee.py
from pydantic import BaseModel
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

class BlueprintProcedure(BaseModel):
    """
    下发给客户端的工序/点位结构
    """
    id: int # <--- 核心修改：直接下发 procedure.id
    name: str # <--- 核心修改：直接下发 procedure.name
    questions: List[BlueprintQuestion]

class AssessmentStartRequest(BaseModel):
    examinee_identifier: str

class AssessmentBlueprintResponse(BaseModel):
    """
    开始/继续考核的响应体 (最终版)
    """
    assessment_result_id: int
    procedures: List[BlueprintProcedure] # <--- 返回结构化的蓝图

# --- 提交答案的 Schema (SubmitAnswerRequest) ---
class SubmitAnswerRequest(BaseModel):
    examinee_identifier: str # <--- 新增，用于校验考生身份
    procedure_id: int # <--- 明确点位ID
    question_id: int # <--- 明确题目ID
    selected_option_ids: List[int] # <--- 核心修改：提交真实的 option.id

class SubmitAnswerResponse(BaseModel):
    status: str
    score_awarded: int
    is_correct: bool

# --- 结束考核的 Schema (FinishAssessmentRequest) ---
class FinishAssessmentRequest(BaseModel):
    examinee_identifier: str # <--- 新增，用于校验考生身份