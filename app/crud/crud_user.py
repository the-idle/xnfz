# app/crud/crud_user.py
from sqlalchemy.orm import Session
from app.models.user_management import User
from app.schemas.user import UserCreate
from app.core.security import get_password_hash

def get_user_by_username(db: Session, *, username: str) -> User | None:
    """
    通过用户名从数据库中获取用户
    """
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, *, user_in: UserCreate) -> User:
    """
    创建新用户
    """
    db_user = User(
        username=user_in.username,
        hashed_password=get_password_hash(user_in.password),
        is_superuser=True # 默认为超级用户
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user