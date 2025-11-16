# app/crud/crud_answer_log.py (最终、最健-壮、最正确版本)
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Tuple

from app.crud.base import CRUDBase
from app.models.assessment_management import AnswerLog, AssessmentResult
from app.schemas.examinee import SubmitAnswerRequest
from pydantic import BaseModel

class CRUDAnswerLog(CRUDBase[AnswerLog, SubmitAnswerRequest, BaseModel]):
    def calculate_and_log_answer(
        self, db: Session, *, result: AssessmentResult, answer_in: SubmitAnswerRequest, answer_map: dict
    ) -> Tuple[int, bool]:
        """
        核心计分逻辑（最终防御性版本）
        """
        if not answer_in.selected_option_ids:
            raise ValueError("No options submitted.")
        
        # --- 提取题目信息 ---
        first_option_id_str = str(answer_in.selected_option_ids[0])
        if first_option_id_str not in answer_map:
            raise ValueError(f"Invalid option ID {first_option_id_str} submitted.")
        
        question_info = answer_map[first_option_id_str]
        question_id = question_info['question_id']
        question_score = question_info['question_score']
        question_type = question_info['question_type']
        
        # --- 找出该题目的所有正确答案 ---
        correct_option_ids = set()
        for opt_id, info in answer_map.items():
            # 使用严格的、防御性的检查
            if info.get('question_id') == question_id and info.get('is_correct') is True:
                correct_option_ids.add(int(opt_id))

        # --- 进行计分 ---
        score_awarded = 0
        is_correct = False
        submitted_option_ids = set(answer_in.selected_option_ids)

        # 核心判断：两个整数集合必须完全相等
        if submitted_option_ids == correct_option_ids:
            score_awarded = question_score
            is_correct = True
            
        # --- 记录日志 ---
        # 核心修正：SQLAlchemy 的 JSON 类型会自动处理序列化，我们只需要传递 Python 列表
        db_log = AnswerLog(
            result_id=result.id,
            question_id=question_id,
            selected_option_ids=answer_in.selected_option_ids, # <--- 直接传递列表
            score_awarded=score_awarded,
            answered_at=datetime.utcnow()
        )
        db.add(db_log)
        
        # --- 更新总分 ---
        result.total_score = (result.total_score or 0) + score_awarded
        db.add(result)
        
        db.commit()
        db.refresh(result)
        
        return score_awarded, is_correct

crud_answer_log = CRUDAnswerLog(AnswerLog)