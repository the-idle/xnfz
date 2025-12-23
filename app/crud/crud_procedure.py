# app/crud/crud_procedure.py
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.question_management import Procedure, Question
from app.models.assessment_management import AnswerLog
from app.schemas.procedure import ProcedureCreate, ProcedureUpdate
from typing import List, Optional



class CRUDProcedure(CRUDBase[Procedure, ProcedureCreate, ProcedureUpdate]):
    def create_with_bank(
        self, db: Session, *, obj_in: ProcedureCreate, question_bank_id: int
    ) -> Procedure:
        """
        创建一个新的工序/点位，并与一个题库关联。
        """
        db_obj = Procedure(**obj_in.model_dump(), question_bank_id=question_bank_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi_by_bank(self, db: Session, *, question_bank_id: int, skip: int = 0, limit: int = 100) -> List[Procedure]:
        return db.query(self.model).filter(self.model.question_bank_id == question_bank_id).offset(skip).limit(limit).all()

    def remove(self, db: Session, *, id: int) -> Procedure:
        """
        删除工序，同时清理关联的 answer_logs 记录以避免外键约束错误
        """
        # 1. 获取该工序下所有题目的 ID
        question_ids = db.query(Question.id).filter(Question.procedure_id == id).all()
        question_ids = [q[0] for q in question_ids]

        # 2. 删除这些题目关联的 answer_logs 记录
        if question_ids:
            db.query(AnswerLog).filter(AnswerLog.question_id.in_(question_ids)).delete(synchronize_session=False)

        # 3. 删除工序（会级联删除题目和选项）
        obj = db.query(self.model).get(id)
        db.delete(obj)
        db.commit()
        return obj

crud_procedure = CRUDProcedure(Procedure)