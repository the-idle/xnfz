# app/models/user_management.py
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.db.session import Base

class User(Base):
    """管理员用户表 - 与 users 表完全对应"""
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    # 对应数据库的 tinyint(1) 类型
    is_superuser = Column(Boolean, default=False, nullable=True)

class Examinee(Base):
    """考生信息表 - 与 examinees 表完全对应"""
    __tablename__ = 'examinees'
    id = Column(Integer, primary_key=True, index=True)
    identifier = Column(String(100), unique=True, index=True, nullable=False)
    
    assessment_results = relationship("AssessmentResult", back_populates="examinee")