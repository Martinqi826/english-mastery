"""
FastAPI 应用入口
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import os

from app.config import settings


# 配置日志
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# 全局状态
db_connected = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    启动时初始化数据库和 Redis 连接
    关闭时清理资源
    """
    global db_connected
    logger.info("Starting application...")
    logger.info(f"PORT: {os.environ.get('PORT', 'not set')}")
    logger.info(f"DATABASE_URL exists: {bool(settings.DATABASE_URL)}")
    
    # 延迟导入，避免启动时立即连接数据库
    try:
        from app.database import init_db, close_db
        await init_db()
        db_connected = True
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database init failed: {e}")
        db_connected = False
    
    # 连接 Redis（可选，Railway 免费层可以不用）
    try:
        from app.utils.redis_client import redis_client
        await redis_client.connect()
        logger.info("Redis connected")
    except Exception as e:
        logger.warning(f"Redis connection failed (optional): {e}")
    
    yield
    
    # 清理资源
    logger.info("Shutting down...")
    try:
        from app.utils.redis_client import redis_client
        await redis_client.disconnect()
    except:
        pass
    try:
        from app.database import close_db
        await close_db()
    except:
        pass


# 创建 FastAPI 应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="English Mastery 英语进阶学习平台 API",
    docs_url="/docs",  # 始终开启文档，方便验证阶段调试
    redoc_url="/redoc",
    lifespan=lifespan
)


# CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGIN_LIST,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理器"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "code": 1000,
            "message": "服务器内部错误",
            "data": None
        }
    )


# 健康检查 - 必须在路由注册之前定义
@app.get("/health", tags=["系统"])
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "database": "connected" if db_connected else "disconnected"
    }


# 根路径
@app.get("/", tags=["系统"])
async def root():
    """API 根路径"""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }


# 延迟注册 API 路由（仅在数据库连接后才需要）
try:
    from app.api.v1 import api_router
    app.include_router(api_router, prefix=settings.API_V1_PREFIX)
    logger.info("API routes registered")
except Exception as e:
    logger.error(f"Failed to register API routes: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000)),
        reload=settings.DEBUG
    )
