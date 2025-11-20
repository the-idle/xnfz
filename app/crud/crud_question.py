# app/crud/crud_question.py (更新后)
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.question_management import Question, Option
from app.schemas.question import QuestionCreate, QuestionUpdate
from typing import List, Optional



class CRUDQuestion(CRUDBase[Question, QuestionCreate, QuestionUpdate]):
    def get_by_scene_identifier(self, db: Session, *, scene_identifier: str) -> Question | None:
        """
        通过场景标识符查询题目。
        """
        return db.query(self.model).filter(self.model.scene_identifier == scene_identifier).first()
    
    def create_with_options(
        self, db: Session, *, obj_in: QuestionCreate, procedure_id: int # <--- 修改
    ) -> Question:
        """
        创建一个新题目（含选项），并与一个工序/点位关联。
        """
        question_data = obj_in.model_dump(exclude={'options'})
        db_question = Question(**question_data, procedure_id=procedure_id) # <--- 修改
        
        db_options = [Option(**opt.model_dump()) for opt in obj_in.options]
        db_question.options = db_options
        
        db.add(db_question)
        db.commit()
        db.refresh(db_question)
        return db_question

    def get_multi_by_procedure(self, db: Session, *, procedure_id: int, skip: int = 0, limit: int = 100) -> List[Question]:
        """
        通过工序/点位 ID 查询关联的题目。
        """
        return db.query(self.model).filter(self.model.procedure_id == procedure_id).offset(skip).limit(limit).all()

crud_question = CRUDQuestion(Question)