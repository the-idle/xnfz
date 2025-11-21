# app/models/question_management.py
from sqlalchemy import (Column, Integer, String, Text, ForeignKey, 
                        Enum as SQLAlchemyEnum, Boolean)
from sqlalchemy.orm import relationship
from app.db.session import Base
import enum

# 定义与数据库 ENUM 类型完全匹配的 Python 枚举
class QuestionType(enum.Enum):
    SINGLE_CHOICE = "single_choice"
    MULTIPLE_CHOICE = "multiple_choice"
    DEDUCTION_SINGLE_CHOICE = "deduction_single_choice"

class Platform(Base):
    """平台表 - 与 platforms 表完全对应"""
    __tablename__ = 'platforms'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(191), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    hashed_password = Column(String(255), nullable=True)
    
    question_banks = relationship("QuestionBank", back_populates="platform", cascade="all, delete-orphan")

class QuestionBank(Base):
    """题库表 - 与 question_banks 表完全对应"""
    __tablename__ = 'question_banks'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    
    platform_id = Column(Integer, ForeignKey("platforms.id"))
    
    platform = relationship("Platform", back_populates="question_banks")
    procedures = relationship("Procedure", back_populates="question_bank", cascade="all, delete-orphan")

class Procedure(Base):
    """工序/点位表 - 与 procedures 表完全对应"""
    __tablename__ = 'procedures'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    
    question_bank_id = Column(Integer, ForeignKey("question_banks.id"))
    
    question_bank = relationship("QuestionBank", back_populates="procedures")
    questions = relationship("Question", back_populates="procedure", cascade="all, delete-orphan")

class Question(Base):
    """题目表 - 与 questions 表完全对应"""
    __tablename__ = 'questions'
    id = Column(Integer, primary_key=True, index=True)
    prompt = Column(Text, nullable=False)
    image_url = Column(String(512), nullable=True)
    question_type = Column(SQLAlchemyEnum(QuestionType), nullable=False)
    scene_identifier = Column(String(100), nullable=True, unique=False) 
    score = Column(Integer, nullable=False)
    
    procedure_id = Column(Integer, ForeignKey("procedures.id"))
    
    procedure = relationship("Procedure", back_populates="questions")
    options = relationship("Option", back_populates="question", cascade="all, delete-orphan")

class Option(Base):
    """选项表 - 与 options 表完全对应"""
    __tablename__ = 'options'
    id = Column(Integer, primary_key=True, index=True)
    option_text = Column(Text, nullable=False)
    # 对应数据库的 tinyint(1) 类型
    is_correct = Column(Boolean, default=False, nullable=True)
    
    question_id = Column(Integer, ForeignKey("questions.id"))
    
    question = relationship("Question", back_populates="options")