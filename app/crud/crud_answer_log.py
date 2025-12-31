# app/crud/crud_answer_log.py (最终修复版)
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Tuple
import pytz

from app.crud.base import CRUDBase
from app.models.assessment_management import AnswerLog, AssessmentResult
from app.models.question_management import Question
from sqlalchemy.orm import joinedload

from app.schemas.examinee import SubmitAnswerRequest
from pydantic import BaseModel

# 定义北京时区
BEIJING_TZ = pytz.timezone('Asia/Shanghai')

class CRUDAnswerLog(CRUDBase[AnswerLog, SubmitAnswerRequest, BaseModel]):
    def calculate_and_log_answer(
        self, db: Session, *, result: AssessmentResult, answer_in: SubmitAnswerRequest
    ) -> Tuple[int, bool]:
        # 1. 基础校验：问题是否存在，点位是否匹配
        question = (
            db.query(Question).options(joinedload(Question.options))
            .filter(Question.id == answer_in.question_id).first()
        )
        if not question: 
            raise ValueError(f"Question with id {answer_in.question_id} not found.")
        if question.procedure_id != answer_in.procedure_id: 
            raise ValueError("Procedure ID mismatch for the given question.")
            
        # --- 【核心新增校验】 ---
        # 2. 严格校验：所有提交的选项ID，是否都属于当前问题
        valid_option_ids_for_question = {opt.id for opt in question.options}
        submitted_option_ids = set(answer_in.selected_option_ids)
        
        if not submitted_option_ids.issubset(valid_option_ids_for_question):
            invalid_ids = submitted_option_ids - valid_option_ids_for_question
            raise ValueError(f"Invalid option ID(s) submitted for this question: {invalid_ids}")
        # --- 校验结束 ---

        # 3. 提取正确答案和计分
        correct_option_ids = {opt.id for opt in question.options if opt.is_correct}
        
        score_awarded = 0
        is_correct = False
        
        # (后续的计分逻辑、日志记录、分数更新等，完全保持不变)
        if question.question_type.value == 'deduction_single_choice':
            if submitted_option_ids == correct_option_ids:
                score_awarded = 0
                is_correct = True
            else:
                score_awarded = -question.score
                is_correct = False
        elif question.question_type.value == 'multiple_choice':
            if not submitted_option_ids.issubset(correct_option_ids):
                score_awarded = 0
                is_correct = False
            else:
                if submitted_option_ids == correct_option_ids:
                    score_awarded = question.score
                    is_correct = True
                elif submitted_option_ids:
                    if len(correct_option_ids) > 0:
                        score_per_option = question.score / len(correct_option_ids)
                        score_awarded = round(len(submitted_option_ids) * score_per_option)
                    else:
                        score_awarded = 0
                    is_correct = False
                else:
                    score_awarded = 0
                    is_correct = False
        elif question.question_type.value == 'single_choice':
            if submitted_option_ids == correct_option_ids:
                score_awarded = question.score
                is_correct = True

        # 4. 记录日志并提交（统一使用北京时间）
        now_beijing = datetime.now(BEIJING_TZ)
        db_log = AnswerLog(
            result_id=result.id,
            question_id=answer_in.question_id,
            selected_option_ids=answer_in.selected_option_ids,
            score_awarded=score_awarded,
            answered_at=now_beijing.replace(tzinfo=None)  # 去掉时区信息，存储为naive datetime
        )
        db.add(db_log)
        result.total_score = (result.total_score or 0) + score_awarded
        db.add(result)
        db.commit()
        db.refresh(result)
        
        return score_awarded, is_correct

crud_answer_log = CRUDAnswerLog(AnswerLog)