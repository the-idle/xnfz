from app.db.session import Base
from app.models import user_management
from app.models import question_management
from app.models import assessment_management
# initial_data.py
import asyncio
# initial_data.py (更健壮的同步版本)
from app.db.session import SessionLocal
from app.crud import crud_user
from app.schemas import UserCreate

def init_db():
    db = SessionLocal()
    try:
        user = crud_user.get_user_by_username(db, username="admin")
        if not user:
            user_in = UserCreate(username="admin", password="password")
            crud_user.create_user(db, user_in=user_in)
            print("超级用户 'admin' 创建成功，密码 'password'")
        else:
            print("用户 'admin' 已存在")
    finally:
        db.close()

if __name__ == "__main__":
    print("正在初始化数据...")
    init_db()
    print("数据初始化完成。")