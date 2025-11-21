# app/api/endpoints/questions.py (更新后)
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import schemas
from app.api import deps
from app.models import user_management as user_models
from app.crud.crud_question import crud_question
from app.crud.crud_procedure import crud_procedure
from app.schemas.response import UnifiedResponse
from fastapi import Form, File, UploadFile
from pathlib import Path
import json
from datetime import datetime
import shutil
from typing import Optional
from fastapi.responses import FileResponse
from typing import List



router = APIRouter()

UPLOAD_DIR = Path("static/images")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/", response_model=UnifiedResponse[schemas.Question], status_code=status.HTTP_201_CREATED)
def create_question_with_optional_image( # <--- 函数名可以更通用
    procedure_id: int,
    *,
    db: Session = Depends(deps.get_db),
    # --- 核心修改：使用 Form(...) 来接收 JSON 字符串 ---
    question_data: str = Form(...),
    # --- 核心修改：使用 File(...) 来接收可选的图片文件 ---
    image_file: Optional[UploadFile] = File(None),
    current_user: user_models.User = Depends(deps.get_current_user)
):
    """
    为指定工序/点位创建一个新的题目（包含选项和可选的图片）。
    
    - **question_data**: 一个 JSON 字符串，其结构必须符合 QuestionCreate schema。
    - **image_file**: (可选) 一个图片文件。
    """
    # 1. 解析 JSON 字符串为 Pydantic 模型
    try:
        question_in = schemas.QuestionCreate.model_validate_json(question_data)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format for question_data.")
        
    # 2. 检查父级工序和 scene_identifier 是否重复 (逻辑不变)
    procedure = crud_procedure.get(db=db, id=procedure_id)
    if not procedure:
        raise HTTPException(status_code=404, detail="Parent procedure not found")

    existing_question = crud_question.get_by_scene_identifier(db=db, scene_identifier=question_in.scene_identifier)
    if existing_question:
        raise HTTPException(status_code=400, detail=f"Question with scene_identifier '{question_in.scene_identifier}' already exists.")

    # 3. 处理图片上传 (如果提供了文件)
    image_url_to_save = None
    if image_file:
        if image_file.content_type not in ["image/jpeg", "image/png", "image/gif"]:
            raise HTTPException(status_code=400, detail="Invalid image type.")
        
        try:
            file_path = UPLOAD_DIR / f"{datetime.utcnow().timestamp()}_{image_file.filename}"
            with file_path.open("wb") as buffer:
                shutil.copyfileobj(image_file.file, buffer)
            
            # 保存相对路径到数据库
            image_url_to_save = f"/{file_path}"
        finally:
            image_file.file.close()

    # 4. 调用 CRUD 函数创建题目
    # 注意：我们将 image_url 覆盖到 Pydantic 模型中
    question_in.image_url = image_url_to_save.replace("\\", "/")
    
    question = crud_question.create_with_options(
        db=db, obj_in=question_in, procedure_id=procedure_id
    )
    return {"data": question}

@router.get("/", response_model=UnifiedResponse[List[schemas.Question]])
def read_questions(
    procedure_id: int,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: user_models.User = Depends(deps.get_current_user)
):
    """
    根据工序/点位 ID 分页获取题目列表。 
    """
    questions = crud_question.get_multi_by_procedure(db=db, procedure_id=procedure_id, skip=skip, limit=limit)
    return {"data": questions}

@router.get("/{question_id}", response_model=UnifiedResponse[schemas.Question])
def read_question(
    question_id: int,
    db: Session = Depends(deps.get_db),
    current_user: user_models.User = Depends(deps.get_current_user)
):
    """
    根据题目 ID 获取单个题目详情。
    """
    question = crud_question.get(db=db, id=question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return {"data": question}

@router.put("/{question_id}", response_model=UnifiedResponse[schemas.Question])
def update_question(
    question_id: int,
    *,
    db: Session = Depends(deps.get_db),
    question_data: str = Form(...),
    image_file: Optional[UploadFile] = File(None),
    current_user: user_models.User = Depends(deps.get_current_user)
):
    """
    更新题目信息，支持可选图片上传。
    若提供新图片，旧图片将被替换。
    """
    question = crud_question.get(db=db, id=question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    # 解析 JSON
    try:
        question_in = schemas.QuestionUpdate.model_validate_json(question_data)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format for question_data.")

    # 处理图片上传
    image_url_to_save = question.image_url  # 默认保留原图
    if image_file:
        if image_file.content_type not in ["image/jpeg", "image/png", "image/gif"]:
            raise HTTPException(status_code=400, detail="Invalid image type.")
        try:
            file_path = UPLOAD_DIR / f"{datetime.utcnow().timestamp()}_{image_file.filename}"
            with file_path.open("wb") as buffer:
                shutil.copyfileobj(image_file.file, buffer)
            image_url_to_save = f"/{file_path}"
        finally:
            image_file.file.close()

    question_in.image_url = image_url_to_save
    updated_question = crud_question.update(db=db, db_obj=question, obj_in=question_in)
    return {"data": updated_question}

@router.delete("/{question_id}", response_model=UnifiedResponse[schemas.Question])
def delete_question(
    question_id: int,
    db: Session = Depends(deps.get_db),
    current_user: user_models.User = Depends(deps.get_current_user)
):
    """
    删除指定题目。
    """
    question = crud_question.get(db=db, id=question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    removed_question = crud_question.remove(db=db, id=question_id)
    return {"data": removed_question}

