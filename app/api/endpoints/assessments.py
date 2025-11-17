# app/api/endpoints/assessments.py (最终修正版)
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app import schemas

# --- 修正导入语句 ---
# 不再导入整个模块，而是直接从模块中导入我们需要的那个 CRUD 实例
from app.crud.crud_assessment import crud_assessment

from app.api import deps
from app.models import user_management as user_models
from app.schemas.response import UnifiedResponse
router = APIRouter()

@router.post("/", response_model=UnifiedResponse[schemas.Assessment], status_code=status.HTTP_201_CREATED)
def create_assessment(
    *,
    db: Session = Depends(deps.get_db),
    assessment_in: schemas.AssessmentCreate,
    current_user: user_models.User = Depends(deps.get_current_user)
):
    """
    创建一个新的考核场次 (需要管理员权限)，并检查时间冲突。
    """
    # --- 核心修正：将校验逻辑放在正确的文件中 ---
    has_conflict = crud_assessment.check_time_conflict(
        db=db, 
        question_bank_id=assessment_in.question_bank_id,
        start_time=assessment_in.start_time,
        end_time=assessment_in.end_time
    )
    if has_conflict:
        raise HTTPException(
            status_code=409, # 409 Conflict
            detail="An assessment for the same platform and overlapping time already exists."
        )
    # --- 校验结束 ---

    assessment = crud_assessment.create(db=db, obj_in=assessment_in)
    return {"data": assessment}

@router.get("/", response_model=UnifiedResponse[List[schemas.Assessment]]) # 建议返回 Read Schema
def read_assessments(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: user_models.User = Depends(deps.get_current_user)
):
    """
    获取考核场次列表 (需要管理员权限)
    """
    assessments = crud_assessment.get_multi(db, skip=skip, limit=limit) # 修正
    return {"data": assessments}


@router.get("/{assessment_id}", response_model=UnifiedResponse[schemas.Assessment]) # 建议返回 Read Schema

def read_assessment_by_id(
    assessment_id: int,
    db: Session = Depends(deps.get_db),
    current_user: user_models.User = Depends(deps.get_current_user)
):
    """
    通过 ID 获取单个考核场次 (需要管理员权限)
    """
    assessment = crud_assessment.get(db=db, id=assessment_id) # 修正
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return {"data": assessment}

@router.put("/{assessment_id}", response_model=UnifiedResponse[schemas.Assessment]) # 建议返回 Read Schema
def update_assessment(
    *,
    db: Session = Depends(deps.get_db),
    assessment_id: int,
    assessment_in: schemas.AssessmentUpdate,
    current_user: user_models.User = Depends(deps.get_current_user)
):
    """
    更新一个考核场次 (需要管理员权限)
    """
    assessment = crud_assessment.get(db=db, id=assessment_id) # 修正
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    assessment = crud_assessment.update(db=db, db_obj=assessment, obj_in=assessment_in) # 修正
    return {"data": assessment}

@router.delete("/{assessment_id}", response_model=UnifiedResponse[schemas.Assessment]) # 建议返回 Read Schema
def delete_assessment(
    *,
    db: Session = Depends(deps.get_db),
    assessment_id: int,
    current_user: user_models.User = Depends(deps.get_current_user)
):
    """
    删除一个考核场-次 (需要管理员权限)
    """
    assessment = crud_assessment.get(db=db, id=assessment_id) # 修正
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    assessment = crud_assessment.remove(db=db, id=assessment_id) # 修正
    return {"data": assessment}
    # return {"msg": "已成功删除 考核场次."}
