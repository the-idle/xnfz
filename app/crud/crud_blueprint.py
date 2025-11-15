# app/crud/crud_blueprint.py
from sqlalchemy.orm import Session, subqueryload, joinedload
from app.models.question_management import QuestionBank, Procedure, Question, Option
from datetime import datetime
import json
from redis import Redis # 假设使用 Redis 缓存

# 模拟一个缓存（实际项目中应使用 Redis 或类似工具）
blueprint_cache = {}

def generate_answer_map_and_blueprint(db: Session, *, question_bank_id: int):
    """
    构建结构化的考核蓝图，并生成一个 answer_id -> option_id 的映射
    """
    bank = (
        db.query(QuestionBank)
        .options(
            subqueryload(QuestionBank.procedures)
            .subqueryload(Procedure.questions)
            .joinedload(Question.options)
        )
        .filter(QuestionBank.id == question_bank_id)
        .first()
    )

    if not bank:
        return [], {}

    blueprint_procedures = []
    answer_map = {}
    answer_id_counter = 1

    sorted_procedures = sorted(bank.procedures, key=lambda p: p.id)

    for proc in sorted_procedures:
        blueprint_questions = []
        sorted_questions = sorted(proc.questions, key=lambda q: q.id)
        
        for q in sorted_questions:
            blueprint_options = []
            for opt in q.options:
                answer_map[answer_id_counter] = {
                    "option_id": opt.id,
                    "question_id": q.id,
                    "is_correct": opt.is_correct
                }
                blueprint_options.append({
                    "answer_id": answer_id_counter,
                    "option_text": opt.option_text,
                })
                answer_id_counter += 1
            
            blueprint_questions.append({
                "question_id": q.id,
                "scene_identifier": q.scene_identifier,
                "prompt": q.prompt,
                "question_type": q.question_type.value,
                "score": q.score,
                "image_url": q.image_url,
                "options": blueprint_options,
            })
        
        blueprint_procedures.append({
            "procedure_id": proc.id,
            "procedure_name": proc.name,
            "questions": blueprint_questions,
        })
        
    return blueprint_procedures, answer_map

def cache_blueprint_and_map(session_id: int, blueprint: list, answer_map: dict):
    """
    将蓝图和答案映射缓存起来（实际应使用 Redis）
    """
    # 使用简单的字典模拟 Redis
    blueprint_cache[f"blueprint:{session_id}"] = json.dumps(blueprint)
    blueprint_cache[f"answer_map:{session_id}"] = json.dumps(answer_map)

def get_cached_answer_map(session_id: int):
    """
    从缓存中获取答案映射
    """
    answer_map_json = blueprint_cache.get(f"answer_map:{session_id}")
    return json.loads(answer_map_json) if answer_map_json else None