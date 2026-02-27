"""
内容服务
处理词汇、课程等内容
"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.models.content import Vocabulary, Course, LearningMaterial
from app.models.membership import Membership, MembershipLevel
from app.utils.redis_client import redis_client


class ContentService:
    """内容服务类"""
    
    @staticmethod
    async def get_vocabulary_by_day(
        db: AsyncSession,
        day: int,
        user_id: Optional[int] = None,
        membership_level: MembershipLevel = MembershipLevel.FREE
    ) -> List[Vocabulary]:
        """
        获取指定天数的词汇
        """
        query = select(Vocabulary).where(
            and_(
                Vocabulary.day == day,
                Vocabulary.is_active == True
            )
        )
        
        # 免费用户只能获取非会员专属词汇
        if membership_level == MembershipLevel.FREE:
            query = query.where(Vocabulary.is_premium == False)
        
        query = query.order_by(Vocabulary.id)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_vocabulary_by_id(
        db: AsyncSession,
        word_id: int
    ) -> Optional[Vocabulary]:
        """
        根据 ID 获取词汇
        """
        result = await db.execute(
            select(Vocabulary).where(Vocabulary.id == word_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def search_vocabulary(
        db: AsyncSession,
        keyword: str,
        limit: int = 20
    ) -> List[Vocabulary]:
        """
        搜索词汇
        """
        result = await db.execute(
            select(Vocabulary).where(
                and_(
                    Vocabulary.word.ilike(f"%{keyword}%"),
                    Vocabulary.is_active == True
                )
            ).limit(limit)
        )
        return result.scalars().all()
    
    @staticmethod
    async def get_courses(
        db: AsyncSession,
        course_type: Optional[str] = None,
        day: Optional[int] = None,
        membership_level: MembershipLevel = MembershipLevel.FREE
    ) -> List[Course]:
        """
        获取课程列表
        """
        query = select(Course).where(Course.is_active == True)
        
        if course_type:
            query = query.where(Course.type == course_type)
        
        if day:
            query = query.where(Course.day == day)
        
        # 免费用户只能获取非会员专属课程
        if membership_level == MembershipLevel.FREE:
            query = query.where(Course.is_premium == False)
        
        query = query.order_by(Course.sort_order, Course.id)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_course_by_id(
        db: AsyncSession,
        course_id: int
    ) -> Optional[Course]:
        """
        根据 ID 获取课程详情
        """
        result = await db.execute(
            select(Course).where(Course.id == course_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_course_materials(
        db: AsyncSession,
        course_id: int
    ) -> List[LearningMaterial]:
        """
        获取课程相关学习材料
        """
        result = await db.execute(
            select(LearningMaterial).where(
                and_(
                    LearningMaterial.course_id == course_id,
                    LearningMaterial.is_active == True
                )
            )
        )
        return result.scalars().all()
    
    @staticmethod
    async def get_user_membership_level(
        db: AsyncSession,
        user_id: int
    ) -> MembershipLevel:
        """
        获取用户会员等级
        """
        # 先从缓存获取
        cached = await redis_client.get_user_membership(user_id)
        if cached:
            return MembershipLevel(cached.get("level", "free"))
        
        # 从数据库获取
        result = await db.execute(
            select(Membership).where(Membership.user_id == user_id)
        )
        membership = result.scalar_one_or_none()
        
        if not membership:
            return MembershipLevel.FREE
        
        # 检查是否过期
        if not membership.is_active:
            return MembershipLevel.FREE
        
        # 缓存会员状态
        await redis_client.cache_user_membership(
            user_id,
            {
                "level": membership.level.value,
                "is_active": membership.is_active,
                "end_date": membership.end_date.isoformat() if membership.end_date else None
            },
            ttl=3600  # 缓存1小时
        )
        
        return membership.level


# 创建服务实例
content_service = ContentService()
