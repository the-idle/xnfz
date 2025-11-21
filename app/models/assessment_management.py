# app/models/assessment_management.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.session import Base

class Assessment(Base):
    """考核场次表 - 与 assessments 表完全对应"""
    __tablename__ = 'assessments'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    
    # 关系：一场考核只使用一个题库
    question_bank_id = Column(Integer, ForeignKey("question_banks.id"), nullable=False)
    
    # ORM 关系，方便在代码中通过 assessment.question_bank 访问
    question_bank = relationship("QuestionBank")
    # ORM 关系，方便通过 assessment.results 访问所有考核结果
    results = relationship("AssessmentResult", back_populates="assessment")

class AssessmentResult(Base):
    """考生成绩与过程记录总表 - 与 assessment_results 表完全对应"""
    __tablename__ = 'assessment_results'
    id = Column(Integer, primary_key=True, index=True)
    total_score = Column(Integer, nullable=True) # 数据库中可为NULL
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True) # 考核结束前为NULL
    
    assessment_id = Column(Integer, ForeignKey("assessments.id"))
    examinee_id = Column(Integer, ForeignKey("examinees.id"))
    
    assessment = relationship("Assessment", back_populates="results")
    examinee = relationship("Examinee", back_populates="assessment_results")
    answer_logs = relationship("AnswerLog", back_populates="result")

class AnswerLog(Base):
    """详细答题日志表 - 与 answer_logs 表完全对应"""
    __tablename__ = 'answer_logs'
    id = Column(Integer, primary_key=True, index=True)
    
    result_id = Column(Integer, ForeignKey("assessment_results.id"))
    question_id = Column(Integer, ForeignKey("questions.id"))
    
    # 对应数据库的 JSON 类型，SQLAlchemy 会自动处理 Python 列表/字典与 JSON 的转换
    selected_option_ids = Column(JSON, nullable=False)
    score_awarded = Column(Integer, nullable=False)
    answered_at = Column(DateTime, nullable=False)

    result = relationship("AssessmentResult", back_populates="answer_logs")
    question = relationship("Question") # 单向关系即可，如果 Question 不需要反向访问