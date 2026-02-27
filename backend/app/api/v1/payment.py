"""
支付 API 路由
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.order import OrderStatus
from app.schemas.base import APIResponse, ErrorCode, success_response, error_response
from app.schemas.payment import (
    CreateOrderRequest,
    OrderResponse,
    PaymentResult,
    OrderListResponse,
    RefundRequest
)
from app.services.payment_service import payment_service


router = APIRouter()


@router.get("/products", response_model=APIResponse)
async def get_products():
    """
    获取产品列表
    
    返回所有可购买的会员产品
    """
    products = payment_service.get_products()
    
    return success_response({
        "products": [
            {
                "id": p.id,
                "name": p.name,
                "type": p.type.value,
                "price": str(p.price),
                "original_price": str(p.original_price) if p.original_price else None,
                "duration_days": p.duration_days,
                "description": p.description,
                "features": p.features
            }
            for p in products
        ]
    })


@router.post("/orders", response_model=APIResponse[PaymentResult])
async def create_order(
    request: CreateOrderRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    创建订单
    
    - 选择产品和支付方式
    - 返回支付链接/二维码
    """
    try:
        # 创建订单
        order = await payment_service.create_order(
            db, 
            current_user.id, 
            request
        )
        
        # 获取支付链接
        payment_result = await payment_service.get_payment_url(order)
        
        return success_response(payment_result, "订单创建成功")
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=error_response(ErrorCode.INVALID_PARAMS, str(e))
        )


@router.get("/orders", response_model=APIResponse[OrderListResponse])
async def get_orders(
    status: Optional[str] = Query(None, description="订单状态筛选"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取订单列表
    """
    order_status = None
    if status:
        try:
            order_status = OrderStatus(status)
        except ValueError:
            pass
    
    orders = await payment_service.get_user_orders(
        db,
        current_user.id,
        status=order_status,
        limit=page_size,
        offset=(page - 1) * page_size
    )
    
    return success_response(OrderListResponse(
        orders=[
            OrderResponse(
                order_no=o.order_no,
                product_name=o.product_name,
                product_type=o.product_type.value,
                amount=o.amount,
                actual_amount=o.actual_amount,
                discount_amount=o.discount_amount,
                status=o.status,
                pay_method=o.pay_method,
                created_at=o.created_at,
                expire_at=o.expire_at
            )
            for o in orders
        ],
        total=len(orders)
    ))


@router.get("/orders/{order_no}", response_model=APIResponse[OrderResponse])
async def get_order_detail(
    order_no: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取订单详情
    """
    order = await payment_service.get_order_by_no(db, order_no)
    
    if not order:
        raise HTTPException(
            status_code=404,
            detail=error_response(ErrorCode.ORDER_NOT_FOUND, "订单不存在")
        )
    
    if order.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail=error_response(ErrorCode.PERMISSION_DENIED, "无权查看此订单")
        )
    
    return success_response(OrderResponse(
        order_no=order.order_no,
        product_name=order.product_name,
        product_type=order.product_type.value,
        amount=order.amount,
        actual_amount=order.actual_amount,
        discount_amount=order.discount_amount,
        status=order.status,
        pay_method=order.pay_method,
        created_at=order.created_at,
        expire_at=order.expire_at
    ))


@router.post("/orders/{order_no}/cancel", response_model=APIResponse)
async def cancel_order(
    order_no: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    取消订单
    
    只能取消待支付的订单
    """
    order = await payment_service.get_order_by_no(db, order_no)
    
    if not order:
        raise HTTPException(
            status_code=404,
            detail=error_response(ErrorCode.ORDER_NOT_FOUND, "订单不存在")
        )
    
    if order.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail=error_response(ErrorCode.PERMISSION_DENIED, "无权操作此订单")
        )
    
    try:
        await payment_service.cancel_order(db, order)
        return success_response(None, "订单已取消")
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=error_response(ErrorCode.INVALID_PARAMS, str(e))
        )


@router.post("/notify/wechat")
async def wechat_notify(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    微信支付回调
    
    处理微信支付结果通知
    """
    # TODO: 验证签名
    # TODO: 解密通知数据
    # TODO: 处理支付结果
    
    # 这里是简化的处理逻辑
    body = await request.json()
    
    # 验证并处理
    # order_no = body.get("out_trade_no")
    # trade_no = body.get("transaction_id")
    # await payment_service.handle_payment_success(db, order_no, trade_no)
    
    return {"code": "SUCCESS", "message": "成功"}


@router.post("/notify/alipay")
async def alipay_notify(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    支付宝回调
    
    处理支付宝支付结果通知
    """
    # TODO: 验证签名
    # TODO: 处理支付结果
    
    form_data = await request.form()
    
    # 验证并处理
    # order_no = form_data.get("out_trade_no")
    # trade_no = form_data.get("trade_no")
    # trade_status = form_data.get("trade_status")
    # if trade_status == "TRADE_SUCCESS":
    #     await payment_service.handle_payment_success(db, order_no, trade_no)
    
    return "success"
