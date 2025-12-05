# app/crud/crud_assessment.py
from app.crud.base import CRUDBase
from app.models.assessment_management import Assessment
from app.schemas.assessment import AssessmentCreate, AssessmentUpdate
from app.models.question_management import QuestionBank

from datetime import datetime, timedelta
from sqlalchemy.orm import Session 


class CRUDAssessment(CRUDBase[Assessment, AssessmentCreate, AssessmentUpdate]):
    # 目前不需要针对 Assessment 的特殊 CRUD 方法，
    # CRUDBase 提供的通用方法已经足够。
    # 未来如果需要，例如“获取所有正在进行的考核”，可以在这里添加。
    def get_upcoming_or_active(self, db: Session, *, platform_id: int) -> Assessment | None:
        """
        在指定平台下，获取即将开始或正在进行的、最优先的考核。
        优先级：1. 正在进行的； 2. 即将开始且离现在最近的。
        """
        now = datetime.now() # 获取当前的 naive 时间
        
        # 1. 找到该平台下的所有题库ID
        platform_banks = db.query(QuestionBank.id).filter(QuestionBank.platform_id == platform_id).all()
        if not platform_banks: return None
        platform_bank_ids = [b.id for b in platform_banks]

        assessments = (
            db.query(Assessment)
            .filter(
                Assessment.question_bank_id.in_(platform_bank_ids),
                Assessment.end_time > now # 直接用 naive 时间比较
            )
            .order_by(Assessment.start_time.asc())
            .all()
        )
        
        if not assessments:
            return None

        # 3. 应用业务优先级逻辑
        # 优先返回已经开始的
        for assessment in assessments:
            if assessment.start_time <= now:
                return assessment
        
        # 如果没有正在进行的，则返回第一个即将开始的
        return assessments[0]


    def check_time_conflict(
        self, db: Session, *, question_bank_id: int, start_time: datetime, end_time: datetime
    ) -> bool:
        # 1. 先通过题库ID找到平台ID
        bank = db.query(QuestionBank).filter(QuestionBank.id == question_bank_id).first()
        if not bank:
            return False # 如果题库不存在，则没有平台，自然没有冲突
        
        platform_id = bank.platform_id

        # 2. 查询该平台下的所有题库
        platform_banks = db.query(QuestionBank.id).filter(QuestionBank.platform_id == platform_id).all()
        platform_bank_ids = [b.id for b in platform_banks]

        # 3. 检查这些题库关联的考核是否有时间重叠
        conflict = (
            db.query(Assessment)
            .filter(
                Assessment.question_bank_id.in_(platform_bank_ids),
                Assessment.start_time < end_time,
                Assessment.end_time > start_time
            )
            .first()
        )
        return conflict is not None

# 创建一个 CRUDAssessment 类的实例，供 API 端点使用
crud_assessment = CRUDAssessment(Assessment)