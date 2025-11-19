# app/models/question_management.py
from sqlalchemy import (Column, Integer, String, Text, ForeignKey, 
                        Enum as SQLAlchemyEnum, Boolean)
from sqlalchemy.orm import relationship
from app.db.session import Base
import enum

# QuestionType 枚举保持不变
class QuestionType(enum.Enum):
    SINGLE_CHOICE = "single_choice"
    MULTIPLE_CHOICE = "multiple_choice"
    DEDUCTION_SINGLE_CHOICE = "deduction_single_choice" # <--- 新增扣分单选题

# Platform 模型保持不变
class Platform(Base):
    __tablename__ = 'platforms'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(191), nullable=False, unique=True, comment="如：班组长现场管理平台 V1.0")
    description = Column(Text)
    
    question_banks = relationship("QuestionBank", back_populates="platform", cascade="all, delete-orphan")

# QuestionBank 模型保持不变，但 relationship 会有微调
class QuestionBank(Base):
    __tablename__ = 'question_banks'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    
    platform_id = Column(Integer, ForeignKey("platforms.id"))
    
    platform = relationship("Platform", back_populates="question_banks")
    
    # --- 修正关系 ---
    # 一个题库现在拥有多个“工序/点位”
    procedures = relationship("Procedure", back_populates="question_bank", cascade="all, delete-orphan")

# --- 新增模型：Procedure (工序/点位) ---
class Procedure(Base):
    __tablename__ = 'procedures'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, comment="工序或点位的名称，如：车床A点")
    
    # 外键，指向它所属的题库
    question_bank_id = Column(Integer, ForeignKey("question_banks.id"))
    
    # 关系：反向指向 QuestionBank
    question_bank = relationship("QuestionBank", back_populates="procedures")
    # 关系：一个工序/点位下可以有多道题目
    questions = relationship("Question", back_populates="procedure", cascade="all, delete-orphan")

# Question 模型修改：现在它属于一个 Procedure，而不是直接属于 QuestionBank
class Question(Base):
    __tablename__ = 'questions'
    id = Column(Integer, primary_key=True, index=True)
    prompt = Column(Text, nullable=False, comment="题干/交互界面的提示文字")
    image_url = Column(String(512), nullable=True, comment="题目关联的图片URL或路径")
    question_type = Column(SQLAlchemyEnum(QuestionType), nullable=False)
    scene_identifier = Column(String(100), nullable=False, unique=True, comment="场景中的唯一标识，如'gongxu_1_wuliao'")
    score = Column(Integer, nullable=False, default=5, comment="该题目的总分值")
    
    # --- 修正外键和关系 ---
    # 外键现在指向 'procedures' 表
    procedure_id = Column(Integer, ForeignKey("procedures.id"))
    
    # 关系：反向指向 Procedure
    procedure = relationship("Procedure", back_populates="questions")
    
    # 与 Option 的关系保持不变
    options = relationship("Option", back_populates="question", cascade="all, delete-orphan")
    answer_logs = relationship("AnswerLog", back_populates="question")

# Option 模型保持不变
class Option(Base):
    __tablename__ = 'options'
    id = Column(Integer, primary_key=True, index=True)
    option_text = Column(Text, nullable=False)
    is_correct = Column(Boolean, default=False, comment="是否为正确答案")
    
    question_id = Column(Integer, ForeignKey("questions.id"))
    
    question = relationship("Question", back_populates="options")