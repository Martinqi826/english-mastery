"""
支付服务
处理订单创建、支付、回调等
"""
import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.models.user import User
from app.models.order import Order, OrderStatus, PayMethod, ProductType
from app.models.membership import Membership, MembershipLevel
from app.schemas.payment import CreateOrderRequest, ProductInfo, PaymentResult
from app.utils.redis_client import redis_client
from app.config import settings


# 产品配置
PRODUCTS = {
    "basic_monthly": ProductInfo(
        id="basic_monthly",
        name="基础会员 - 月付",
        type=ProductType.BASIC_MONTHLY,
        price=Decimal("29.00"),
        original_price=Decimal("39.00"),
        duration_days=30,
        description="解锁全部学习内容",
        features=["全部词汇学习", "全部听力课程", "全部阅读材料", "全部写作练习"]
    ),
    "basic_yearly": ProductInfo(
        id="basic_yearly",
        name="基础会员 - 年付",
        type=ProductType.BASIC_YEARLY,
        price=Decimal("199.00"),
        original_price=Decimal("468.00"),
        duration_days=365,
        description="年付更优惠，省269元",
        features=["全部词汇学习", "全部听力课程", "全部阅读材料", "全部写作练习"]
    ),
    "premium_monthly": ProductInfo(
        id="premium_monthly",
        name="高级会员 - 月付",
        type=ProductType.PREMIUM_MONTHLY,
        price=Decimal("99.00"),
        original_price=Decimal("149.00"),
        duration_days=30,
        description="专属辅导，快速进步",
        features=["基础会员全部功能", "AI 智能批改", "专属学习计划", "1对1答疑"]
    ),
    "premium_yearly": ProductInfo(
        id="premium_yearly",
        name="高级会员 - 年付",
        type=ProductType.PREMIUM_YEARLY,
        price=Decimal("799.00"),
        original_price=Decimal("1788.00"),
        duration_days=365,
        description="年付更优惠，省989元",
        features=["基础会员全部功能", "AI 智能批改", "专属学习计划", "1对1答疑"]
    ),
}


