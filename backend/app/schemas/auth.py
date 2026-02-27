"""
认证相关 Schema
"""
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """登录请求"""
    email: Optional[EmailStr] = Field(None, description="邮箱")
    phone: Optional[str] = Field(None, description="手机号")
    password: str = Field(..., min_length=1, description="密码")
    
    def model_post_init(self, __context):
        """验证邮箱和手机号至少有一个"""
        if not self.email and not self.phone:
            raise ValueError('请提供邮箱或手机号')


class TokenResponse(BaseModel):
    """Token 响应"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = Field(..., description="access_token 有效期(秒)")


class RefreshRequest(BaseModel):
    """Token 刷新请求"""
    refresh_token: str


class LogoutRequest(BaseModel):
    """退出登录请求"""
    refresh_token: Optional[str] = None


class PasswordResetRequest(BaseModel):
    """密码重置请求"""
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    
    def model_post_init(self, __context):
        if not self.email and not self.phone:
            raise ValueError('请提供邮箱或手机号')


class PasswordResetConfirm(BaseModel):
    """密码重置确认"""
    token: str
    new_password: str = Field(..., min_length=6, max_length=50)


class WechatLoginRequest(BaseModel):
    """微信登录请求"""
    code: str = Field(..., description="微信授权码")


class GoogleLoginRequest(BaseModel):
    """Google 登录请求"""
    id_token: str = Field(..., description="Google ID Token")
