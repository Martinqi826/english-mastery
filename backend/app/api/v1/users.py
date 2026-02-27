"""
用户 API 路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.membership import Membership
from app.models.learning import LearningProgress
from app.schemas.base import APIResponse, ErrorCode, success_response, error_response
from app.schemas.user import UserUpdate, UserPasswordChange, UserProfileResponse
from app.services.auth_service import auth_service
from app.utils.security import hash_password


router = APIRouter()


@router.get("/profile", response_model=APIResponse[UserProfileResponse])
async def get_user_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取用户详细资料
    
    包含用户信息、学习统计、会员状态
    """
    # 获取会员信息
    result = await db.execute(
        select(Membership).where(Membership.user_id == current_user.id)
    )
    membership = result.scalar_one_or_none()
    
    # 获取学习进度
    result = await db.execute(
        select(LearningProgress).where(LearningProgress.user_id == current_user.id)
    )
    progress = result.scalar_one_or_none()
    
    profile = UserProfileResponse(
        id=current_user.id,
        email=current_user.email,
        phone=current_user.phone,
        name=current_user.name,
        avatar=current_user.avatar,
        created_at=current_user.created_at,
        current_day=progress.current_day if progress else 1,
        streak_days=progress.streak_days if progress else 0,
        total_study_time=progress.total_study_time if progress else 0,
        words_learned=progress.words_learned if progress else 0,
        membership_level=membership.level.value if membership else "free",
        membership_end_date=membership.end_date if membership else None
    )
    
    return success_response(profile)


@router.put("/profile", response_model=APIResponse)
async def update_user_profile(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    更新用户资料
    
    可更新字段：昵称、头像
    """
    if update_data.name is not None:
        current_user.name = update_data.name
    
    if update_data.avatar is not None:
        current_user.avatar = update_data.avatar
    
    await db.commit()
    
    return success_response({
        "id": current_user.id,
        "name": current_user.name,
        "avatar": current_user.avatar
    }, "资料更新成功")


@router.put("/password", response_model=APIResponse)
async def change_password(
    password_data: UserPasswordChange,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    修改密码
    
    需要提供原密码和新密码
    """
    try:
        await auth_service.change_password(
            db,
            current_user,
            password_data.old_password,
            password_data.new_password
        )
        
        return success_response(None, "密码修改成功，请重新登录")
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_response(ErrorCode.INVALID_PARAMS, str(e))
        )


@router.get("/membership", response_model=APIResponse)
async def get_membership_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取会员状态
    """
    result = await db.execute(
        select(Membership).where(Membership.user_id == current_user.id)
    )
    membership = result.scalar_one_or_none()
    
    if not membership:
        return success_response({
            "level": "free",
            "is_active": True,
            "start_date": None,
            "end_date": None,
            "days_remaining": 0,
            "auto_renew": False
        })
    
    return success_response({
        "level": membership.level.value,
        "is_active": membership.is_active,
        "start_date": membership.start_date,
        "end_date": membership.end_date,
        "days_remaining": membership.days_remaining,
        "auto_renew": membership.auto_renew
    })


@router.delete("/account", response_model=APIResponse)
async def delete_account(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    注销账户
    
    警告：此操作不可恢复
    """
    # 软删除：标记为非激活状态
    current_user.is_active = False
    await db.commit()
    
    # 清除 Token
    from app.utils.redis_client import redis_client
    await redis_client.delete_refresh_token(current_user.id)
    
    return success_response(None, "账户已注销")
