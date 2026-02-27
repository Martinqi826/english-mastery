"""
学习 API 路由
"""
from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.base import APIResponse, success_response
from app.schemas.learning import (
    ProgressResponse, 
    ProgressUpdate,
    CheckinRequest,
    CheckinResponse,
    StatsResponse
)
from app.services.learning_service import learning_service


router = APIRouter()


@router.get("/progress", response_model=APIResponse[ProgressResponse])
async def get_progress(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取学习进度
    
    返回各项技能进度、学习统计等
    """
    progress = await learning_service.get_progress(db, current_user.id)
    
    return success_response(ProgressResponse(
        vocabulary=progress.vocabulary,
        listening=progress.listening,
        reading=progress.reading,
        writing=progress.writing,
        speaking=progress.speaking,
        overall=progress.overall,
        current_day=progress.current_day,
        start_date=progress.start_date,
        total_study_time=progress.total_study_time,
        words_learned=progress.words_learned,
        streak_days=progress.streak_days
    ))


@router.put("/progress", response_model=APIResponse[ProgressResponse])
async def update_progress(
    update_data: ProgressUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    更新学习进度
    
    可更新各项技能进度，或增加学习时长/词汇数
    """
    progress = await learning_service.update_progress(
        db, 
        current_user.id, 
        update_data
    )
    
    return success_response(ProgressResponse(
        vocabulary=progress.vocabulary,
        listening=progress.listening,
        reading=progress.reading,
        writing=progress.writing,
        speaking=progress.speaking,
        overall=progress.overall,
        current_day=progress.current_day,
        start_date=progress.start_date,
        total_study_time=progress.total_study_time,
        words_learned=progress.words_learned,
        streak_days=progress.streak_days
    ), "进度更新成功")


@router.post("/checkin", response_model=APIResponse[CheckinResponse])
async def checkin(
    checkin_data: CheckinRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    今日打卡
    
    - 需要完成至少3项任务才能打卡
    - 一天只能打卡一次
    """
    if len(checkin_data.tasks) < 3:
        return success_response(
            None, 
            "需要完成至少3项任务才能打卡"
        )
    
    record = await learning_service.checkin(db, current_user.id, checkin_data)
    
    # 获取最新的连续打卡天数
    progress = await learning_service.get_progress(db, current_user.id)
    
    return success_response(CheckinResponse(
        id=record.id,
        checkin_date=record.checkin_date,
        tasks=record.tasks,
        study_time=record.study_time,
        note=record.note,
        streak_days=progress.streak_days
    ), "打卡成功！")


@router.get("/checkin/history", response_model=APIResponse)
async def get_checkin_history(
    start_date: Optional[date] = Query(None, description="开始日期"),
    end_date: Optional[date] = Query(None, description="结束日期"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取打卡历史
    
    可指定日期范围
    """
    records = await learning_service.get_checkin_history(
        db, 
        current_user.id,
        start_date,
        end_date
    )
    
    progress = await learning_service.get_progress(db, current_user.id)
    
    return success_response({
        "records": [
            {
                "id": r.id,
                "checkin_date": r.checkin_date.isoformat(),
                "tasks": r.tasks,
                "study_time": r.study_time,
                "note": r.note
            }
            for r in records
        ],
        "total_checkins": len(records),
        "current_streak": progress.streak_days
    })


@router.get("/today", response_model=APIResponse)
async def get_today_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取今日学习状态
    
    返回今日是否已打卡、已完成任务等
    """
    status = await learning_service.get_today_status(db, current_user.id)
    
    return success_response({
        "date": status["date"].isoformat(),
        "is_checked_in": status["is_checked_in"],
        "tasks": status["tasks"],
        "study_time": status["study_time"],
        "can_checkin": len(status["tasks"]) >= 3
    })


@router.get("/stats", response_model=APIResponse[StatsResponse])
async def get_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取学习统计
    
    返回综合学习数据统计
    """
    stats = await learning_service.get_stats(db, current_user.id)
    
    return success_response(StatsResponse(**stats))
