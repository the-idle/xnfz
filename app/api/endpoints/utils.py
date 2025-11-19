# app/api/endpoints/utils.py
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from app.api import deps
from app.models import user_management as user_models
from app.schemas.response import UnifiedResponse
import shutil
from pathlib import Path
from datetime import datetime



router = APIRouter()

# 定义一个用于存放上传文件的目录
UPLOAD_DIR = Path("static/images")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/upload/image/", response_model=UnifiedResponse[dict])
def upload_image(
    file: UploadFile = File(...),
    current_user: user_models.User = Depends(deps.get_current_user)
):
    """
    上传图片文件 (需要管理员权限)
    """
    # 校验文件类型
    if file.content_type not in ["image/jpeg", "image/png", "image/gif"]:
        raise HTTPException(status_code=400, detail="Invalid image type. Only JPEG, PNG, GIF are allowed.")
    
    try:
        # 创建一个安全的文件名 (例如，使用时间戳或UUID)
        file_path = UPLOAD_DIR / f"{datetime.utcnow().timestamp()}_{file.filename}"
        
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 返回一个可供前端访问的相对路径
        # (需要 FastAPI 配置静态文件服务)
        file_url = f"/{file_path}"
        
        return {"data": {"file_url": file_url}}
    finally:
        file.file.close()