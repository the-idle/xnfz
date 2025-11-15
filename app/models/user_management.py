# app/models/user_management.py
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.db.session import Base

class User(Base):
    """管理员表"""
    __tablename__ = 'users' # 使用复数形式，更符合规范
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_superuser = Column(Boolean, default=True)

class Examinee(Base):
    """考生信息表"""
    __tablename__ = 'examinees'
    id = Column(Integer, primary_key=True, index=True)
    # 使用 seat_number 或 machine_code 作为唯一标识
    identifier = Column(String(100), unique=True, index=True, nullable=False)
    
    # 关系：一个考生可以有多条考核记录
    assessment_results = relationship("AssessmentResult", back_populates="examinee")