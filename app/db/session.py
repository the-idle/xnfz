# app/db/session.py (最终版本)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.core.config import settings
from typing import Generator

class Base(DeclarativeBase):
    """所有 SQLAlchemy 模型的基础类。"""
    # __tablename__ 将在各个模型中自动生成
    pass

# 创建数据库引擎
engine = create_engine(
    url=settings.DATABASE_URL,
    # echo=True 在开发时很有用，它会打印出所有执行的 SQL 语句
    echo=True, # 建议在开发时开启
    pool_size=50,  # 增加常驻连接数
    max_overflow=100,  # 增加最大溢出连接数
    pool_pre_ping=True,  # 连接前先ping，确保连接有效
    pool_recycle=3600,  # 1小时后回收连接，避免数据库连接超时
    pool_timeout=30,  # 连接获取超时时间（秒）
)

# 创建一个可配置的 Session 类
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# 依赖注入函数：为每个 API 请求提供一个独立的数据库会话
def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()