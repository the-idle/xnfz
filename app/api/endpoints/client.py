# app/api/endpoints/client.py (最终修复与增强版)
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app import schemas
from app.api import deps
from app.crud.crud_assessment import crud_assessment
from app.crud.crud_examinee import crud_examinee
from app.crud.crud_assessment_result import crud_assessment_result
from app.crud.crud_answer_log import crud_answer_log


from app.crud.crud_blueprint import build_assessment_blueprint
from app.models.assessment_management import AssessmentResult
from app.schemas.examinee import BlueprintProcedure
from app.schemas.response import UnifiedResponse # 导入统一响应模型
from app.models.assessment_management import AnswerLog


router = APIRouter()

# @router.get("/assessments/recent", response_model=UnifiedResponse[schemas.Assessment])
# def get_recent_assessment(db: Session = Depends(deps.get_db)):
#     assessment = crud_assessment.get_most_recent_active(db=db)
#     if not assessment:
#         raise HTTPException(status_code=404, detail="No active assessment found.")
#     return {"data": assessment}
@router.get("/platforms/{platform_id}/assessments/upcoming", response_model=UnifiedResponse[schemas.Assessment])
def get_upcoming_assessment_for_platform(
    platform_id: int, # <--- 接收 platform_id
    db: Session = Depends(deps.get_db)
):
    """
    为指定平台获取最优先的（即将开始或正在进行的）一场考核。
    """
    assessment = crud_assessment.get_upcoming_or_active(db=db, platform_id=platform_id)
    if not assessment:
        raise HTTPException(status_code=404, detail="No upcoming or active assessment found for this platform.")
    return {"data": assessment}

@router.post("/assessments/{assessment_id}/session", response_model=UnifiedResponse[schemas.AssessmentBlueprintResponse])
def start_or_resume_assessment_session(assessment_id: int, *, db: Session = Depends(deps.get_db), start_request: schemas.AssessmentStartRequest):
    assessment = crud_assessment.get(db=db, id=assessment_id)
    if not assessment: raise HTTPException(status_code=404, detail="Assessment not found")

    now_utc = datetime.now(timezone.utc)
    start_time_utc = assessment.start_time.replace(tzinfo=timezone.utc)
    end_time_utc = assessment.end_time.replace(tzinfo=timezone.utc)
    if now_utc < start_time_utc: raise HTTPException(status_code=403, detail="Assessment has not started yet.")
    if now_utc > end_time_utc: raise HTTPException(status_code=403, detail="Assessment has already ended.")

    examinee = crud_examinee.get_or_create_by_identifier(db=db, identifier=start_request.examinee_identifier)

        # --- 核心增强：前置检查 ---
    # 1. 检查该考生是否已经完成过这场考核
    finished_session = crud_assessment_result.get_finished_session(
        db=db, assessment_id=assessment_id, examinee_id=examinee.id
    )
    if finished_session:
        raise HTTPException(
            status_code=403, # 403 Forbidden
            detail="You have already completed and submitted this assessment."
        )

    # --- 核心修复点 1: 创建新会话 ---
    session = crud_assessment_result.get_active_session(db=db, assessment_id=assessment_id, examinee_id=examinee.id)

    if not session:
        session = AssessmentResult(assessment_id=assessment_id, examinee_id=examinee.id, start_time=datetime.utcnow())
        db.add(session); db.commit(); db.refresh(session)
        # (可选) 如果您有缓存逻辑，应该在这里为新会hs话触发
        # generate_and_cache_answer_map(db=db, session_id=session.id, question_bank_id=assessment.question_bank_id)

    # --- 2. 获取数据 (保持不变) ---
    full_blueprint = build_assessment_blueprint(db=db, question_bank_id=assessment.question_bank_id)
    # 关键：获取已回答题目的详细日志映射 {question_id: [selected_ids]}
    answered_logs_map = crud_assessment_result.get_answered_logs_map(db=db, result_id=session.id)
    answered_question_ids = set(answered_logs_map.keys())
    
    # --- 3. 【核心修复】二次加工蓝图，注入已选答案 ---
    blueprint_to_return = []
    for proc in full_blueprint:
        
        question_ids_in_proc = {q.id for q in proc.questions}
        
        # a. 如果工序已完成，则过滤掉
        if question_ids_in_proc.issubset(answered_question_ids):
            continue

        # b. 如果工序未完成，则处理其下的题目，注入已选答案
        processed_questions = []
        for question in proc.questions:
            # 将 Pydantic 模型转为字典以便修改
            question_data = question.model_dump()
            
            # 关键：如果题目已回答，就从 map 中获取答案并注入
            if question.id in answered_logs_map:
                question_data['selected_option_ids'] = answered_logs_map[question.id]['selected_option_ids']
                question_data['score_awarded'] = answered_logs_map[question.id]['score_awarded']

            processed_questions.append(question_data)

        # d. 创建一个新的工序对象，包含处理过的题目列表
        filtered_proc = BlueprintProcedure(
            id=proc.id,
            name=proc.name,
            questions=processed_questions
        )
        blueprint_to_return.append(filtered_proc)

        
    # --- 4. 返回最终结果 ---
    return {"data": {"assessment_result_id": session.id, "procedures": blueprint_to_return}}

