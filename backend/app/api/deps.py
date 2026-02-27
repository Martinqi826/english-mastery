"""
API 依赖注入
"""
from typing import Optional, Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.user import User
from app.models.membership import Membership, MembershipLevel
from app.utils.security import verify_access_token
from app.utils.redis_client import redis_client
from app.schemas.base import ErrorCode


# Bearer Token 提取器
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Annotated[
        Optional[HTTPAuthorizationCredentials], 
        Depends(security)
    ],
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    获取当前登录用户
    验证 JWT Token 并返回用户对象
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": ErrorCode.UNAUTHORIZED,
                "message": "未提供认证信息"
            }
        )
    
    token = credentials.credentials
    
    # 检查 Token 是否在黑名单中
    if await redis_client.is_token_blacklisted(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": ErrorCode.INVALID_TOKEN,
                "message": "Token 已失效"
            }
        )
    
    # 验证 Token
    payload = verify_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": ErrorCode.INVALID_TOKEN,
                "message": "无效的 Token"
            }
        )
    
    # 获取用户
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": ErrorCode.INVALID_TOKEN,
                "message": "无效的 Token"
            }
        )
    
    result = await db.execute(
        select(User).where(User.id == int(user_id))
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": ErrorCode.USER_NOT_FOUND,
                "message": "用户不存在"
            }
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": ErrorCode.USER_DISABLED,
                "message": "用户已被禁用"
            }
        )
    
    return user


async def get_current_user_optional(
    credentials: Annotated[
        Optional[HTTPAuthorizationCredentials], 
        Depends(security)
    ],
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """
    可选的用户认证
    未登录时返回 None，不抛出异常
    """
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        return None


async def get_current_active_member(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    获取当前会员用户
    验证用户具有有效会员资格
    """
    result = await db.execute(
        select(Membership).where(Membership.user_id == current_user.id)
    )
    membership = result.scalar_one_or_none()
    
    if not membership or membership.level == MembershipLevel.FREE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": ErrorCode.MEMBERSHIP_REQUIRED,
                "message": "需要会员资格"
            }
        )
    
    if not membership.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": ErrorCode.MEMBERSHIP_EXPIRED,
                "message": "会员已过期"
            }
        )
    
    return current_user


async def get_current_premium_member(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    获取当前高级会员用户
    验证用户具有高级会员资格
    """
    result = await db.execute(
        select(Membership).where(Membership.user_id == current_user.id)
    )
    membership = result.scalar_one_or_none()
    
    if not membership or membership.level != MembershipLevel.PREMIUM:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": ErrorCode.PREMIUM_REQUIRED,
                "message": "需要高级会员资格"
            }
        )
    
    if not membership.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": ErrorCode.MEMBERSHIP_EXPIRED,
                "message": "会员已过期"
            }
        )
    
    return current_user


async def check_rate_limit(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    检查 API 限流
    """
    from app.config import settings
    
    allowed, remaining = await redis_client.check_rate_limit(
        f"user:{current_user.id}",
        limit=settings.RATE_LIMIT_PER_MINUTE,
        window=60
    )
    
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "code": ErrorCode.RATE_LIMIT_EXCEEDED,
                "message": "请求过于频繁，请稍后再试"
            }
        )
    
    return current_user
