# app/crud/crud_examinee.py
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.crud.base import CRUDBase
from app.models.user_management import Examinee
from app.schemas.examinee import BaseModel # 仅用于类型提示，无实际 Schema

class CRUDExaminee(CRUDBase[Examinee, BaseModel, BaseModel]):
    def get_or_create_by_identifier(self, db: Session, *, identifier: str) -> Examinee:
        """
        通过标识符获取考生，如果不存在则创建。
        使用 INSERT ... ON DUPLICATE KEY 或异常捕获处理并发竞态条件。
        """
        # 1. 先尝试查询
        examinee = db.query(Examinee).filter(Examinee.identifier == identifier).first()
        if examinee:
            return examinee

        # 2. 不存在则尝试创建，使用异常捕获处理并发竞态
        try:
            examinee = Examinee(identifier=identifier)
            db.add(examinee)
            db.flush()  # 先 flush 检测冲突，不 commit
            db.commit()
            db.refresh(examinee)
            return examinee
        except IntegrityError:
            # 3. 并发冲突：另一个线程已创建，回滚后重新查询
            db.rollback()
            examinee = db.query(Examinee).filter(Examinee.identifier == identifier).first()
            if examinee:
                return examinee
            # 极端情况：如果还是查不到，抛出异常
            raise ValueError(f"无法获取或创建考生: {identifier}")

crud_examinee = CRUDExaminee(Examinee)