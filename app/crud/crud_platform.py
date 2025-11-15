# app/crud/crud_platform.py
from sqlalchemy.orm import Session

from app.models.question_management import Platform
from app.schemas.platform import PlatformCreate, PlatformUpdate
from .base import CRUDBase

class CRUDPlatform(CRUDBase[Platform, PlatformCreate, PlatformUpdate]):
    def get_by_name(self, db: Session, *, name: str) -> Platform | None:
        """
        通过平台名称查询平台 (这是一个 Platform 特有的方法，所以我们保留它)。
        """
        return db.query(self.model).filter(self.model.name == name).first()

# 创建一个 CRUDPlatform 类的实例，供 API 端点使用
crud_platform = CRUDPlatform(Platform)