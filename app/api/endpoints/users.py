# app/api/endpoints/users.py (完整版)
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import schemas, crud
from app.api import deps
from app.models import user_management as user_models
from app.schemas.response import UnifiedResponse
from app.core.security import verify_password
from app.crud.crud_user import crud_user

router = APIRouter()

@router.post("/", response_model=UnifiedResponse[schemas.User], status_code=201)
def create_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.UserCreate,
    current_user: user_models.User = Depends(deps.get_current_active_superuser)
):
    user = crud_user.get_by_username(db, username=user_in.username)
    if user:
        raise HTTPException(status_code=409, detail="Username already registered.")
    user = crud_user.create(db=db, obj_in=user_in)
    return {"data": user}

@router.get("/", response_model=UnifiedResponse[List[schemas.User]])
def read_users(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: user_models.User = Depends(deps.get_current_active_superuser)
):
    users = crud_user.get_multi(db, skip=skip, limit=limit)
    return {"data": users}

@router.get("/{user_id}", response_model=UnifiedResponse[schemas.User])
def read_user_by_id(
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_user: user_models.User = Depends(deps.get_current_active_superuser)
):
    user = crud_user.get(db=db, id=user_id) 
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return {"data": user}

@router.put("/{user_id}", response_model=UnifiedResponse[schemas.User])
def update_user(
    user_id: int,
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.UserUpdate,
    current_user: user_models.User = Depends(deps.get_current_active_superuser)
):
    user = crud_user.get(db=db, id=user_id) 
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    user = crud_user.update(db=db, db_obj=user, obj_in=user_in) 
    return {"data": user}

@router.delete("/{user_id}", response_model=UnifiedResponse)
def delete_user(
    user_id: int,
    *,
    db: Session = Depends(deps.get_db),
    current_user: user_models.User = Depends(deps.get_current_active_superuser)
):
    user = crud_user.get(db=db, id=user_id) 
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    # (可选) 增加逻辑：不能删除自己
    if current_user.id == user_id:
        raise HTTPException(status_code=403, detail="Superusers cannot delete themselves.")
    crud_user.remove(db=db, id=user_id)
    return {"msg": f"User {user_id} deleted successfully."}