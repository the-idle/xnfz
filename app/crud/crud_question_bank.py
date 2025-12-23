# app/crud/crud_question_bank.py
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.question_management import QuestionBank, Platform, Procedure, Question
from app.schemas.question_bank import QuestionBankCreate, QuestionBankUpdate
from .base import CRUDBase

class CRUDQuestionBank(CRUDBase[QuestionBank, QuestionBankCreate, QuestionBankUpdate]):

    def get_total_score(self, db: Session, *, question_bank_id: int) -> int:
        """
        计算题库的总分（所有题目分数之和）
        """
        result = db.query(func.sum(Question.score)).join(
            Procedure, Question.procedure_id == Procedure.id
        ).filter(
            Procedure.question_bank_id == question_bank_id
        ).scalar()
        return result or 0

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
    
    def get_multi_by_platform(
        self, db: Session, *, platform_id: int, skip: int = 0, limit: int = 100
    ) -> list[QuestionBank]:
        """
        获取指定平台下的所有题库。
        """
        return db.query(self.model).filter(self.model.platform_id == platform_id).offset(skip).limit(limit).all()

    def get_by_name_and_platform(self, db: Session, *, name: str, platform_id: int) -> QuestionBank | None:
        """
        在指定平台下，通过名称查找题库。
        """
        return db.query(self.model).filter(self.model.name == name, self.model.platform_id == platform_id).first()

# 创建一个 CRUDQuestionBank 类的实例，供 API 端点使用
crud_question_bank = CRUDQuestionBank(QuestionBank)