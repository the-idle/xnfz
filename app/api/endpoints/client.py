# app/api/endpoints/client.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime,timezone 

from app import schemas
from app.api import deps
from app.api import deps
from app.crud.crud_assessment_result import crud_assessment_result
from app.crud.crud_examinee import crud_examinee
from app.crud.crud_assessment import crud_assessment
from app.crud.crud_answer_log import crud_answer_log
from app.crud.crud_question import crud_question
from app.crud.crud_blueprint import (
    build_assessment_blueprint,
    generate_and_cache_answer_map,
    get_cached_answer_map
)
from app.models.assessment_management import AssessmentResult
from app.models.question_management import Question 
from app.schemas.examinee import BlueprintProcedure
from app.schemas.response import UnifiedResponse


router = APIRouter()

@router.get("/assessments/recent", response_model=UnifiedResponse[schemas.Assessment])
def get_recent_assessment(db: Session = Depends(deps.get_db)):
    """
    获取当前正在进行中，且最近开始的一场考核。
    供 Unity 客户端启动时自动查询。
    """
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
        db.add(session)
        db.commit(); db.refresh(session)
        generate_and_cache_answer_map(db=db, session_id=session.id, question_bank_id=assessment.question_bank_id)

    blueprint = build_assessment_blueprint(db=db, question_bank_id=assessment.question_bank_id)
    answered_ids = crud_assessment_result.get_answered_question_ids(db=db, result_id=session.id)
    
    if answered_ids:
        filtered_procedures = []
        for proc in blueprint:
            remaining_questions = [q for q in proc.questions if q.id not in answered_ids]
            if remaining_questions:
                filtered_procedures.append(BlueprintProcedure(id=proc.id, name=proc.name, questions=remaining_questions))
        blueprint_to_return = filtered_procedures
    else:
        blueprint_to_return = blueprint

    return {"data": {"assessment_result_id": session.id, "procedures": blueprint_to_return}}


@router.post("/assessment-results/{result_id}/answer", response_model=UnifiedResponse[schemas.SubmitAnswerResponse])
def submit_answer(result_id: int, *, db: Session = Depends(deps.get_db), answer_in: schemas.SubmitAnswerRequest):
    result = crud_assessment_result.get(db=db, id=result_id)
    if not result or result.end_time: raise HTTPException(status_code=404, detail="Session not found or already finished")

    examinee = crud_examinee.get(db=db, id=result.examinee_id)
    if not examinee or examinee.identifier != answer_in.examinee_identifier: raise HTTPException(status_code=403, detail="Examinee identifier mismatch.")

    answer_map = get_cached_answer_map(result_id)
    if not answer_map: raise HTTPException(status_code=500, detail="Cache lost. Please restart session.")
    
    answered_ids = crud_assessment_result.get_answered_question_ids(db=db, result_id=result_id)
    if answer_in.question_id in answered_ids: raise HTTPException(status_code=400, detail="Question already answered.")

    try:
        score_awarded, is_correct = crud_answer_log.calculate_and_log_answer(db=db, result=result, answer_in=answer_in, answer_map=answer_map)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
        
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


