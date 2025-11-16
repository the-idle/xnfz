# app/crud/crud_blueprint.py (最终、最简化、最正确版本)
from sqlalchemy.orm import Session, subqueryload, joinedload
from app.models.question_management import QuestionBank, Procedure, Question
from app.schemas.examinee import BlueprintProcedure, BlueprintQuestion, BlueprintOption
import json
from typing import List

cache = {} # 简单的内存缓存

def build_assessment_blueprint(db: Session, *, question_bank_id: int) -> List[BlueprintProcedure]:
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

def generate_and_cache_answer_map(db: Session, *, session_id: int, question_bank_id: int):
    answer_map = {}
    questions = db.query(Question).join(Procedure).filter(Procedure.question_bank_id == question_bank_id).options(joinedload(Question.options)).all()
    
    for q in questions:
        for opt in q.options:
            answer_map[str(opt.id)] = {
                "question_id": q.id,
                "procedure_id": q.procedure_id,
                "is_correct": opt.is_correct,
                "question_score": q.score,
                "question_type": q.question_type.value
            }
    cache[f"answer_map:{session_id}"] = json.dumps(answer_map)

def get_cached_answer_map(session_id: int) -> dict | None:
    answer_map_json = cache.get(f"answer_map:{session_id}")
    return json.loads(answer_map_json) if answer_map_json else None