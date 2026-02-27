"""
API v1 路由模块
"""
from fastapi import APIRouter

from app.api.v1 import auth, users, learning, vocabulary, payment

api_router = APIRouter()

# 注册各模块路由
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(users.router, prefix="/users", tags=["用户"])
api_router.include_router(learning.router, prefix="/learning", tags=["学习"])
api_router.include_router(vocabulary.router, prefix="/vocabulary", tags=["词汇"])
api_router.include_router(payment.router, prefix="/payment", tags=["支付"])