@router.post("/assessment-results/{result_id}/answer", response_model=UnifiedResponse[schemas.SubmitAnswerResponse])
def submit_answer(result_id: int, *, db: Session = Depends(deps.get_db), answer_in: schemas.SubmitAnswerRequest):
    result = crud_assessment_result.get(db=db, id=result_id)
    if not result or result.end_time: raise HTTPException(status_code=404, detail="Session not found or already finished")

    # --- 新增：提交答案时间校验 ---
    assessment = crud_assessment.get(db=db, id=result.assessment_id)
    now_utc = datetime.now(timezone.utc)
    end_time_utc = assessment.end_time.replace(tzinfo=timezone.utc)
    if now_utc > end_time_utc: raise HTTPException(status_code=403, detail="Assessment has already ended. Cannot submit answer.")

    examinee = crud_examinee.get(db=db, id=result.examinee_id)
    if not examinee or examinee.identifier != answer_in.examinee_identifier: raise HTTPException(status_code=403, detail="Examinee identifier mismatch.")

    # --- 关键修复：重复提交校验 ---
    answered_ids = crud_assessment_result.get_answered_question_ids(db=db, result_id=result_id)
    if answer_in.question_id in answered_ids:
        raise HTTPException(status_code=400, detail="Question has already been answered.")

    # answer_map = get_cached_answer_map(result_id)
    # if not answer_map: raise HTTPException(status_code=500, detail="Cache lost. Please restart session.")
    
    # --- 关键修复：将所有计分和日志逻辑委托给 CRUD 层 ---
    try:
        # 直接调用正确的方法，它会处理所有事情：校验、计分、记录日志、更新分数和提交
        score_awarded, is_correct = crud_answer_log.calculate_and_log_answer(
            db=db, result=result, answer_in=answer_in
        )

    except ValueError as e:
        # 如果 calculate_and_log_answer 内部抛出 ValueError (例如问题不存在)，则捕获并返回400错误
        raise HTTPException(status_code=400, detail=str(e))
    
    # 成功后直接返回结果
    return {"data": {"status": "success", "score_awarded": score_awarded, "is_correct": is_correct}}

@router.post("/assessment-results/{result_id}/finish", response_model=UnifiedResponse)
def finish_assessment(result_id: int, *, db: Session = Depends(deps.get_db), finish_request: schemas.FinishAssessmentRequest):
    result = crud_assessment_result.get(db=db, id=result_id)
    if not result: raise HTTPException(status_code=404, detail="Session not found")
    
    examinee = crud_examinee.get(db=db, id=result.examinee_id)
    if not examinee or examinee.identifier != finish_request.examinee_identifier: raise HTTPException(status_code=403, detail="Examinee identifier mismatch.")

    if result.end_time: raise HTTPException(status_code=400, detail="Assessment has already been finished.")
        
    result.end_time = datetime.utcnow()
    db.add(result); db.commit()
    return {"data": {"status": "finished", "final_score": result.total_score}}