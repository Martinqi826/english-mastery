"""
Redis 客户端模块
用于缓存、会话管理、限流等
"""
import json
from typing import Any, Optional
import redis.asyncio as redis

from app.config import settings


class RedisClient:
    """Redis 异步客户端封装"""
    
    def __init__(self):
        self._client: Optional[redis.Redis] = None
    
    async def connect(self):
        """建立 Redis 连接"""
        self._client = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
    
    async def disconnect(self):
        """关闭 Redis 连接"""
        if self._client:
            await self._client.close()
    
    @property
    def client(self) -> redis.Redis:
        """获取 Redis 客户端"""
        if not self._client:
            raise RuntimeError("Redis client not connected")
        return self._client
    
    # ==================== 基础操作 ====================
    
    async def get(self, key: str) -> Optional[str]:
        """获取字符串值"""
        return await self.client.get(key)
    
    async def set(
        self, 
        key: str, 
        value: str, 
        expire: Optional[int] = None
    ) -> bool:
        """设置字符串值"""
        return await self.client.set(key, value, ex=expire)
    
    async def delete(self, key: str) -> int:
        """删除键"""
        return await self.client.delete(key)
    
    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        return await self.client.exists(key) > 0
    
    async def expire(self, key: str, seconds: int) -> bool:
        """设置过期时间"""
        return await self.client.expire(key, seconds)
    
    # ==================== JSON 操作 ====================
    
    async def get_json(self, key: str) -> Optional[Any]:
        """获取 JSON 对象"""
        data = await self.get(key)
        if data:
            return json.loads(data)
        return None
    
    async def set_json(
        self, 
        key: str, 
        value: Any, 
        expire: Optional[int] = None
    ) -> bool:
        """设置 JSON 对象"""
        return await self.set(key, json.dumps(value, ensure_ascii=False), expire)
    
    # ==================== 缓存操作 ====================
    
    async def cache_get(self, key: str) -> Optional[Any]:
        """从缓存获取数据"""
        return await self.get_json(f"cache:{key}")
    
    async def cache_set(
        self, 
        key: str, 
        value: Any, 
        ttl: int = 3600
    ) -> bool:
        """设置缓存数据"""
        return await self.set_json(f"cache:{key}", value, ttl)
    
    async def cache_delete(self, key: str) -> int:
        """删除缓存"""
        return await self.delete(f"cache:{key}")
    
    # ==================== 会话管理 ====================
    
    async def store_refresh_token(
        self, 
        user_id: int, 
        token: str, 
        expire_days: int = 7
    ) -> bool:
        """存储刷新令牌"""
        key = f"refresh_token:{user_id}"
        return await self.set(key, token, expire_days * 86400)
    
    async def get_refresh_token(self, user_id: int) -> Optional[str]:
        """获取刷新令牌"""
        return await self.get(f"refresh_token:{user_id}")
    
    async def delete_refresh_token(self, user_id: int) -> int:
        """删除刷新令牌（退出登录）"""
        return await self.delete(f"refresh_token:{user_id}")
    
    async def blacklist_token(self, token: str, expire: int = 900) -> bool:
        """将 Token 加入黑名单"""
        return await self.set(f"blacklist:{token}", "1", expire)
    
    async def is_token_blacklisted(self, token: str) -> bool:
        """检查 Token 是否在黑名单中"""
        return await self.exists(f"blacklist:{token}")
    
    # ==================== 限流 ====================
    
    async def check_rate_limit(
        self, 
        key: str, 
        limit: int = 100, 
        window: int = 60
    ) -> tuple[bool, int]:
        """
        检查限流
        返回 (是否允许, 剩余次数)
        """
        full_key = f"rate_limit:{key}"
        current = await self.client.incr(full_key)
        
        if current == 1:
            await self.expire(full_key, window)
        
        if current > limit:
            return False, 0
        
        return True, limit - current
    
    # ==================== 用户状态缓存 ====================
    
    async def cache_user_membership(
        self, 
        user_id: int, 
        membership_data: dict, 
        ttl: int = 3600
    ) -> bool:
        """缓存用户会员状态"""
        return await self.set_json(
            f"membership:{user_id}", 
            membership_data, 
            ttl
        )
    
    async def get_user_membership(self, user_id: int) -> Optional[dict]:
        """获取用户会员状态缓存"""
        return await self.get_json(f"membership:{user_id}")
    
    async def invalidate_user_membership(self, user_id: int) -> int:
        """使用户会员状态缓存失效"""
        return await self.delete(f"membership:{user_id}")


# 全局 Redis 客户端实例
redis_client = RedisClient()
