"""
学习服务
处理学习进度、打卡、统计等
"""
from datetime import date, datetime, timedelta
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.models.user import User
from app.models.learning import LearningProgress, CheckinRecord
from app.schemas.learning import ProgressUpdate, CheckinRequest


class LearningService:
    """学习服务类"""
    
    @staticmethod
    async def get_progress(
        db: AsyncSession,
        user_id: int
    ) -> LearningProgress:
        """
        获取用户学习进度
        """
        result = await db.execute(
            select(LearningProgress).where(LearningProgress.user_id == user_id)
        )
        progress = result.scalar_one_or_none()
        
        if not progress:
            # 创建默认进度记录
            progress = LearningProgress(user_id=user_id)
            db.add(progress)
            await db.commit()
            await db.refresh(progress)
        
        return progress
    
    @staticmethod
    async def update_progress(
        db: AsyncSession,
        user_id: int,
        update_data: ProgressUpdate
    ) -> LearningProgress:
        """
        更新学习进度
        """
        progress = await LearningService.get_progress(db, user_id)
        
        # 更新各项技能进度
        if update_data.vocabulary is not None:
            progress.vocabulary = update_data.vocabulary
        if update_data.listening is not None:
            progress.listening = update_data.listening
        if update_data.reading is not None:
            progress.reading = update_data.reading
        if update_data.writing is not None:
            progress.writing = update_data.writing
        if update_data.speaking is not None:
            progress.speaking = update_data.speaking
        
        # 增量更新
        if update_data.add_study_time:
            progress.total_study_time += update_data.add_study_time
        if update_data.add_words_learned:
            progress.words_learned += update_data.add_words_learned
        
        # 重新计算总体进度
        progress.overall = progress.calculate_overall()
        
        # 更新当前天数
        if progress.start_date:
            days_diff = (date.today() - progress.start_date).days
            progress.current_day = min(30, max(1, days_diff + 1))
        
        await db.commit()
        await db.refresh(progress)
        
        return progress
    
    @staticmethod
    async def checkin(
        db: AsyncSession,
        user_id: int,
        checkin_data: CheckinRequest
    ) -> CheckinRecord:
        """
        今日打卡
        """
        today = date.today()
        
        # 检查今日是否已打卡
        result = await db.execute(
            select(CheckinRecord).where(
                and_(
                    CheckinRecord.user_id == user_id,
                    CheckinRecord.checkin_date == today
                )
            )
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            # 更新今日打卡记录
            existing.tasks = checkin_data.tasks
            existing.study_time = checkin_data.study_time
            existing.note = checkin_data.note
            await db.commit()
            await db.refresh(existing)
            record = existing
        else:
            # 创建新打卡记录
            record = CheckinRecord(
                user_id=user_id,
                checkin_date=today,
                tasks=checkin_data.tasks,
                study_time=checkin_data.study_time,
                note=checkin_data.note
            )
            db.add(record)
            await db.commit()
            await db.refresh(record)
        
        # 更新连续打卡天数
        streak = await LearningService._calculate_streak(db, user_id)
        
        # 更新学习进度中的连续打卡天数
        progress = await LearningService.get_progress(db, user_id)
        progress.streak_days = streak
        progress.total_study_time += checkin_data.study_time
        await db.commit()
        
        return record
    
    @staticmethod
    async def get_checkin_history(
        db: AsyncSession,
        user_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[CheckinRecord]:
        """
        获取打卡历史
        """
        query = select(CheckinRecord).where(
            CheckinRecord.user_id == user_id
        )
        
        if start_date:
            query = query.where(CheckinRecord.checkin_date >= start_date)
        if end_date:
            query = query.where(CheckinRecord.checkin_date <= end_date)
        
        query = query.order_by(CheckinRecord.checkin_date.desc())
        
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_today_status(
        db: AsyncSession,
        user_id: int
    ) -> dict:
        """
        获取今日学习状态
        """
        today = date.today()
        
        # 查询今日打卡记录
        result = await db.execute(
            select(CheckinRecord).where(
                and_(
                    CheckinRecord.user_id == user_id,
                    CheckinRecord.checkin_date == today
                )
            )
        )
        record = result.scalar_one_or_none()
        
        return {
            "date": today,
            "is_checked_in": record is not None,
            "tasks": record.tasks if record else [],
            "study_time": record.study_time if record else 0
        }
    
    @staticmethod
    async def get_stats(
        db: AsyncSession,
        user_id: int
    ) -> dict:
        """
        获取学习统计数据
        """
        progress = await LearningService.get_progress(db, user_id)
        
        # 获取总打卡次数
        result = await db.execute(
            select(func.count(CheckinRecord.id)).where(
                CheckinRecord.user_id == user_id
            )
        )
        checkin_count = result.scalar() or 0
        
        # 计算最长连续打卡
        longest_streak = await LearningService._calculate_longest_streak(db, user_id)
        
        # 计算日均学习时长
        avg_daily_time = 0
        if checkin_count > 0:
            avg_daily_time = round(progress.total_study_time / checkin_count, 1)
        
        return {
            "current_day": progress.current_day,
            "total_days": 30,
            "completion_rate": round(progress.overall, 1),
            "total_study_time": progress.total_study_time,
            "avg_daily_time": avg_daily_time,
            "words_learned": progress.words_learned,
            "words_total": 900,  # 30天 * 30词
            "checkin_count": checkin_count,
            "current_streak": progress.streak_days,
            "longest_streak": longest_streak,
            "skill_progress": {
                "vocabulary": progress.vocabulary,
                "listening": progress.listening,
                "reading": progress.reading,
                "writing": progress.writing,
                "speaking": progress.speaking
            }
        }
    
    @staticmethod
    async def _calculate_streak(
        db: AsyncSession,
        user_id: int
    ) -> int:
        """
        计算当前连续打卡天数
        """
        today = date.today()
        streak = 0
        current_date = today
        
        while True:
            result = await db.execute(
                select(CheckinRecord).where(
                    and_(
                        CheckinRecord.user_id == user_id,
                        CheckinRecord.checkin_date == current_date
                    )
                )
            )
            record = result.scalar_one_or_none()
            
            if record:
                streak += 1
                current_date -= timedelta(days=1)
            else:
                break
        
        return streak
    
    @staticmethod
    async def _calculate_longest_streak(
        db: AsyncSession,
        user_id: int
    ) -> int:
        """
        计算最长连续打卡天数
        """
        result = await db.execute(
            select(CheckinRecord.checkin_date).where(
                CheckinRecord.user_id == user_id
            ).order_by(CheckinRecord.checkin_date)
        )
        dates = [row[0] for row in result.fetchall()]
        
        if not dates:
            return 0
        
        longest = 1
        current = 1
        
        for i in range(1, len(dates)):
            if (dates[i] - dates[i-1]).days == 1:
                current += 1
                longest = max(longest, current)
            else:
                current = 1
        
        return longest


# 创建服务实例
learning_service = LearningService()
