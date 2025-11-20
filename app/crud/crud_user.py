# app/crud/crud_user.py
from sqlalchemy.orm import Session
from app.models.user_management import User
from app.schemas.user import UserCreate
from app.core.security import get_password_hash
from app.schemas.user import UserUpdate
from app.crud.base import CRUDBase

class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def get_by_username(self, db: Session, *, username: str) -> User | None:
        return db.query(User).filter(User.username == username).first()

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        db_obj = User(
            username=obj_in.username,
            hashed_password=get_password_hash(obj_in.password),
            is_superuser=obj_in.is_superuser
        )
        db.add(db_obj); db.commit(); db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, db_obj: User, obj_in: UserUpdate) -> User:
        # 如果传入了新密码，则进行哈希处理
        if obj_in.password:
            hashed_password = get_password_hash(obj_in.password)
            db_obj.hashed_password = hashed_password
        
        # 更新 is_superuser 状态 (如果传入了)
        if obj_in.is_superuser is not None:
            db_obj.is_superuser = obj_in.is_superuser
            
        db.add(db_obj); db.commit(); db.refresh(db_obj)
        return db_obj

crud_user = CRUDUser(User)