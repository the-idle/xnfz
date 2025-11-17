# app/api/endpoints/login.py
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api import deps
from app.models import user_management as user_models
from app import schemas
from app import crud
from app.core import security
from app.db.session import get_db
from app.schemas.response import UnifiedResponse

router = APIRouter()

@router.post("/login/token", response_model=UnifiedResponse[schemas.Token])
def login_for_access_token(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    OAuth2-compatible token login, get an access token for future requests
    """
    user = crud.crud_user.get_user_by_username(db, username=form_data.username)
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=400,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=security.settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        subject=user.username, expires_delta=access_token_expires
    )
    return {"data": {"access_token": access_token, "token_type": "bearer"}}




@router.post("/login/test-token", response_model=UnifiedResponse[schemas.User])

def test_token(current_user: user_models.User = Depends(deps.get_current_user)):
    """
    Test access token
    """
    return {"data": current_user}