# app/crud/crud_answer_log.py (最终修复版)
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Tuple

from app.crud.base import CRUDBase
from app.models.assessment_management import AnswerLog, AssessmentResult
from app.models.question_management import Question
from sqlalchemy.orm import joinedload

from app.schemas.examinee import SubmitAnswerRequest
from pydantic import BaseModel

class CRUDAnswerLog(CRUDBase[AnswerLog, SubmitAnswerRequest, BaseModel]):
    def calculate_and_log_answer(
        self, db: Session, *, result: AssessmentResult, answer_in: SubmitAnswerRequest
    ) -> Tuple[int, bool]:
        print("\n--- [DEBUG] ENTERING calculate_and_log_answer ---")
        
        question = (
            db.query(Question).options(joinedload(Question.options))
            .filter(Question.id == answer_in.question_id).first()
        )
        if not question: raise ValueError(f"Question with id {answer_in.question_id} not found.")
        if question.procedure_id != answer_in.procedure_id: raise ValueError("Procedure ID mismatch.")
            
        correct_option_ids = {opt.id for opt in question.options if opt.is_correct}
        
        print(f"[DEBUG] Type of question.question_type: {type(question.question_type)}")
        print(f"[DEBUG] Value of question.question_type: {question.question_type.value}")
        
        score_awarded = 0
        is_correct = False
        submitted_option_ids = set(answer_in.selected_option_ids)

        # --- 终极核心修正：将比较字符串改为小写 ---
        # --- 升级计分逻辑 ---
        if question.question_type.value == 'deduction_single_choice':
            if submitted_option_ids == correct_option_ids:
                score_awarded = 0 # 答对不得分
                is_correct = True
            else:
                score_awarded = -question.score # 答错，扣除该题的全部分值
                is_correct = False

        elif question.question_type.value == 'single_choice': # <--- 修正为小写！
            print(f"[DEBUG] SINGLE_CHOICE: Comparing {submitted_option_ids} == {correct_option_ids}")
            if submitted_option_ids == correct_option_ids:
                score_awarded = question.score
                is_correct = True
                
        elif question.question_type.value == 'multiple_choice': # <--- 修正为小写！
            print(f"[DEBUG] MULTIPLE_CHOICE: Checking subset and equality")
            if not submitted_option_ids.issubset(correct_option_ids):
                score_awarded = 0
                is_correct = False
            else:
                if submitted_option_ids == correct_option_ids:
                    score_awarded = question.score
                    is_correct = True
                else:
                    score_awarded = round(question.score / 2)
                    is_correct = False

        print(f"[DEBUG] Final Result: is_correct={is_correct}, score_awarded={score_awarded}")

        db_log = AnswerLog(
            result_id=result.id,
            question_id=answer_in.question_id,
            selected_option_ids=answer_in.selected_option_ids,
            score_awarded=score_awarded,
            answered_at=datetime.utcnow()
        )
        db.add(db_log)
        result.total_score = (result.total_score or 0) + score_awarded
        db.add(result)
        db.commit()
        db.refresh(result)
        
        print("--- [DEBUG] EXITING calculate_and_log_answer ---\n")
        
        return score_awarded, is_correct

crud_answer_log = CRUDAnswerLog(AnswerLog)