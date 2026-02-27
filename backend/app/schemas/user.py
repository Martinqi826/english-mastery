"""
用户相关 Schema
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator
import re


class UserBase(BaseModel):
    """用户基础信息"""
    name: str = Field(..., min_length=2, max_length=100, description="昵称")


class UserCreate(UserBase):
    """用户注册请求"""
    email: Optional[EmailStr] = Field(None, description="邮箱")
    phone: Optional[str] = Field(None, description="手机号")
    password: str = Field(..., min_length=6, max_length=50, description="密码")
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        if v is not None:
            # 中国手机号格式验证
            if not re.match(r'^1[3-9]\d{9}$', v):
                raise ValueError('无效的手机号格式')
        return v
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('密码至少6位')
        return v
    
    def model_post_init(self, __context):
        """验证邮箱和手机号至少有一个"""
        if not self.email and not self.phone:
            raise ValueError('邮箱和手机号至少填写一个')


class UserUpdate(BaseModel):
    """用户信息更新请求"""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    avatar: Optional[str] = Field(None, max_length=500)


class UserPasswordChange(BaseModel):
    """密码修改请求"""
    old_password: str = Field(..., min_length=6)
    new_password: str = Field(..., min_length=6, max_length=50)


class UserResponse(BaseModel):
    """用户响应"""
    id: int
    email: Optional[str] = None
    phone: Optional[str] = None
    name: str
    avatar: Optional[str] = None
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login_at: Optional[datetime] = None
    
    # 会员信息（简要）
    membership_level: Optional[str] = None
    membership_active: bool = False
    
    class Config:
        from_attributes = True


class UserProfileResponse(BaseModel):
    """用户详细资料响应"""
    id: int
    email: Optional[str] = None
    phone: Optional[str] = None
    name: str
    avatar: Optional[str] = None
    created_at: datetime
    
    # 学习统计
    current_day: int = 1
    streak_days: int = 0
    total_study_time: int = 0
    words_learned: int = 0
    
    # 会员信息
    membership_level: str = "free"
    membership_end_date: Optional[datetime] = None
    
    class Config:
        from_attributes = True
