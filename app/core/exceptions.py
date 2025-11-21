# app/core/exceptions.py
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi import status
from fastapi.exceptions import RequestValidationError



async def http_exception_handler(request: Request, exc: Exception):
    """
    全局 HTTP 异常处理器
    """
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "code": exc.status_code, # 使用 HTTP 状态码作为业务码
            "msg": exc.detail,
            "data": None
        },
    )

class BusinessException(Exception):
    """
    自定义业务异常基类
    """
    def __init__(self, code: int = 400, msg: str = "Bad Request", data: any = None):
        self.code = code
        self.msg = msg
        self.data = data

async def business_exception_handler(request: Request, exc: BusinessException):
    """
    自定义业务异常处理器
    """
    return JSONResponse(
        status_code=status.HTTP_200_OK, # 业务异常通常返回 200 OK
        content={
            "code": exc.code,
            "msg": exc.msg,
            "data": exc.data,
        }
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=HTTP_200_OK,
        content={
            "code": 422,
            "msg": "请求参数验证失败",
            "data": exc.errors() # 返回详细的字段错误信息
        }
    )