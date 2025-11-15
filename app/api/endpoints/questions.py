# app/api/endpoints/questions.py (更新后)
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import schemas
from app.api import deps
from app.models import user_management as user_models
from app.crud.crud_question import crud_question
from app.crud.crud_procedure import crud_procedure

router = APIRouter()

@router.post("/", response_model=schemas.Question, status_code=status.HTTP_201_CREATED)
def create_question_for_procedure( # <--- 函数名可以更通用
    procedure_id: int, # <--- 修改
    *,
    db: Session = Depends(deps.get_db),
    question_in: schemas.QuestionCreate,
    current_user: user_models.User = Depends(deps.get_current_user)
):
    """
    为指定工序/点位创建一个新的题目（包含选项）
    """
    # 检查父级工序是否存在
    procedure = crud_procedure.get(db=db, id=procedure_id) # <--- 修改
    if not procedure:
        raise HTTPException(status_code=404, detail="Parent procedure not found")

    existing_question = crud_question.get_by_scene_identifier(db=db, scene_identifier=question_in.scene_identifier)
    if existing_question:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Question with scene_identifier '{question_in.scene_identifier}' already exists.",
        )
        
    question = crud_question.create_with_options(
        db=db, obj_in=question_in, procedure_id=procedure_id # <--- 修改
    )
    return question