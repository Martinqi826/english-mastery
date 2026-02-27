"""
订单模型
"""
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class OrderStatus(str, Enum):
    """订单状态枚举"""
    PENDING = "pending"         # 待支付
    PAID = "paid"               # 已支付
    CANCELLED = "cancelled"     # 已取消
    REFUNDED = "refunded"       # 已退款
    FAILED = "failed"           # 支付失败


class PayMethod(str, Enum):
    """支付方式枚举"""
    WECHAT = "wechat"           # 微信支付
    ALIPAY = "alipay"           # 支付宝


class ProductType(str, Enum):
    """产品类型枚举"""
    BASIC_MONTHLY = "basic_monthly"         # 基础会员月付
    BASIC_YEARLY = "basic_yearly"           # 基础会员年付
    PREMIUM_MONTHLY = "premium_monthly"     # 高级会员月付
    PREMIUM_YEARLY = "premium_yearly"       # 高级会员年付
    COURSE = "course"                       # 单独课程


class Order(Base):
    """订单表"""
    
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 订单信息
    order_no = Column(
        String(64), 
        unique=True, 
        nullable=False, 
        index=True,
        comment="订单号"
    )
    user_id = Column(
        Integer, 
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False,
        index=True,
        comment="用户ID"
    )
    
    # 产品信息
    product_type = Column(
        SQLEnum(ProductType), 
        nullable=False,
        comment="产品类型"
    )
    product_name = Column(String(200), nullable=False, comment="产品名称")
    product_id = Column(String(50), nullable=True, comment="产品ID(课程ID等)")
    
    # 金额
    amount = Column(Numeric(10, 2), nullable=False, comment="订单金额")
    actual_amount = Column(Numeric(10, 2), nullable=False, comment="实付金额")
    discount_amount = Column(Numeric(10, 2), default=0, comment="优惠金额")
    
    # 支付信息
    pay_method = Column(SQLEnum(PayMethod), nullable=True, comment="支付方式")
    status = Column(
        SQLEnum(OrderStatus), 
        default=OrderStatus.PENDING,
        nullable=False,
        index=True,
        comment="订单状态"
    )
    
    # 第三方支付信息
    trade_no = Column(String(64), nullable=True, comment="第三方交易号")
    pay_time = Column(DateTime, nullable=True, comment="支付时间")
    
    # 退款信息
    refund_no = Column(String(64), nullable=True, comment="退款单号")
    refund_amount = Column(Numeric(10, 2), nullable=True, comment="退款金额")
    refund_time = Column(DateTime, nullable=True, comment="退款时间")
    refund_reason = Column(Text, nullable=True, comment="退款原因")
    
    # 备注
    remark = Column(Text, nullable=True, comment="订单备注")
    
    # 时间
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(
        DateTime, 
        server_default=func.now(), 
        onupdate=func.now(),
        comment="更新时间"
    )
    expire_at = Column(DateTime, nullable=True, comment="订单过期时间")
    
    # 关联
    user = relationship("User", back_populates="orders")
    
    def __repr__(self):
        return f"<Order(order_no={self.order_no}, status={self.status})>"
