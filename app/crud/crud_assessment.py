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
    def get_most_recent_active(self, db: Session) -> Assessment | None:
        """
        获取距离现在最近的一场、且在7天内的有效考核。
        """
        now = datetime.utcnow()
        seven_days_later = now + timedelta(days=7)
        
        return (
            db.query(Assessment)
            .filter(
                Assessment.start_time <= now, # 已经开始
                Assessment.end_time >= now,   # 尚未结束
                Assessment.start_time <= seven_days_later # 且开始时间在未来7天内（这个条件其实被前两个覆盖了，主要是为了筛选近期）
            )
            .order_by(Assessment.start_time.asc()) # 按开始时间升序，获取最早开始的那个
            .first()
        )


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