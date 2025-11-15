# app/crud/crud_question_bank.py
from sqlalchemy.orm import Session

from app.models.question_management import QuestionBank, Platform
from app.schemas.question_bank import QuestionBankCreate, QuestionBankUpdate
from .base import CRUDBase

class CRUDQuestionBank(CRUDBase[QuestionBank, QuestionBankCreate, QuestionBankUpdate]):
    def create_with_platform(
        self, db: Session, *, obj_in: QuestionBankCreate, platform_id: int
    ) -> QuestionBank:
        """
        创建一个新的题库，并将其与一个平台关联。
        """
        db_obj = QuestionBank(**obj_in.model_dump(), platform_id=platform_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

# 创建一个 CRUDQuestionBank 类的实例，供 API 端点使用
crud_question_bank = CRUDQuestionBank(QuestionBank)