"""
配置管理模块
使用 pydantic-settings 从环境变量读取配置
支持 MySQL 和 PostgreSQL 双数据库
"""
from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    # 应用配置
    APP_NAME: str = "English Mastery API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # API 配置
    API_V1_PREFIX: str = "/api/v1"
    
    # 数据库配置 - 支持直接 DATABASE_URL 或分开配置
    # Railway 自动注入 DATABASE_URL，我们用 DATABASE_URL_ENV 接收
    DATABASE_URL_ENV: Optional[str] = None
    DATABASE_URL: Optional[str] = None  # 也支持标准的 DATABASE_URL
    DB_TYPE: str = "postgresql"  # postgresql 或 mysql
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "postgres"
    DB_PASSWORD: str = ""
    DB_NAME: str = "english_mastery"
    
    @property
    def ASYNC_DATABASE_URL(self) -> str:
        """异步数据库连接 URL"""
        # 优先使用环境变量中的 DATABASE_URL（Railway 自动注入）
        url = self.DATABASE_URL_ENV or self.DATABASE_URL
        if url:
            # Railway PostgreSQL URL 需要转换为 asyncpg 格式
            if url.startswith("postgresql://"):
                return url.replace("postgresql://", "postgresql+asyncpg://")
            elif url.startswith("postgres://"):
                return url.replace("postgres://", "postgresql+asyncpg://")
            return url
        
        # 手动配置
        if self.DB_TYPE == "postgresql":
            return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        else:
            return f"mysql+aiomysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"
    
    @property
    def SYNC_DATABASE_URL(self) -> str:
        """同步数据库连接 URL (用于 Alembic)"""
        url = self.DATABASE_URL_ENV or self.DATABASE_URL
        if url:
            # 确保是同步驱动格式
            if "asyncpg" in url:
                return url.replace("+asyncpg", "")
            if url.startswith("postgres://"):
                return url.replace("postgres://", "postgresql://")
            return url
        
        if self.DB_TYPE == "postgresql":
            return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        else:
            return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"
    
    # Redis 配置
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0
    
    @property
    def REDIS_URL(self) -> str:
        """Redis 连接 URL"""
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    # JWT 配置
    JWT_SECRET_KEY: str = "your-super-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # 密码加密配置
    BCRYPT_ROUNDS: int = 12
    
    # CORS 配置
    CORS_ORIGINS: str = "*"
    
    @property
    def CORS_ORIGIN_LIST(self) -> list:
        """解析 CORS 域名列表"""
        if self.CORS_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    # 微信支付配置
    WECHAT_MCHID: str = ""
    WECHAT_APPID: str = ""
    WECHAT_API_KEY: str = ""
    WECHAT_CERT_SERIAL_NO: str = ""
    WECHAT_PRIVATE_KEY_PATH: str = ""
    WECHAT_NOTIFY_URL: str = ""
    
    # 支付宝配置
    ALIPAY_APP_ID: str = ""
    ALIPAY_PRIVATE_KEY: str = ""
    ALIPAY_PUBLIC_KEY: str = ""
    ALIPAY_NOTIFY_URL: str = ""
    
    # 腾讯云 COS 配置
    COS_SECRET_ID: str = ""
    COS_SECRET_KEY: str = ""
    COS_REGION: str = "ap-guangzhou"
    COS_BUCKET: str = ""
    
    # 限流配置
    RATE_LIMIT_PER_MINUTE: int = 100
    
    # AI 服务配置 (Claude API)
    ANTHROPIC_API_KEY: str = ""


@lru_cache()
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()


settings = get_settings()
