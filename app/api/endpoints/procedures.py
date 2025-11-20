# app/api/endpoints/procedures.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app import schemas
from app.api import deps
from app.models import user_management as user_models
from app.crud.crud_procedure import crud_procedure
from app.crud.crud_question_bank import crud_question_bank 
from app.schemas.response import UnifiedResponse
from app.models.question_management import QuestionType

router = APIRouter()

@router.post("/", response_model=UnifiedResponse[schemas.Platform])
def create_procedure_for_bank(
    question_bank_id: int,
    *,
    db: Session = Depends(deps.get_db),
    procedure_in: schemas.ProcedureCreate,
    current_user: user_models.User = Depends(deps.get_current_user)
):
    """
    为指定题库创建一个新的工序/点位
    """
    bank = crud_question_bank.get(db=db, id=question_bank_id)
    if not bank:
        raise HTTPException(status_code=404, detail="Parent question bank not found")
    
    procedure = crud_procedure.create_with_bank(db=db, obj_in=procedure_in, question_bank_id=question_bank_id)
    return {"data": procedure}

# 您可以仿照此模式，轻松补全 get_multi, get, update, delete 接口
@router.get("/", response_model=UnifiedResponse[List[schemas.Procedure]])
def read_procedures(
    question_bank_id: int,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: user_models.User = Depends(deps.get_current_user)
):
    # 需要在 crud_procedure 中添加一个 get_multi_by_bank 方法
    procedures = crud_procedure.get_multi_by_bank(db=db, question_bank_id=question_bank_id, skip=skip, limit=limit)
    return {"data": procedures}

@router.get("/{procedure_id}", response_model=UnifiedResponse[schemas.Procedure])
def read_procedure(
    procedure_id: int,
    db: Session = Depends(deps.get_db),
    current_user: user_models.User = Depends(deps.get_current_user)
):
    # 需要在 crud_procedure 中添加一个 get 方法
    procedure = crud_procedure.get(db=db, id=procedure_id)
    if not procedure:
        raise HTTPException(status_code=404, detail="Procedure not found")
    return {"data": procedure}

# --- 核心修复：Update 接口 ---
@router.put("/{procedure_id}", response_model=UnifiedResponse[schemas.Procedure])
def update_procedure(
    procedure_id: int,
    *,
    db: Session = Depends(deps.get_db),
    procedure_in: schemas.ProcedureUpdate,
    current_user: user_models.User = Depends(deps.get_current_user)
):
    # 1. 先查询是否存在
    procedure = crud_procedure.get(db=db, id=procedure_id)
    if not procedure:
        raise HTTPException(status_code=404, detail="Procedure not found")
    
    # 2. 再执行更新
    procedure = crud_procedure.update(db=db, db_obj=procedure, obj_in=procedure_in)
    return {"data": procedure}

# --- 核心修复：Delete 接口 ---
@router.delete("/{procedure_id}", response_model=UnifiedResponse[schemas.Procedure])
def delete_procedure(
    procedure_id: int,
    db: Session = Depends(deps.get_db),
    current_user: user_models.User = Depends(deps.get_current_user)
):
    # 1. 先查询是否存在
    procedure = crud_procedure.get(db=db, id=procedure_id)
    if not procedure:
        raise HTTPException(status_code=404, detail="Procedure not found")
    
    # 2. 执行删除 (CRUDBase 的方法通常叫 remove)
    crud_procedure.remove(db=db, id=procedure_id)
    return {"data": procedure}