class PaymentService:
    """支付服务类"""
    
    @staticmethod
    def get_products() -> List[ProductInfo]:
        """获取所有产品列表"""
        return list(PRODUCTS.values())
    
    @staticmethod
    def get_product(product_id: str) -> Optional[ProductInfo]:
        """获取产品信息"""
        return PRODUCTS.get(product_id)
    
    @staticmethod
    def generate_order_no() -> str:
        """生成订单号"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_part = uuid.uuid4().hex[:8].upper()
        return f"EM{timestamp}{random_part}"
    
    @staticmethod
    async def create_order(
        db: AsyncSession,
        user_id: int,
        request: CreateOrderRequest
    ) -> Order:
        """
        创建订单
        """
        # 获取产品信息
        product = PaymentService.get_product(request.product_id)
        if not product:
            raise ValueError("产品不存在")
        
        # 计算金额
        amount = product.price
        actual_amount = amount
        discount_amount = Decimal(0)
        
        # TODO: 处理优惠券
        if request.coupon_code:
            # 验证优惠券并计算折扣
            pass
        
        # 创建订单
        order = Order(
            order_no=PaymentService.generate_order_no(),
            user_id=user_id,
            product_type=product.type,
            product_name=product.name,
            product_id=request.product_id,
            amount=amount,
            actual_amount=actual_amount,
            discount_amount=discount_amount,
            pay_method=request.pay_method,
            status=OrderStatus.PENDING,
            expire_at=datetime.now(timezone.utc) + timedelta(minutes=30)  # 30分钟过期
        )
        
        db.add(order)
        await db.commit()
        await db.refresh(order)
        
        return order
    
    @staticmethod
    async def get_payment_url(
        order: Order
    ) -> PaymentResult:
        """
        获取支付链接/二维码
        """
        if order.pay_method == PayMethod.WECHAT:
            return await PaymentService._create_wechat_payment(order)
        elif order.pay_method == PayMethod.ALIPAY:
            return await PaymentService._create_alipay_payment(order)
        else:
            raise ValueError("不支持的支付方式")
    
    @staticmethod
    async def _create_wechat_payment(order: Order) -> PaymentResult:
        """
        创建微信支付
        """
        # TODO: 调用微信支付 API
        # 这里返回模拟数据，实际需要集成微信支付 SDK
        return PaymentResult(
            order_no=order.order_no,
            status="pending",
            pay_url=f"https://wx.tenpay.com/pay?order={order.order_no}",
            qr_code=f"weixin://wxpay/bizpayurl?sr={order.order_no}"
        )
    
    @staticmethod
    async def _create_alipay_payment(order: Order) -> PaymentResult:
        """
        创建支付宝支付
        """
        # TODO: 调用支付宝 API
        # 这里返回模拟数据，实际需要集成支付宝 SDK
        return PaymentResult(
            order_no=order.order_no,
            status="pending",
            pay_url=f"https://openapi.alipay.com/gateway?order={order.order_no}"
        )
    
    @staticmethod
    async def handle_payment_success(
        db: AsyncSession,
        order_no: str,
        trade_no: str
    ) -> Order:
        """
        处理支付成功
        """
        # 获取订单
        result = await db.execute(
            select(Order).where(Order.order_no == order_no)
        )
        order = result.scalar_one_or_none()
        
        if not order:
            raise ValueError("订单不存在")
        
        if order.status == OrderStatus.PAID:
            return order  # 已处理过
        
        # 更新订单状态
        order.status = OrderStatus.PAID
        order.trade_no = trade_no
        order.pay_time = datetime.now(timezone.utc)
        
        # 开通/续费会员
        await PaymentService._activate_membership(db, order)
        
        await db.commit()
        await db.refresh(order)
        
        # 清除会员缓存
        await redis_client.invalidate_user_membership(order.user_id)
        
        return order
    
    @staticmethod
    async def _activate_membership(
        db: AsyncSession,
        order: Order
    ):
        """
        激活/续费会员
        """
        # 获取产品信息
        product = PaymentService.get_product(order.product_id)
        if not product:
            return
        
        # 确定会员等级
        if order.product_type in [ProductType.BASIC_MONTHLY, ProductType.BASIC_YEARLY]:
            level = MembershipLevel.BASIC
        elif order.product_type in [ProductType.PREMIUM_MONTHLY, ProductType.PREMIUM_YEARLY]:
            level = MembershipLevel.PREMIUM
        else:
            return  # 非会员产品
        
        # 获取用户会员记录
        result = await db.execute(
            select(Membership).where(Membership.user_id == order.user_id)
        )
        membership = result.scalar_one_or_none()
        
        now = datetime.now(timezone.utc)
        
        if not membership:
            # 创建会员记录
            membership = Membership(
                user_id=order.user_id,
                level=level,
                start_date=now,
                end_date=now + timedelta(days=product.duration_days)
            )
            db.add(membership)
        else:
            # 更新/续费
            if membership.end_date and membership.end_date > now:
                # 在有效期内续费，延长时间
                membership.end_date = membership.end_date + timedelta(days=product.duration_days)
            else:
                # 已过期，重新开始
                membership.start_date = now
                membership.end_date = now + timedelta(days=product.duration_days)
            
            # 升级等级
            if level == MembershipLevel.PREMIUM:
                membership.level = level
    
    @staticmethod
    async def get_user_orders(
        db: AsyncSession,
        user_id: int,
        status: Optional[OrderStatus] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[Order]:
        """
        获取用户订单列表
        """
        query = select(Order).where(Order.user_id == user_id)
        
        if status:
            query = query.where(Order.status == status)
        
        query = query.order_by(Order.created_at.desc()).offset(offset).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_order_by_no(
        db: AsyncSession,
        order_no: str
    ) -> Optional[Order]:
        """
        根据订单号获取订单
        """
        result = await db.execute(
            select(Order).where(Order.order_no == order_no)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def cancel_order(
        db: AsyncSession,
        order: Order
    ) -> Order:
        """
        取消订单
        """
        if order.status != OrderStatus.PENDING:
            raise ValueError("只能取消待支付订单")
        
        order.status = OrderStatus.CANCELLED
        await db.commit()
        await db.refresh(order)
        
        return order


# 创建服务实例
payment_service = PaymentService()
