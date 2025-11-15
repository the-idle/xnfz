# app/crud/crud_examinee.py
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.user_management import Examinee
from app.schemas.examinee import BaseModel # 仅用于类型提示，无实际 Schema

class CRUDExaminee(CRUDBase[Examinee, BaseModel, BaseModel]):
    def get_or_create_by_identifier(self, db: Session, *, identifier: str) -> Examinee:
        """
        通过标识符获取考生，如果不存在则创建。
        """
        examinee = db.query(Examinee).filter(Examinee.identifier == identifier).first()
        if not examinee:
            examinee = Examinee(identifier=identifier)
            db.add(examinee)
            db.commit()
            db.refresh(examinee)
        return examinee

crud_examinee = CRUDExaminee(Examinee)