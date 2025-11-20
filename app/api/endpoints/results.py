# app/api/endpoints/results.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app import schemas
from app.api import deps
from app.models import user_management as user_models
from app.crud.crud_assessment_result import crud_assessment_result
from app.schemas.response import UnifiedResponse
from fastapi import HTTPException
from app.models.assessment_management import AssessmentResult
from sqlalchemy.orm import selectinload

router = APIRouter()

@router.get(
    "/assessments/{assessment_id}/results/",
    response_model=UnifiedResponse[List[schemas.AssessmentResultDetail]]
)
def read_assessment_results(
    assessment_id: int,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: user_models.User = Depends(deps.get_current_user)
):
    """
    获取一场考核的所有考生成绩详情 (需要管理员权限)
    """
    results = crud_assessment_result.get_multi_by_assessment(
        db=db, assessment_id=assessment_id, skip=skip, limit=limit
    )
    
    # 手动组装数据以匹配 AssessmentResultDetail schema
    detailed_results = []
    for res in results:
        detailed_results.append({
            "id": res.id,
            "total_score": res.total_score,
            "start_time": res.start_time,
            "end_time": res.end_time,
            "examinee_identifier": res.examinee.identifier,
            "answer_logs": res.answer_logs
        })

    return {"data": detailed_results}

@router.get(
    "/{result_id}",
    response_model=UnifiedResponse[schemas.AssessmentResultDetail]
)
def read_single_assessment_result(
    result_id: int,
    db: Session = Depends(deps.get_db),
    current_user: user_models.User = Depends(deps.get_current_user)
):
    """
    根据ID获取单次考核详情
    """
    # 核心：使用 selectinload 预加载关联数据，提高效率
    result = (
        db.query(AssessmentResult)
        .options(
            selectinload(AssessmentResult.examinee),
            selectinload(AssessmentResult.answer_logs)
        )
        .filter(AssessmentResult.id == result_id)
        .first()
    )
    
    if not result:
        raise HTTPException(status_code=404, detail="Assessment result not found")
    
    # --- 手动组装数据以确保 selected_option_ids 被正确解析 ---
    answer_logs_details = []
    for log in result.answer_logs:
        selected_ids = []
        # 增加健壮性检查，确保数据能被正确解析
        if isinstance(log.selected_option_ids, list):
            selected_ids = log.selected_option_ids
        elif isinstance(log.selected_option_ids, str):
            try:
                selected_ids = json.loads(log.selected_option_ids)
            except:
                pass # 解析失败则返回空列表

        answer_logs_details.append({
            "question_id": log.question_id,
            "score_awarded": log.score_awarded,
            "answered_at": log.answered_at,
            "selected_option_ids": selected_ids
        })

    detailed_result = {
        "id": result.id,
        "total_score": result.total_score,
        "start_time": result.start_time,
        "end_time": result.end_time,
        "examinee_identifier": result.examinee.identifier if result.examinee else "Unknown",
        "answer_logs": answer_logs_details
    }
    
    return {"data": detailed_result}