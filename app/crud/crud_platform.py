# app/crud/crud_platform.py
from sqlalchemy.orm import Session

from app.models.question_management import Platform
from app.schemas.platform import PlatformCreate, PlatformUpdate
from app.core.security import get_password_hash, verify_password
from .base import CRUDBase

class CRUDPlatform(CRUDBase[Platform, PlatformCreate, PlatformUpdate]):
    def get_by_name(self, db: Session, *, name: str) -> Platform | None:
        """
        通过平台名称查询平台 (这是一个 Platform 特有的方法，所以我们保留它)。
        """
        return db.query(self.model).filter(self.model.name == name).first()

    def create(self, db: Session, *, obj_in: PlatformCreate) -> Platform:
        # 1. 排除 password 字段，因为我们要存的是 hash 后的
        create_data = obj_in.model_dump(exclude={"password"})
        db_obj = Platform(**create_data)
        
        # 2. 直接哈希密码 (因为 Schema 保证了 password 一定存在且不为 None)
        db_obj.hashed_password = get_password_hash(obj_in.password)
            
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, db_obj: Platform, obj_in: PlatformUpdate) -> Platform:
        """
        更新一个平台 (最终正确版)
        """
        # 1. 获取要更新的普通字段数据 (不包括 password)
        update_data = obj_in.model_dump(exclude_unset=True, exclude={"password"})

        # 2. 更新普通字段
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        # 3. 单独、特殊地处理密码字段
        # obj_in.password is not None 确保了即使前端传了空字符串 "" 也能被处理
        if obj_in.password is not None:
            if obj_in.password == "": # 如果是空字符串，表示清除密码
                db_obj.hashed_password = None
            else: # 如果是新密码，则哈希后更新
                db_obj.hashed_password = get_password_hash(obj_in.password)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

# 创建一个 CRUDPlatform 类的实例，供 API 端点使用
crud_platform = CRUDPlatform(Platform)