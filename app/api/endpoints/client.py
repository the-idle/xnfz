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

router = APIRouter()

@router.get("/assessments/recent", response_model=UnifiedResponse[schemas.Assessment])
def get_recent_assessment(db: Session = Depends(deps.get_db)):
    assessment = crud_assessment.get_most_recent_active(db=db)
    if not assessment:
        raise HTTPException(status_code=404, detail="No active assessment found.")
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
    session = crud_assessment_result.get_active_session(db=db, assessment_id=assessment_id, examinee_id=examinee.id)

    if not session:
        session = AssessmentResult(assessment_id=assessment_id, examinee_id=examinee.id, start_time=datetime.utcnow())
        db.add(session); db.commit(); db.refresh(session)
        # generate_and_cache_answer_map(db=db, session_id=session.id, question_bank_id=assessment.question_bank_id)

    blueprint = build_assessment_blueprint(db=db, question_bank_id=assessment.question_bank_id)
    answered_ids = crud_assessment_result.get_answered_question_ids(db=db, result_id=session.id)
    
    blueprint_to_return = blueprint
    if answered_ids:
        filtered_procedures = []
        for proc in blueprint:
            remaining_questions = [q for q in proc.questions if q.id not in answered_ids]
            if remaining_questions:
                filtered_procedures.append(BlueprintProcedure(id=proc.id, name=proc.name, questions=remaining_questions))
        blueprint_to_return = filtered_procedures

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