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
    # echo=True 在开发时很有用，它会打印出所有执行的 SQL 语句
    echo=False,  # 生产环境建议关闭，减少日志开销
    poolclass=QueuePool,
    pool_size=30,  # 常驻连接数，根据 MySQL max_connections 调整
    max_overflow=70,  # 最大溢出连接数，pool_size + max_overflow = 100
    pool_pre_ping=True,  # 连接前先 ping，确保连接有效
    pool_recycle=1800,  # 30分钟后回收连接，避免 MySQL wait_timeout 断开
    pool_timeout=10,  # 获取连接超时时间（秒），超时抛异常而非无限等待
    pool_use_lifo=True,  # 后进先出，优先使用最近归还的连接，减少空闲连接超时
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