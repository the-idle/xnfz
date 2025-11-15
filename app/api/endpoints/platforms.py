# app/api/endpoints/platforms.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app import schemas
from app.api import deps
from app.models import user_management as user_models

from app.crud.crud_platform import crud_platform 
router = APIRouter()

@router.post("/", response_model=schemas.Platform, status_code=status.HTTP_201_CREATED)
def create_platform(
    *,
    db: Session = Depends(deps.get_db),
    platform_in: schemas.PlatformCreate,
    current_user: user_models.User = Depends(deps.get_current_user)
):
    """
    创建一个新的考核平台 (需要管理员权限)
    - 如果平台名称已存在，会返回 400 错误。
    """
    # --- 新增区块 开始 ---
    # 1. 在创建之前，先检查同名平台是否已存在
    existing_platform = crud_platform.get_by_name(db=db, name=platform_in.name)
    if existing_platform:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Platform with name '{platform_in.name}' already exists.",
        )
    # --- 新增区块 结束 ---

    # 2. 如果不存在，则创建
    platform = crud_platform.create(db=db, obj_in=platform_in)
    return platform


@router.get("/", response_model=List[schemas.Platform])
def read_platforms(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: user_models.User = Depends(deps.get_current_user)
):
    platforms = crud_platform.get_multi(db, skip=skip, limit=limit) # 修正
    return platforms

@router.get("/{platform_id}", response_model=schemas.Platform)
def read_platform_by_id(
    platform_id: int,
    db: Session = Depends(deps.get_db),
    current_user: user_models.User = Depends(deps.get_current_user)
):
    platform = crud_platform.get(db=db, id=platform_id) # 修正 (注意 CRUDBase 中是 id)
    if not platform:
        raise HTTPException(status_code=404, detail="Platform not found")
    return platform

@router.put("/{platform_id}", response_model=schemas.Platform)
def update_platform(
    *,
    db: Session = Depends(deps.get_db),
    platform_id: int,
    platform_in: schemas.PlatformUpdate,
    current_user: user_models.User = Depends(deps.get_current_user)
):
    platform = crud_platform.get(db=db, id=platform_id) # 修正
    if not platform:
        raise HTTPException(status_code=404, detail="Platform not found")
    platform = crud_platform.update(db=db, db_obj=platform, obj_in=platform_in) # 修正
    return platform

@router.delete("/{platform_id}", response_model=schemas.Platform)
def delete_platform(
    *,
    db: Session = Depends(deps.get_db),
    platform_id: int,
    current_user: user_models.User = Depends(deps.get_current_user)
):
    platform = crud_platform.get(db=db, id=platform_id) # 修正
    if not platform:
        raise HTTPException(status_code=404, detail="Platform not found")
    platform = crud_platform.remove(db=db, id=platform_id) # 修正
    return platform