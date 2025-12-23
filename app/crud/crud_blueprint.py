# app/crud/crud_blueprint.py (最终、最简化、最正确版本)
from sqlalchemy.orm import Session, subqueryload, joinedload
from app.models.question_management import QuestionBank, Procedure, Question
from app.schemas.examinee import BlueprintProcedure, BlueprintQuestion, BlueprintOption
from app.core.cache import cache_service
import logging
from typing import List

logger = logging.getLogger(__name__)


def build_assessment_blueprint(db: Session, *, question_bank_id: int) -> List[BlueprintProcedure]:
    """
    构建结构化的考核蓝图。
    优先从 Redis 缓存获取，缓存未命中时从数据库查询并缓存结果。
    """
    # 1. 尝试从缓存获取
    cached_data = cache_service.get_blueprint(question_bank_id)
    if cached_data:
        logger.debug(f"从缓存获取题库蓝图: {question_bank_id}")
        # 将缓存的字典数据转换回 Pydantic 模型
        return [BlueprintProcedure(**proc) for proc in cached_data]

    # 2. 缓存未命中，从数据库查询
    logger.debug(f"缓存未命中，从数据库查询题库蓝图: {question_bank_id}")
    bank = (
        db.query(QuestionBank)
        .options(
            subqueryload(QuestionBank.procedures)
            .subqueryload(Procedure.questions)
            .joinedload(Question.options)
        )
        .filter(QuestionBank.id == question_bank_id).first()
    )
    if not bank:
        return []

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

    # 3. 将结果写入缓存
    if procedures:
        cache_service.set_blueprint(question_bank_id, procedures)
        logger.debug(f"题库蓝图已缓存: {question_bank_id}")

    return procedures


def invalidate_blueprint_cache(question_bank_id: int) -> bool:
    """
    使题库蓝图缓存失效
    在题库、工序、题目发生变更时调用
    """
    logger.info(f"使题库蓝图缓存失效: {question_bank_id}")
    return cache_service.invalidate_blueprint(question_bank_id)
