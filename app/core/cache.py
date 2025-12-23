# app/core/cache.py
"""
Redis 缓存服务模块
提供统一的缓存操作接口，支持降级到内存缓存
"""
import json
import logging
from typing import Optional, Any, Callable
from functools import wraps
import redis
from app.core.config import settings

logger = logging.getLogger(__name__)

# Redis 客户端实例
_redis_client: Optional[redis.Redis] = None

# 内存缓存（降级方案）
_memory_cache: dict = {}


def get_redis_client() -> Optional[redis.Redis]:
    """
    获取 Redis 客户端实例（单例模式）
    如果 Redis 不可用，返回 None
    """
    global _redis_client

    if not settings.REDIS_ENABLED:
        return None

    if _redis_client is None:
        try:
            _redis_client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                password=settings.REDIS_PASSWORD,
                decode_responses=True,
                socket_timeout=5,
                socket_connect_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30
            )
            # 测试连接
            _redis_client.ping()
            logger.info(f"Redis 连接成功: {settings.REDIS_HOST}:{settings.REDIS_PORT}")
        except redis.ConnectionError as e:
            logger.warning(f"Redis 连接失败，将使用内存缓存: {e}")
            _redis_client = None
        except Exception as e:
            logger.warning(f"Redis 初始化异常: {e}")
            _redis_client = None

    return _redis_client


class CacheService:
    """
    缓存服务类
    优先使用 Redis，失败时降级到内存缓存
    """

    # 缓存键前缀
    PREFIX_BLUEPRINT = "blueprint:"
    PREFIX_ASSESSMENT = "assessment:"
    PREFIX_PLATFORM = "platform:"

    @staticmethod
    def _get_client() -> Optional[redis.Redis]:
        return get_redis_client()

    @classmethod
    def get(cls, key: str) -> Optional[Any]:
        """获取缓存值"""
        client = cls._get_client()

        if client:
            try:
                value = client.get(key)
                if value:
                    return json.loads(value)
            except redis.RedisError as e:
                logger.warning(f"Redis GET 失败: {e}")
            except json.JSONDecodeError as e:
                logger.warning(f"缓存数据解析失败: {e}")

        # 降级到内存缓存
        return _memory_cache.get(key)

    @classmethod
    def set(cls, key: str, value: Any, ttl: int = 3600) -> bool:
        """设置缓存值"""
        client = cls._get_client()
        serialized = json.dumps(value, ensure_ascii=False, default=str)

        if client:
            try:
                client.setex(key, ttl, serialized)
                return True
            except redis.RedisError as e:
                logger.warning(f"Redis SET 失败: {e}")

        # 降级到内存缓存（不支持 TTL）
        _memory_cache[key] = value
        return True

    @classmethod
    def delete(cls, key: str) -> bool:
        """删除缓存"""
        client = cls._get_client()

        if client:
            try:
                client.delete(key)
            except redis.RedisError as e:
                logger.warning(f"Redis DELETE 失败: {e}")

        # 同时清理内存缓存
        _memory_cache.pop(key, None)
        return True

    @classmethod
    def delete_pattern(cls, pattern: str) -> int:
        """删除匹配模式的所有键"""
        client = cls._get_client()
        deleted_count = 0

        if client:
            try:
                cursor = 0
                while True:
                    cursor, keys = client.scan(cursor, match=pattern, count=100)
                    if keys:
                        deleted_count += client.delete(*keys)
                    if cursor == 0:
                        break
            except redis.RedisError as e:
                logger.warning(f"Redis DELETE PATTERN 失败: {e}")

        # 同时清理内存缓存
        keys_to_delete = [k for k in _memory_cache.keys() if k.startswith(pattern.replace("*", ""))]
        for k in keys_to_delete:
            _memory_cache.pop(k, None)
            deleted_count += 1

        return deleted_count

    @classmethod
    def clear_all(cls) -> bool:
        """清空所有缓存（谨慎使用）"""
        client = cls._get_client()

        if client:
            try:
                client.flushdb()
            except redis.RedisError as e:
                logger.warning(f"Redis FLUSHDB 失败: {e}")

        _memory_cache.clear()
        return True

    # ============ 业务相关的缓存方法 ============

    @classmethod
    def get_blueprint(cls, question_bank_id: int) -> Optional[list]:
        """获取题库蓝图缓存"""
        key = f"{cls.PREFIX_BLUEPRINT}{question_bank_id}"
        return cls.get(key)

    @classmethod
    def set_blueprint(cls, question_bank_id: int, blueprint: list) -> bool:
        """设置题库蓝图缓存"""
        key = f"{cls.PREFIX_BLUEPRINT}{question_bank_id}"
        # 将 Pydantic 模型转为字典
        data = [proc.model_dump() if hasattr(proc, 'model_dump') else proc for proc in blueprint]
        return cls.set(key, data, ttl=settings.CACHE_TTL_BLUEPRINT)

    @classmethod
    def invalidate_blueprint(cls, question_bank_id: int) -> bool:
        """使题库蓝图缓存失效"""
        key = f"{cls.PREFIX_BLUEPRINT}{question_bank_id}"
        return cls.delete(key)

    @classmethod
    def get_upcoming_assessment(cls, platform_id: int) -> Optional[dict]:
        """获取平台即将进行的考核缓存"""
        key = f"{cls.PREFIX_ASSESSMENT}upcoming:{platform_id}"
        return cls.get(key)

    @classmethod
    def set_upcoming_assessment(cls, platform_id: int, assessment: dict) -> bool:
        """设置平台即将进行的考核缓存"""
        key = f"{cls.PREFIX_ASSESSMENT}upcoming:{platform_id}"
        return cls.set(key, assessment, ttl=settings.CACHE_TTL_ASSESSMENT)

    @classmethod
    def invalidate_assessment(cls, platform_id: int = None) -> int:
        """使考核缓存失效"""
        if platform_id:
            key = f"{cls.PREFIX_ASSESSMENT}upcoming:{platform_id}"
            cls.delete(key)
            return 1
        else:
            return cls.delete_pattern(f"{cls.PREFIX_ASSESSMENT}*")


# 缓存装饰器
def cached(key_func: Callable, ttl: int = 3600):
    """
    缓存装饰器
    用于自动缓存函数返回值

    使用示例:
    @cached(lambda bank_id: f"blueprint:{bank_id}", ttl=3600)
    def get_blueprint(bank_id: int):
        ...
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = key_func(*args, **kwargs)
            cached_value = CacheService.get(cache_key)

            if cached_value is not None:
                return cached_value

            result = func(*args, **kwargs)

            if result is not None:
                CacheService.set(cache_key, result, ttl=ttl)

            return result
        return wrapper
    return decorator


# 导出
cache_service = CacheService()
