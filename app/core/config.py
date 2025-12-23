from pydantic import BaseModel
from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv
load_dotenv()
class Settings(BaseSettings):
    APP_NAME: str = "Unity Assessment API"
    DEBUG: bool = False

    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = os.getenv("ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

    DATABASE_URL: str = os.getenv("DATABASE_URL")

    # Redis 配置
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", 6379))
    REDIS_DB: int = int(os.getenv("REDIS_DB", 0))
    REDIS_PASSWORD: Optional[str] = os.getenv("REDIS_PASSWORD", None)
    REDIS_ENABLED: bool = os.getenv("REDIS_ENABLED", "true").lower() == "true"

    # 缓存过期时间配置（秒）
    CACHE_TTL_BLUEPRINT: int = int(os.getenv("CACHE_TTL_BLUEPRINT", 3600))  # 题库蓝图缓存1小时
    CACHE_TTL_ASSESSMENT: int = int(os.getenv("CACHE_TTL_ASSESSMENT", 300))  # 考核信息缓存5分钟

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()