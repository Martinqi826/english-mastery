"""
会员模型
"""
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class MembershipLevel(str, Enum):
    """会员等级枚举"""
    FREE = "free"           # 免费用户
    BASIC = "basic"         # 基础会员
    PREMIUM = "premium"     # 高级会员


class Membership(Base):
    """会员表"""
    
    __tablename__ = "memberships"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(
        Integer, 
        ForeignKey("users.id", ondelete="CASCADE"), 
        unique=True, 
        nullable=False,
        comment="用户ID"
    )
    
    # 会员信息
    level = Column(
        SQLEnum(MembershipLevel), 
        default=MembershipLevel.FREE, 
        nullable=False,
        comment="会员等级"
    )
    
    # 有效期
    start_date = Column(DateTime, nullable=True, comment="会员开始时间")
    end_date = Column(DateTime, nullable=True, comment="会员结束时间")
    
    # 自动续费
    auto_renew = Column(Boolean, default=False, comment="是否自动续费")
    renew_product_id = Column(String(50), nullable=True, comment="续费产品ID")
    
    # 时间
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(
        DateTime, 
        server_default=func.now(), 
        onupdate=func.now(),
        comment="更新时间"
    )
    
    # 关联
    user = relationship("User", back_populates="membership")
    
    @property
    def is_active(self) -> bool:
        """检查会员是否有效"""
        if self.level == MembershipLevel.FREE:
            return True
        if not self.end_date:
            return False
        return datetime.now() < self.end_date
    
    @property
    def days_remaining(self) -> int:
        """剩余天数"""
        if self.level == MembershipLevel.FREE or not self.end_date:
            return 0
        delta = self.end_date - datetime.now()
        return max(0, delta.days)
    
    def __repr__(self):
        return f"<Membership(user_id={self.user_id}, level={self.level})>"
