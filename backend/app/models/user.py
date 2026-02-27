"""
用户模型
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    """用户表"""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 登录凭证
    email = Column(String(255), unique=True, index=True, nullable=True, comment="邮箱")
    phone = Column(String(20), unique=True, index=True, nullable=True, comment="手机号")
    password_hash = Column(String(255), nullable=False, comment="密码哈希")
    
    # 基本信息
    name = Column(String(100), nullable=False, comment="昵称")
    avatar = Column(String(500), nullable=True, comment="头像URL")
    
    # 第三方登录
    wechat_openid = Column(String(100), unique=True, nullable=True, comment="微信OpenID")
    wechat_unionid = Column(String(100), nullable=True, comment="微信UnionID")
    google_id = Column(String(100), unique=True, nullable=True, comment="Google ID")
    
    # 状态
    is_active = Column(Boolean, default=True, comment="是否激活")
    is_verified = Column(Boolean, default=False, comment="邮箱/手机是否验证")
    
    # 时间
    created_at = Column(
        DateTime, 
        server_default=func.now(), 
        comment="创建时间"
    )
    updated_at = Column(
        DateTime, 
        server_default=func.now(), 
        onupdate=func.now(),
        comment="更新时间"
    )
    last_login_at = Column(DateTime, nullable=True, comment="最后登录时间")
    
    # 关联
    membership = relationship(
        "Membership", 
        back_populates="user", 
        uselist=False
    )
    learning_progress = relationship(
        "LearningProgress",
        back_populates="user",
        uselist=False
    )
    checkin_records = relationship(
        "CheckinRecord",
        back_populates="user"
    )
    orders = relationship(
        "Order",
        back_populates="user"
    )
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, name={self.name})>"
