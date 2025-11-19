# app/api/endpoints/results.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app import schemas
from app.api import deps
from app.models import user_management as user_models
from app.crud.crud_assessment_result import crud_assessment_result
from app.schemas.response import UnifiedResponse

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