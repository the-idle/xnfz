# app/crud/crud_assessment_result.py
import json
from datetime import datetime
import pytz

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.crud.base import CRUDBase
from app.models.assessment_management import AssessmentResult, AnswerLog, Assessment
from app.models.question_management import Question, QuestionBank, Procedure
from app.schemas.examinee import BaseModel # 仅用于类型提示
from typing import List, Tuple
from typing import Dict
from sqlalchemy.orm import selectinload

# 定义北京时区
BEIJING_TZ = pytz.timezone('Asia/Shanghai')



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

    def get_or_create_active_session(
        self, db: Session, *, assessment_id: int, examinee_id: int
    ) -> Tuple[AssessmentResult, bool]:
        """
        获取或创建活跃会话，处理并发竞态条件。
        返回: (session, is_new) - session 对象和是否是新创建的标志
        """
        # 1. 先尝试获取已存在的会话
        session = self.get_active_session(db=db, assessment_id=assessment_id, examinee_id=examinee_id)
        if session:
            return session, False

        # 2. 不存在则尝试创建，使用异常捕获处理并发
        try:
            # 统一使用北京时间，并转换为naive datetime存储
            now_beijing = datetime.now(BEIJING_TZ)
            session = AssessmentResult(
                assessment_id=assessment_id,
                examinee_id=examinee_id,
                start_time=now_beijing.replace(tzinfo=None)  # 去掉时区信息，存储为naive datetime
            )
            db.add(session)
            db.flush()  # 先 flush 检测冲突
            db.commit()
            db.refresh(session)
            return session, True
        except IntegrityError:
            # 3. 并发冲突：另一个线程已创建，回滚后重新查询
            db.rollback()
            session = self.get_active_session(db=db, assessment_id=assessment_id, examinee_id=examinee_id)
            if session:
                return session, False
            # 极端情况：如果还是查不到，抛出异常
            raise ValueError(f"无法获取或创建考核会话: assessment={assessment_id}, examinee={examinee_id}")

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

    def get_count_by_assessment(self, db: Session, *, assessment_id: int) -> int:
        """
        获取某场考核下的成绩记录总数
        """
        return db.query(AssessmentResult).filter(
            AssessmentResult.assessment_id == assessment_id
        ).count()

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

    def get_finished_session(self, db: Session, *, assessment_id: int, examinee_id: int) -> AssessmentResult | None:
        """
        查找一个考生在某场考核下，是否已存在【已完成】的会话。
        """
        return db.query(AssessmentResult).filter(
            AssessmentResult.assessment_id == assessment_id,
            AssessmentResult.examinee_id == examinee_id,
            AssessmentResult.end_time != None # 核心条件：end_time 不为空
        ).first()


crud_assessment_result = CRUDAssessmentResult(AssessmentResult)