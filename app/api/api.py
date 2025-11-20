# app/api/api.py
from fastapi import APIRouter

# 1. 导入所有端点模块
from app.api.endpoints import (
    login, platforms, question_banks, procedures, questions , client, assessments, utils, results, users
)

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(platforms.router, prefix="/platforms", tags=["platforms"])

# 二级资源：题库 (嵌套在平台下)
api_router.include_router(
    question_banks.router,
    prefix="/platforms/{platform_id}/question-banks", # <-- 建议嵌套
    tags=["question-banks"]
)

# 三级资源：工序/点位 (嵌套在题库下)
api_router.include_router(
    procedures.router,
    prefix="/question-banks/{question_bank_id}/procedures",
    tags=["procedures"]
)

# 四级资源：题目 (嵌套在工序/点位下)
api_router.include_router(
    questions.router,
    prefix="/procedures/{procedure_id}/questions",
    tags=["questions"]
)
api_router.include_router(utils.router, prefix="/utils", tags=["utils"])

api_router.include_router(assessments.router, prefix="/assessments", tags=["assessments"])
api_router.include_router(client.router, prefix="/client", tags=["client"])
api_router.include_router(results.router, prefix="/admin", tags=["results"])

