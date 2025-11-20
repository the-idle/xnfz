# app/main.py
from fastapi import FastAPI

# 1. 导入您的主 API 路由器和配置
from app.api.api import api_router
from app.core.config import settings
from fastapi.exceptions import HTTPException
from app.core.exceptions import http_exception_handler, BusinessException, business_exception_handler
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# 2. (重要) 导入所有数据库模型，以确保 SQLAlchemy 在启动时能识别它们
#    这是解决运行时 "failed to locate a name" 错误的关键
from app.models import user_management
from app.models import question_management
from app.models import assessment_management

# 3. 创建 FastAPI 应用实例
app = FastAPI(
    title=settings.APP_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

origins = [
    "http://localhost:5173", # 前端地址
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # 开发阶段为了方便，可以直接设为 ["*"] 允许所有
    allow_credentials=True,
    allow_methods=["*"], # 允许所有方法 (GET, POST, PUT...)
    allow_headers=["*"], # 允许所有 Header
)

app.mount("/static", StaticFiles(directory="static"), name="static")    
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(BusinessException, business_exception_handler)
# 4. (重要) 移除 startup 事件中的 create_all。
#    我们完全信任 Alembic 来管理数据库迁移。

# 5. 添加一个健康的根路径，用于检查服务是否存活
@app.get("/", tags=["Health Check"])
def health_check():
    """
    健康检查端点。
    """
    return {"status": "ok", "app_name": settings.APP_NAME}

# 6. 将您的主 API 路由器包含进来，并添加统一的前缀
app.include_router(api_router, prefix=settings.API_V1_STR)