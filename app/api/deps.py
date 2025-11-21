# app/api/deps.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from pydantic import ValidationError

from app.core import security
from app.core.config import settings
from app.db.session import get_db
from app.models.user_management import User
from app.schemas import user as user_schema
from app.crud.crud_user import crud_user
# 这一行是关键：它创建了一个 OAuth2 "流"，并指定了获取 token 的 URL
# FastAPI 会用它来在 Swagger UI 中自动添加 "Authorize" 按钮
reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"/api/v1/login/token"
)

def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(reusable_oauth2)
) -> User:
    """
    依赖函数：解码并验证 token，然后返回对应的用户模型
    """
    try:
        # 解码 JWT token
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        # 使用 TokenData schema 来验证 payload 的结构
        token_data = user_schema.TokenData(**payload)
    except (JWTError, ValidationError):
        # 如果 token 无效或 payload 格式不正确，则抛出异常
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="身份凭证无效或已过期，请重新登录。",
        )
    
    # 从 token 中获取用户名，并从数据库中查找用户
    user = crud_user.get_by_username(db, username=token_data.sub) # 'sub' 是 JWT 的标准主题字段
    
    if not user:
        # 如果在数据库中找不到该用户，抛出异常
        raise HTTPException(status_code=404, detail="未找到指定的用户。")
        
    return user

# app/api/deps.py
def get_current_active_superuser(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="用户权限不足，无法执行此操作。")
    return current_user