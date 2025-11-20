# app/crud/crud_question.py (更新后)
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.question_management import Question, Option, QuestionType
from app.schemas.question import QuestionCreate, QuestionUpdate
from typing import List, Optional
from fastapi.encoders import jsonable_encoder
from typing import Union, Dict, Any


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
        # 1. 分离题目数据和选项数据
        obj_in_data = jsonable_encoder(obj_in)
        options_data = obj_in_data.pop("options", [])
        
        # 2. 创建题目
        db_question = Question(**obj_in_data, procedure_id=procedure_id)
        db.add(db_question)
        db.commit()
        db.refresh(db_question)
        
        # 3. 创建选项
        for opt in options_data:
            option = Option(**opt, question_id=db_question.id)
            db.add(option)

        db.commit()
        db.refresh(db_question)
        return db_question

    def update(
        self,
        db: Session,
        *,
        db_obj: Question,
        obj_in: Union[QuestionUpdate, Dict[str, Any]]
    ) -> Question:
        """
        重写更新逻辑，支持更新嵌套的 options (删除旧的，添加新的)
        """
        # 1. 获取更新数据字典
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        
        # 2. 提取 options 数据，不让它干扰 Question 本身的更新
        options_data = update_data.pop("options", None)

        # 3. 更新 Question 表的基础字段
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        
        db.add(db_obj)
        
        # 4. 处理 Options 更新 (核心修复)
        if options_data is not None:
            # 策略：物理删除该题目下所有旧选项，然后重新插入
            # 优点：逻辑简单，完全匹配前端传来的最新状态
            db.query(Option).filter(Option.question_id == db_obj.id).delete()
            
            # 添加新选项
            for opt in options_data:
                # 即使前端传了 id (用于回显)，插入新记录时也要去掉，让数据库自动生成新 ID
                if 'id' in opt: del opt['id']
                
                new_opt = Option(**opt, question_id=db_obj.id)
                db.add(new_opt)

        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi_by_procedure(self, db: Session, *, procedure_id: int, skip: int = 0, limit: int = 100) -> List[Question]:
        """
        通过工序/点位 ID 查询关联的题目。
        """
        return db.query(self.model).filter(self.model.procedure_id == procedure_id).offset(skip).limit(limit).all()

crud_question = CRUDQuestion(Question)