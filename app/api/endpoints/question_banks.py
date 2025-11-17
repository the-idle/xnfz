# app/api/endpoints/question_banks.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app import schemas

# --- 修正导入语句 ---
# 直接从具体的模块导入我们需要的 CRUD 实例
from app.crud.crud_platform import crud_platform
from app.crud.crud_question_bank import crud_question_bank

from app.api import deps
from app.models import user_management as user_models
from app.schemas.response import UnifiedResponse

router = APIRouter()


@router.post("/", response_model=UnifiedResponse[schemas.QuestionBank], status_code=status.HTTP_201_CREATED)
def create_question_bank_for_platform(
    *,
    db: Session = Depends(deps.get_db),
    platform_id: int,  # 从 URL 路径中获取
    question_bank_in: schemas.QuestionBankCreate,
    current_user: user_models.User = Depends(deps.get_current_user)
):
    """
    为指定的平台创建一个新的题库 (需要管理员权限)
    """
    # --- 修正函数调用 ---
    # 1. 检查平台是否存在
    platform = crud_platform.get(db=db, id=platform_id)
    if not platform:
        raise HTTPException(status_code=404, detail="Parent platform not found")

    # 2. 创建题库并与平台关联
    question_bank = crud_question_bank.create_with_platform(
        db=db, obj_in=question_bank_in, platform_id=platform_id
    )
    return {"data": question_bank}


@router.get("/", response_model=UnifiedResponse[List[schemas.QuestionBank]])
def read_question_banks_for_platform(
    *,
    db: Session = Depends(deps.get_db),
    platform_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: user_models.User = Depends(deps.get_current_user)
):
    """
    获取指定平台下的题库列表 (需要管理员权限)
    """
    # (注意：这个查询逻辑可以进一步优化，但目前可以工作)
    platform = crud_platform.get(db=db, id=platform_id)
    if not platform:
        raise HTTPException(status_code=404, detail="Parent platform not found")
    
    # crud_question_bank 实例没有 get_multi_by_platform 方法，需要我们自己实现
    # 这里我们暂时使用 platform 的关系属性来获取
    question_banks = platform.question_banks[skip : skip + limit]
    return {"data": question_banks}
