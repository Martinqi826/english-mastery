"""
认证 API 路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.deps import get_current_user, security
from app.models.user import User
from app.schemas.base import APIResponse, ErrorCode, success_response, error_response
from app.schemas.user import UserCreate, UserResponse
from app.schemas.auth import (
    LoginRequest, 
    TokenResponse, 
    RefreshRequest,
    LogoutRequest
)
from app.services.auth_service import auth_service


router = APIRouter()


@router.post("/register", response_model=APIResponse[dict])
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    用户注册
    
    - 支持邮箱或手机号注册（至少填一个）
    - 密码至少6位
    - 注册成功后自动登录，返回 Token
    """
    try:
        user, tokens = await auth_service.register(db, user_data)
        
        return success_response({
            "user": {
                "id": user.id,
                "email": user.email,
                "phone": user.phone,
                "name": user.name
            },
            "tokens": tokens.model_dump()
        }, "注册成功")
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_response(ErrorCode.INVALID_PARAMS, str(e))
        )


@router.post("/login", response_model=APIResponse[dict])
async def login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    用户登录
    
    - 支持邮箱或手机号登录
    - 返回 Access Token 和 Refresh Token
    """
    try:
        user, tokens = await auth_service.login(
            db,
            email=login_data.email,
            phone=login_data.phone,
            password=login_data.password
        )
        
        return success_response({
            "user": {
                "id": user.id,
                "email": user.email,
                "phone": user.phone,
                "name": user.name,
                "avatar": user.avatar
            },
            "tokens": tokens.model_dump()
        }, "登录成功")
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error_response(ErrorCode.INVALID_CREDENTIALS, str(e))
        )


@router.post("/refresh", response_model=APIResponse[TokenResponse])
async def refresh_token(
    refresh_data: RefreshRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    刷新 Token
    
    - 使用 Refresh Token 获取新的 Access Token
    - Refresh Token 也会更新
    """
    try:
        tokens = await auth_service.refresh_tokens(
            db,
            refresh_data.refresh_token
        )
        
        return success_response(tokens, "Token 刷新成功")
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error_response(ErrorCode.TOKEN_EXPIRED, str(e))
        )


@router.post("/logout", response_model=APIResponse)
async def logout(
    logout_data: LogoutRequest = None,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    current_user: User = Depends(get_current_user)
):
    """
    退出登录
    
    - 将当前 Token 加入黑名单
    - 清除 Refresh Token
    """
    access_token = credentials.credentials if credentials else ""
    refresh_token = logout_data.refresh_token if logout_data else None
    
    await auth_service.logout(
        current_user.id,
        access_token,
        refresh_token
    )
    
    return success_response(None, "退出成功")


@router.get("/me", response_model=APIResponse[UserResponse])
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取当前用户信息
    """
    from sqlalchemy import select
    from app.models.membership import Membership
    
    # 获取会员信息
    result = await db.execute(
        select(Membership).where(Membership.user_id == current_user.id)
    )
    membership = result.scalar_one_or_none()
    
    user_response = UserResponse(
        id=current_user.id,
        email=current_user.email,
        phone=current_user.phone,
        name=current_user.name,
        avatar=current_user.avatar,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        created_at=current_user.created_at,
        last_login_at=current_user.last_login_at,
        membership_level=membership.level.value if membership else "free",
        membership_active=membership.is_active if membership else False
    )
    
    return success_response(user_response)
