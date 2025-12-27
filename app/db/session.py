# app/db/session.py (最终版本)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.pool import QueuePool
from app.core.config import settings
from typing import Generator

class Base(DeclarativeBase):
    """所有 SQLAlchemy 模型的基础类。"""
    # __tablename__ 将在各个模型中自动生成
    pass

# 创建数据库引擎
# 针对高并发场景优化连接池配置
engine = create_engine(
    url=settings.DATABASE_URL,
    echo=False,
    poolclass=QueuePool,

    # 针对 1000 线程的配置
    pool_size=100,  # 大幅增加常驻连接
    max_overflow=400,  # 允许更多溢出连接
    pool_pre_ping=True,
    pool_recycle=300,  # 5分钟回收，更快释放连接
    pool_timeout=3,  # 更短的超时时间
    pool_use_lifo=False,  # 高并发下改为先进先出

    # 添加连接参数
    connect_args={
        "connect_timeout": 2,
        "read_timeout": 10,
        "write_timeout": 10,
    },

    # 重要：增加连接池的线程安全性
    pool_reset_on_return='rollback',
)

# 创建一个可配置的 Session 类
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False  # 提交后不过期对象，减少不必要的刷新查询
)

# 依赖注入函数：为每个 API 请求提供一个独立的数据库会话
def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()