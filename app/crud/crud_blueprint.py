# app/crud/crud_blueprint.py (最终、最简化、最正确版本)
from sqlalchemy.orm import Session, subqueryload, joinedload
from app.models.question_management import QuestionBank, Procedure, Question
from app.schemas.examinee import BlueprintProcedure, BlueprintQuestion, BlueprintOption
import json
from typing import List

cache = {} # 简单的内存缓存

def build_assessment_blueprint(db: Session, *, question_bank_id: int) -> List[BlueprintProcedure]:
    """
    构建结构化的考核蓝图。这是此文件唯一的职责。
    """
    bank = (
        db.query(QuestionBank)
        .options(
            subqueryload(QuestionBank.procedures)
            .subqueryload(Procedure.questions)
            .joinedload(Question.options)
        )
        .filter(QuestionBank.id == question_bank_id).first()
    )
    if not bank: return []

    procedures = []
    for proc in sorted(bank.procedures, key=lambda p: p.id):
        questions = []
        for q in sorted(proc.questions, key=lambda q: q.id):
            options = [BlueprintOption(id=opt.id, option_text=opt.option_text) for opt in q.options]
            questions.append(BlueprintQuestion(
                id=q.id, scene_identifier=q.scene_identifier, prompt=q.prompt,
                question_type=q.question_type.value, score=q.score, image_url=q.image_url, options=options
            ))
        procedures.append(BlueprintProcedure(id=proc.id, name=proc.name, questions=questions))
    return procedures

