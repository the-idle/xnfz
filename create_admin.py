# create_admin.py
import sys
import os

# 将当前目录加入 Python 路径
sys.path.append(os.getcwd())

from app.db.session import SessionLocal
from app.models.user_management import User
from app.core.security import get_password_hash
# 导入其他模型防止报错
from app.models import question_management
from app.models import assessment_management 

def init_db():
    db = SessionLocal()
    
    # 你想创建的账号密码
    username = "admin" 
    password = "password" 
    
    user = db.query(User).filter(User.username == username).first()
    
    if user:
        print(f"用户 {username} 已存在，正在重置密码...")
        user.hashed_password = get_password_hash(password)
        user.is_superuser = True
        # 模型里没有 is_active，不需要设置
    else:
        print(f"正在创建超级管理员 {username} ...")
        user = User(
            username=username,
            hashed_password=get_password_hash(password),
            is_superuser=True
            # 删除 is_active, full_name, email，因为你的数据库模型里没有这些字段
        )
        db.add(user)
    
    try:
        db.commit()
        print(f"✅ 成功！")
        print(f"账号: {username}")
        print(f"密码: {password}")
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("开始初始化管理员账号...")
    init_db()