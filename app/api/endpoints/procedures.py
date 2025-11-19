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