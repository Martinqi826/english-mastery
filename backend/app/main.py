"""
FastAPI 应用入口 - 极简启动版本
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import os

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# 从环境变量读取配置（避免导入复杂模块）
APP_NAME = os.environ.get("APP_NAME", "English Mastery API")
APP_VERSION = "1.0.0"
CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*")

# 创建 FastAPI 应用（不使用 lifespan，确保快速启动）
app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="English Mastery 英语进阶学习平台 API",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS 中间件
cors_origins = ["*"] if CORS_ORIGINS == "*" else [o.strip() for o in CORS_ORIGINS.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 健康检查 - 最先定义，确保能响应
@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "version": APP_VERSION,
        "port": os.environ.get("PORT", "unknown")
    }

# 根路径
@app.get("/")
async def root():
    """API 根路径"""
    return {
        "message": f"Welcome to {APP_NAME}",
        "version": APP_VERSION,
        "docs": "/docs"
    }

# 启动时打印信息
logger.info(f"Starting {APP_NAME} v{APP_VERSION}")
logger.info(f"PORT environment variable: {os.environ.get('PORT', 'not set')}")

# 延迟加载数据库和复杂路由（在后台，不阻塞启动）
@app.on_event("startup")
async def startup_event():
    """应用启动后的初始化"""
    logger.info("Application started, initializing components...")
    
    # 尝试初始化数据库
    try:
        from app.database import init_db
        await init_db()
        logger.info("Database initialized")
    except Exception as e:
        logger.warning(f"Database init skipped: {e}")
    
    # 注册 API 路由
    try:
        from app.config import settings
        from app.api.v1 import api_router
        app.include_router(api_router, prefix=settings.API_V1_PREFIX)
        logger.info("API routes registered")
    except Exception as e:
        logger.warning(f"API routes registration skipped: {e}")


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"Starting uvicorn on port {port}")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port
    )
