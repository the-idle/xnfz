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
from pydantic import BaseModel, Field
from typing import List

# --- 蓝图结构 ---
class BlueprintOption(BaseModel):
    answer_id: int
    option_text: str

class BlueprintQuestion(BaseModel):
    question_id: int
    scene_identifier: str
    prompt: str
    question_type: str
    score: int
    image_url: str | None = None
    options: List[BlueprintOption]

class BlueprintProcedure(BaseModel):
    procedure_id: int
    procedure_name: str
    questions: List[BlueprintQuestion]

# --- API 请求和响应 ---
class AssessmentStartRequest(BaseModel):
    examinee_identifier: str

class AssessmentBlueprintResponse(BaseModel):
    assessment_result_id: int
    procedures: List[BlueprintProcedure]

class SubmitAnswerRequest(BaseModel):
    selected_answer_ids: List[int] # <--- 核心修改

class SubmitAnswerResponse(BaseModel):
    status: str
    score_awarded: int
    is_correct: bool