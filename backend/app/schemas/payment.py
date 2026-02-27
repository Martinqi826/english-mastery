"""
支付相关 Schema
"""
from datetime import datetime
from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel, Field

from app.models.order import OrderStatus, PayMethod, ProductType


class ProductInfo(BaseModel):
    """产品信息"""
    id: str
    name: str
    type: ProductType
    price: Decimal
    original_price: Optional[Decimal] = None
    duration_days: int = Field(..., description="有效期(天)")
    description: Optional[str] = None
    features: List[str] = []


class CreateOrderRequest(BaseModel):
    """创建订单请求"""
    product_id: str = Field(..., description="产品ID")
    pay_method: PayMethod = Field(..., description="支付方式")
    coupon_code: Optional[str] = Field(None, description="优惠券码")


class OrderResponse(BaseModel):
    """订单响应"""
    order_no: str
    product_name: str
    product_type: str
    amount: Decimal
    actual_amount: Decimal
    discount_amount: Decimal = Decimal(0)
    status: OrderStatus
    pay_method: Optional[PayMethod] = None
    created_at: datetime
    expire_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class PaymentResult(BaseModel):
    """支付结果"""
    order_no: str
    status: str
    pay_url: Optional[str] = None  # 支付链接/二维码
    prepay_id: Optional[str] = None  # 微信预支付ID
    qr_code: Optional[str] = None  # 支付二维码内容


class WechatNotifyData(BaseModel):
    """微信支付回调数据"""
    id: str
    create_time: str
    resource_type: str
    event_type: str
    summary: str
    resource: dict


class AlipayNotifyData(BaseModel):
    """支付宝回调数据"""
    notify_time: str
    notify_type: str
    notify_id: str
    app_id: str
    trade_no: str
    out_trade_no: str
    trade_status: str
    total_amount: str
    buyer_id: Optional[str] = None


class OrderListResponse(BaseModel):
    """订单列表响应"""
    orders: List[OrderResponse]
    total: int


class RefundRequest(BaseModel):
    """退款请求"""
    order_no: str
    reason: str = Field(..., max_length=200, description="退款原因")
