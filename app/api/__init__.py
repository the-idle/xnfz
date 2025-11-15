from fastapi import APIRouter
from app.api.endpoints import login, platforms, question_banks


api_router = APIRouter()
api_router.include_router(login.router)