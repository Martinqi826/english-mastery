"""
基础 Schema 定义
统一响应格式
"""
from typing import TypeVar, Generic, Optional, Any
from pydantic import BaseModel


T = TypeVar('T')


class APIResponse(BaseModel, Generic[T]):
    """统一 API 响应格式"""
    code: int = 0
    message: str = "success"
    data: Optional[T] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "code": 0,
                "message": "success",
                "data": {}
            }
        }


class PageInfo(BaseModel):
    """分页信息"""
    page: int = 1
    page_size: int = 20
    total: int = 0
    total_pages: int = 0


class PaginatedResponse(BaseModel, Generic[T]):
    """分页响应"""
    items: list[T] = []
    page_info: PageInfo


def success_response(data: Any = None, message: str = "success") -> dict:
    """成功响应"""
    return {
        "code": 0,
        "message": message,
        "data": data
    }


def error_response(code: int, message: str, data: Any = None) -> dict:
    """错误响应"""
    return {
        "code": code,
        "message": message,
        "data": data
    }


# 常用错误码
class ErrorCode:
    """错误码定义"""
    
    # 通用错误 1xxx
    UNKNOWN_ERROR = 1000
    INVALID_PARAMS = 1001
    NOT_FOUND = 1002
    PERMISSION_DENIED = 1003
    RATE_LIMIT_EXCEEDED = 1004
    
    # 认证错误 2xxx
    UNAUTHORIZED = 2000
    INVALID_TOKEN = 2001
    TOKEN_EXPIRED = 2002
    INVALID_CREDENTIALS = 2003
    USER_NOT_FOUND = 2004
    USER_DISABLED = 2005
    EMAIL_EXISTS = 2006
    PHONE_EXISTS = 2007
    
    # 会员错误 3xxx
    MEMBERSHIP_EXPIRED = 3000
    MEMBERSHIP_REQUIRED = 3001
    PREMIUM_REQUIRED = 3002
    
    # 支付错误 4xxx
    ORDER_NOT_FOUND = 4000
    ORDER_EXPIRED = 4001
    ORDER_ALREADY_PAID = 4002
    PAYMENT_FAILED = 4003
    REFUND_FAILED = 4004
    
    # 内容错误 5xxx
    CONTENT_NOT_FOUND = 5000
    CONTENT_UNAVAILABLE = 5001
