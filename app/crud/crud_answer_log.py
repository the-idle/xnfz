# app/crud/crud_answer_log.py
from sqlalchemy.orm import Session, joinedload
from datetime import datetime  # <--- 就是这一行！
from typing import Tuple

from app.crud.base import CRUDBase
from app.models.assessment_management import AnswerLog, AssessmentResult
from app.models.question_management import Question, Option, QuestionType # 导入 QuestionType 以便使用
from app.schemas.examinee import SubmitAnswerRequest
from pydantic import BaseModel

class CRUDAnswerLog(CRUDBase[AnswerLog, SubmitAnswerRequest, BaseModel]):
    def calculate_and_log_answer(
        self,
        db: Session,
        *,
        result: AssessmentResult,
        answer_in: SubmitAnswerRequest
    ) -> Tuple[int, bool]:
        """
        核心计分逻辑：计算得分，记录日志，并更新总分。
        返回 (本次得分, 是否完全正确)
        """
        # 1. 获取题目详情，并预加载其正确选项
        question = (
            db.query(Question)
            .options(joinedload(Question.options))
            .filter(Question.id == answer_in.question_id)
            .first()
        )
        if not question:
            raise ValueError("Question not found")

        # 2. 找出所有正确选项的 ID
        correct_option_ids = {opt.id for opt in question.options if opt.is_correct}
        
        # 3. 计算得分和是否正确
        score_awarded = 0
        is_correct = False
        
        submitted_option_ids = set(answer_in.selected_option_ids)

        # 使用 QuestionType 枚举进行比较，更健壮
        if question.question_type == QuestionType.SINGLE_CHOICE:
            if submitted_option_ids == correct_option_ids:
                score_awarded = question.score
                is_correct = True
        elif question.question_type == QuestionType.MULTIPLE_CHOICE:
            if submitted_option_ids == correct_option_ids:
                score_awarded = question.score
                is_correct = True
            
        # 4. 创建答题日志
        new_log = AnswerLog(
            result_id=result.id,
            question_id=answer_in.question_id,
            selected_option_ids=answer_in.selected_option_ids,
            score_awarded=score_awarded,
            answered_at=datetime.utcnow() # 现在 datetime 是已知的了
        )
        db.add(new_log)
        
        # 5. 更新考核会话的总分
        result.total_score = (result.total_score or 0) + score_awarded
        db.add(result)
        
        # 6. 一次性提交
        db.commit()
        
        return score_awarded, is_correct

crud_answer_log = CRUDAnswerLog(AnswerLog)