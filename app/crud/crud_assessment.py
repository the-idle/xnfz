# app/crud/crud_assessment.py
from app.crud.base import CRUDBase
from app.models.assessment_management import Assessment
from app.schemas.assessment import AssessmentCreate, AssessmentUpdate

class CRUDAssessment(CRUDBase[Assessment, AssessmentCreate, AssessmentUpdate]):
    # 目前不需要针对 Assessment 的特殊 CRUD 方法，
    # CRUDBase 提供的通用方法已经足够。
    # 未来如果需要，例如“获取所有正在进行的考核”，可以在这里添加。
    pass

# 创建一个 CRUDAssessment 类的实例，供 API 端点使用
crud_assessment = CRUDAssessment(Assessment)