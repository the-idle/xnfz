# app/crud/crud_assessment_result.py
import json

from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.assessment_management import AssessmentResult, AnswerLog, Assessment
from app.models.question_management import Question, QuestionBank, Procedure
from app.schemas.examinee import BaseModel # 仅用于类型提示
from typing import List
from typing import Dict
from sqlalchemy.orm import selectinload



class CRUDAssessmentResult(CRUDBase[AssessmentResult, BaseModel, BaseModel]):
    def get_active_session(self, db: Session, *, assessment_id: int, examinee_id: int) -> AssessmentResult | None:
        """
        获取一个考生在某场考核下的、尚未结束的会话。
        """
        return db.query(AssessmentResult).filter(
            AssessmentResult.assessment_id == assessment_id,
            AssessmentResult.examinee_id == examinee_id,
            AssessmentResult.end_time == None
        ).first()

    def get_answered_question_ids(self, db: Session, *, result_id: int) -> List[int]:
        """
        获取某次考核会话中所有已回答问题的 ID 列表。
        """
        return [
            log.question_id for log in 
            db.query(AnswerLog.question_id).filter(AnswerLog.result_id == result_id).all()
        ]

    def get_all_questions_for_assessment(self, db: Session, *, assessment_id: int) -> List[Question]:
        """
        获取一场考核所关联的所有题库下的所有题目。
        """
        assessment = db.query(Assessment).get(assessment_id)
        if not assessment:
            return []
        
        # 这是一个多层嵌套查询
        questions = (
            db.query(Question)
            .join(Procedure)
            .join(QuestionBank)
            .filter(QuestionBank.id.in_(assessment.question_bank_ids))
            .all()
        )
        return questions

    def get_multi_by_assessment(
        self, db: Session, *, assessment_id: int, skip: int = 0, limit: int = 100
    ) -> List[AssessmentResult]:
        """
        获取某场考核下的所有成绩记录，并预加载考生和答题日志
        """
        return (
            db.query(AssessmentResult)
            .filter(AssessmentResult.assessment_id == assessment_id)
            .options(
                selectinload(AssessmentResult.examinee),
                selectinload(AssessmentResult.answer_logs)
            )
            .order_by(AssessmentResult.id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_answered_logs_map(self, db: Session, *, result_id: int) -> Dict[int, List[int]]:
        """
        获取某次考核会话中所有已回答题目的日志，并返回一个映射：
        { question_id: [selected_option_ids] }
        """
        logs = db.query(AnswerLog).filter(AnswerLog.result_id == result_id).all()
        
        answered_map = {}
        for log in logs:
            # 确保 selected_option_ids 是一个列表
            # SQLAlchemy 的 JSON 类型会自动反序列化
            if isinstance(log.selected_option_ids, list):
                answered_map[log.question_id] = {
                        'score_awarded':log.score_awarded,
                        'selected_option_ids':log.selected_option_ids
                    }
            else: # 作为后备方案，如果存的是字符串，则手动解析
                try:
                    answered_map[log.question_id] = {
                        'score_awarded':log.score_awarded,
                        'selected_option_ids':json.loads(log.selected_option_ids)
                    }
                except (json.JSONDecodeError, TypeError):
                    answered_map[log.question_id] = {
                        'score_awarded':None,
                        'selected_option_ids':[]
                    }
        return answered_map


crud_assessment_result = CRUDAssessmentResult(AssessmentResult)