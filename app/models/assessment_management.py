# app/models/assessment_management.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.session import Base

class Assessment(Base):
    """考核场次表"""
    __tablename__ = 'assessments'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    
    # 关系：一场考核基于哪个平台
    # platform_id = Column(Integer, ForeignKey("platforms.id"))
    # 关系：这场考核从哪些题库抽题 (使用 JSON 存储题库 ID 列表)
    question_bank_id = Column(Integer, ForeignKey("question_banks.id"), nullable=False)
    question_bank = relationship("QuestionBank")
    results = relationship("AssessmentResult", back_populates="assessment")

class AssessmentResult(Base):
    """考生成绩与过程记录总表"""
    __tablename__ = 'assessment_results'
    id = Column(Integer, primary_key=True, index=True)
    total_score = Column(Integer, default=0)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime)
    
    assessment_id = Column(Integer, ForeignKey("assessments.id"))
    examinee_id = Column(Integer, ForeignKey("examinees.id"))
    
    assessment = relationship("Assessment", back_populates="results")
    examinee = relationship("Examinee", back_populates="assessment_results")
    answer_logs = relationship("AnswerLog", back_populates="result")

class AnswerLog(Base):
    """详细答题日志表"""
    __tablename__ = 'answer_logs'
    id = Column(Integer, primary_key=True, index=True)
    
    result_id = Column(Integer, ForeignKey("assessment_results.id"))
    question_id = Column(Integer, ForeignKey("questions.id"))
    # 存储用户选择的选项ID列表，如单选是[3]，多选是[4, 5]
    selected_option_ids = Column(JSON, nullable=False)
    score_awarded = Column(Integer, nullable=False)
    answered_at = Column(DateTime, nullable=False)

    result = relationship("AssessmentResult", back_populates="answer_logs")
    
    question = relationship("Question", back_populates="answer_logs")