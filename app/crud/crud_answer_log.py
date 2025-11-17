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
        核心计分逻辑（最终版，支持多选递减计分）
        """
        # ... (前置校验，提取 question_id, question_score, question_type 的逻辑不变) ...
        if not answer_in.selected_option_ids:
            raise ValueError("No options submitted.")
        
        first_option_id_str = str(answer_in.selected_option_ids[0])
        if first_option_id_str not in answer_map:
            raise ValueError(f"Invalid option ID {first_option_id_str} submitted.")
        
        question_info = answer_map[first_option_id_str]
        question_id = question_info['question_id']
        question_score = question_info['question_score']
        question_type = question_info['question_type']

        correct_option_ids = {
            int(opt_id) for opt_id, info in answer_map.items() 
            if info.get('question_id') == question_id and info.get('is_correct') is True
        }

        score_awarded = 0
        is_correct = False
        submitted_option_ids = set(answer_in.selected_option_ids)

        # --- 核心修正：计分逻辑 ---
        if question_type == 'MULTIPLE_CHOICE':
            # 1. 检查是否有错选：提交的答案中，是否有不属于正确答案的选项
            if not submitted_option_ids.issubset(correct_option_ids):
                score_awarded = 0  # 只要有错选，一分不得
                is_correct = False
            # 2. 如果没有错选，再判断是否全对或少选
            else:
                if submitted_option_ids == correct_option_ids:
                    score_awarded = question_score # 全对，得满分
                    is_correct = True
                else:
                    # 少选，按比例递减计分 (例如：得一半分数)
                    # 您可以自定义更复杂的计分规则
                    score_awarded = round(question_score / 2) 
                    is_correct = False # 即使得分，也不算完全正确
        
        elif question_type == 'SINGLE_CHOICE':
            if submitted_option_ids == correct_option_ids:
                score_awarded = question_score
                is_correct = True
            # 单选题答错，score_awarded 保持为 0, is_correct 保持为 False
            
        # --- 记录日志和更新总分的逻辑保持不变 ---
        db_log = AnswerLog(...)
        db.add(db_log)
        result.total_score = (result.total_score or 0) + score_awarded
        db.add(result)
        db.commit()
        db.refresh(result)
        
        return score_awarded, is_correct

crud_answer_log = CRUDAnswerLog(AnswerLog)