# app/api/endpoints/client.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from app import schemas
from app.api import deps
from app.api import deps
from app.crud.crud_assessment_result import crud_assessment_result
from app.crud.crud_examinee import crud_examinee
from app.crud.crud_assessment import crud_assessment # 现在这个名字明确指向实例
from app.crud.crud_answer_log import crud_answer_log
from app.crud.crud_question import crud_question
from app.crud.crud_blueprint import (
    generate_answer_map_and_blueprint, cache_blueprint_and_map, get_cached_answer_map
)
from app.models.assessment_management import AssessmentResult

router = APIRouter()

@router.post(
    "/assessments/{assessment_id}/session",
    response_model=schemas.AssessmentBlueprintResponse
)
def start_or_resume_assessment_session(
    assessment_id: int,
    *,
    db: Session = Depends(deps.get_db),
    start_request: schemas.AssessmentStartRequest
):
    assessment = crud_assessment.get(db=db, id=assessment_id)
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
        
    examinee = crud_examinee.get_or_create_by_identifier(db=db, identifier=start_request.examinee_identifier)
    session = crud_assessment_result.get_active_session(db=db, assessment_id=assessment_id, examinee_id=examinee.id)
    
    if not session:
        session = AssessmentResult(
            assessment_id=assessment_id,
            examinee_id=examinee.id,
            start_time=datetime.utcnow()
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        
        # 首次开始，生成并缓存蓝图
        blueprint, answer_map = generate_answer_map_and_blueprint(db=db, question_bank_id=assessment.question_bank_id)
        cache_blueprint_and_map(session.id, blueprint, answer_map)
    else:
        # 断点续考，从缓存或其他地方获取蓝图
        # (简化逻辑：此处重新生成。实际项目中应从缓存读取)
        blueprint, _ = generate_answer_map_and_blueprint(db=db, question_bank_id=assessment.question_bank_id)

    # TODO: 断点续考时，应根据 answered_logs 从 blueprint 中移除已回答的问题

    return {
        "assessment_result_id": session.id,
        "procedures": blueprint
    }

@router.post(
    "/assessment-results/{result_id}/answer",
    response_model=schemas.SubmitAnswerResponse
)
def submit_answer(
    result_id: int,
    *,
    db: Session = Depends(deps.get_db),
    answer_in: schemas.SubmitAnswerRequest
):
    result = crud_assessment_result.get(db=db, id=result_id)
    if not result or result.end_time:
        raise HTTPException(status_code=404, detail="Session not found or already finished")

    # 从缓存获取答案映射
    answer_map = get_cached_answer_map(result_id)
    if not answer_map:
        raise HTTPException(status_code=500, detail="Assessment blueprint not found. Please restart the session.")

    # 提交答案的计分逻辑也需要重构
    # (此处省略具体实现，但核心是使用 answer_map 将 answer_id 转换为 option_id 和 question_id)
    
    # 示例简化逻辑
    score_awarded = 0
    is_correct = True
    for answer_id in answer_in.selected_answer_ids:
        if str(answer_id) not in answer_map or not answer_map[str(answer_id)]['is_correct']:
            is_correct = False
            break
    
    if is_correct:
        first_answer_id = str(answer_in.selected_answer_ids[0])
        question_id = answer_map[first_answer_id]['question_id']
        question = crud_question.get(db=db, id=question_id)
        score_awarded = question.score if question else 0

    # TODO: 记录 AnswerLog
    
    return {
        "status": "success",
        "score_awarded": score_awarded,
        "is_correct": is_correct
    }

@router.post("/assessment-results/{result_id}/finish")
def finish_assessment(
    result_id: int,
    db: Session = Depends(deps.get_db)
):
    """
    Unity 客户端：完成并提交整场考核。
    """
    # 1. 查找考核会话
    result = crud_assessment_result.get(db=db, id=result_id)
    if not result:
        raise HTTPException(status_code=404, detail="Assessment session not found")
        
    # 2. 检查考核是否已结束
    if result.end_time:
        raise HTTPException(status_code=400, detail="Assessment has already been finished")
        
    # 3. 更新结束时间并保存
    result.end_time = datetime.utcnow()
    db.add(result)
    db.commit()
    
    # 4. 返回最终结果
    return {"status": "finished", "final_score": result.total_score}