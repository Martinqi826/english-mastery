"""
认证服务
处理用户注册、登录、Token 管理等
"""
from datetime import datetime, timezone
from typing import Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from app.models.user import User
from app.models.membership import Membership, MembershipLevel
from app.models.learning import LearningProgress
from app.schemas.user import UserCreate
from app.schemas.auth import TokenResponse
from app.utils.security import (
    hash_password, 
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_refresh_token
)
from app.utils.redis_client import redis_client
from app.config import settings


class AuthService:
    """认证服务类"""
    
    @staticmethod
    async def register(
        db: AsyncSession,
        user_data: UserCreate
    ) -> Tuple[User, TokenResponse]:
        """
        用户注册
        返回用户对象和 Token
        """
        # 检查邮箱是否已存在
        if user_data.email:
            result = await db.execute(
                select(User).where(User.email == user_data.email)
            )
            if result.scalar_one_or_none():
                raise ValueError("该邮箱已被注册")
        
        # 检查手机号是否已存在
        if user_data.phone:
            result = await db.execute(
                select(User).where(User.phone == user_data.phone)
            )
            if result.scalar_one_or_none():
                raise ValueError("该手机号已被注册")
        
        # 创建用户
        user = User(
            email=user_data.email,
            phone=user_data.phone,
            password_hash=hash_password(user_data.password),
            name=user_data.name,
            last_login_at=datetime.now(timezone.utc)
        )
        db.add(user)
        await db.flush()  # 获取用户 ID
        
        # 创建默认会员记录（免费用户）
        membership = Membership(
            user_id=user.id,
            level=MembershipLevel.FREE
        )
        db.add(membership)
        
        # 创建学习进度记录
        learning_progress = LearningProgress(
            user_id=user.id
        )
        db.add(learning_progress)
        
        await db.commit()
        await db.refresh(user)
        
        # 生成 Token
        tokens = await AuthService._generate_tokens(user)
        
        return user, tokens
    
    @staticmethod
    async def login(
        db: AsyncSession,
        email: Optional[str],
        phone: Optional[str],
        password: str
    ) -> Tuple[User, TokenResponse]:
        """
        用户登录
        支持邮箱或手机号登录
        """
        # 查找用户
        conditions = []
        if email:
            conditions.append(User.email == email)
        if phone:
            conditions.append(User.phone == phone)
        
        result = await db.execute(
            select(User).where(or_(*conditions))
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise ValueError("用户不存在")
        
        if not user.is_active:
            raise ValueError("用户已被禁用")
        
        # 验证密码
        if not verify_password(password, user.password_hash):
            raise ValueError("密码错误")
        
        # 更新最后登录时间
        user.last_login_at = datetime.now(timezone.utc)
        await db.commit()
        
        # 生成 Token
        tokens = await AuthService._generate_tokens(user)
        
        return user, tokens
    
    @staticmethod
    async def refresh_tokens(
        db: AsyncSession,
        refresh_token: str
    ) -> TokenResponse:
        """
        刷新 Token
        """
        # 验证 Refresh Token
        payload = verify_refresh_token(refresh_token)
        if not payload:
            raise ValueError("无效的 Refresh Token")
        
        user_id = payload.get("sub")
        if not user_id:
            raise ValueError("无效的 Token")
        
        # 检查 Redis 中的 Refresh Token 是否匹配
        stored_token = await redis_client.get_refresh_token(int(user_id))
        if not stored_token or stored_token != refresh_token:
            raise ValueError("Refresh Token 已失效")
        
        # 获取用户
        result = await db.execute(
            select(User).where(User.id == int(user_id))
        )
        user = result.scalar_one_or_none()
        
        if not user or not user.is_active:
            raise ValueError("用户不存在或已被禁用")
        
        # 生成新 Token
        tokens = await AuthService._generate_tokens(user)
        
        return tokens
    
    @staticmethod
    async def logout(
        user_id: int,
        access_token: str,
        refresh_token: Optional[str] = None
    ):
        """
        退出登录
        将 Token 加入黑名单
        """
        # 将 Access Token 加入黑名单（过期时间与原 Token 一致）
        await redis_client.blacklist_token(
            access_token, 
            settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        
        # 删除 Refresh Token
        await redis_client.delete_refresh_token(user_id)
    
    @staticmethod
    async def change_password(
        db: AsyncSession,
        user: User,
        old_password: str,
        new_password: str
    ):
        """
        修改密码
        """
        # 验证旧密码
        if not verify_password(old_password, user.password_hash):
            raise ValueError("原密码错误")
        
        # 更新密码
        user.password_hash = hash_password(new_password)
        await db.commit()
        
        # 使所有 Token 失效
        await redis_client.delete_refresh_token(user.id)
    
    @staticmethod
    async def _generate_tokens(user: User) -> TokenResponse:
        """
        生成 Access Token 和 Refresh Token
        """
        # Token Payload
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "name": user.name
        }
        
        # 生成 Access Token
        access_token = create_access_token(token_data)
        
        # 生成 Refresh Token
        refresh_token = create_refresh_token(token_data)
        
        # 存储 Refresh Token 到 Redis
        await redis_client.store_refresh_token(
            user.id,
            refresh_token,
            settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
        )
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )


# 创建服务实例
auth_service = AuthService()
