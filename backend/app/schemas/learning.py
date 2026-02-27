"""
学习数据相关 Schema
"""
from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class ProgressResponse(BaseModel):
    """学习进度响应"""
    vocabulary: float = 0
    listening: float = 0
    reading: float = 0
    writing: float = 0
    speaking: float = 0
    overall: float = 0
    
    current_day: int = 1
    start_date: date
    total_study_time: int = 0
    words_learned: int = 0
    streak_days: int = 0
    
    class Config:
        from_attributes = True


class ProgressUpdate(BaseModel):
    """学习进度更新请求"""
    vocabulary: Optional[float] = Field(None, ge=0, le=100)
    listening: Optional[float] = Field(None, ge=0, le=100)
    reading: Optional[float] = Field(None, ge=0, le=100)
    writing: Optional[float] = Field(None, ge=0, le=100)
    speaking: Optional[float] = Field(None, ge=0, le=100)
    
    # 增量更新
    add_study_time: Optional[int] = Field(None, ge=0, description="增加学习时长(分钟)")
    add_words_learned: Optional[int] = Field(None, ge=0, description="增加已学词汇数")


class CheckinRequest(BaseModel):
    """打卡请求"""
    tasks: List[str] = Field(..., min_length=1, description="完成的任务列表")
    study_time: int = Field(0, ge=0, description="学习时长(分钟)")
    note: Optional[str] = Field(None, max_length=500, description="学习备注")


class CheckinResponse(BaseModel):
    """打卡响应"""
    id: int
    checkin_date: date
    tasks: List[str]
    study_time: int
    note: Optional[str] = None
    streak_days: int = Field(..., description="当前连续打卡天数")
    
    class Config:
        from_attributes = True


class CheckinHistoryResponse(BaseModel):
    """打卡历史响应"""
    records: List[CheckinResponse]
    total_checkins: int
    current_streak: int
    longest_streak: int


class StatsResponse(BaseModel):
    """学习统计响应"""
    # 总体统计
    current_day: int
    total_days: int = 30
    completion_rate: float = Field(..., description="完成率(%)")
    
    # 时间统计
    total_study_time: int = Field(..., description="总学习时长(分钟)")
    avg_daily_time: float = Field(..., description="日均学习时长(分钟)")
    
    # 词汇统计
    words_learned: int
    words_total: int = Field(default=900, description="总词汇数(30天*30词)")
    
    # 打卡统计
    checkin_count: int
    current_streak: int
    longest_streak: int
    
    # 各项技能
    skill_progress: dict = Field(
        default_factory=dict, 
        description="各技能进度"
    )


class DailyTaskStatus(BaseModel):
    """每日任务状态"""
    task_id: str
    task_name: str
    completed: bool = False
    completed_at: Optional[datetime] = None


class TodayStatusResponse(BaseModel):
    """今日学习状态"""
    date: date
    is_checked_in: bool = False
    tasks: List[DailyTaskStatus]
    study_time: int = 0
    can_checkin: bool = Field(..., description="是否可以打卡(完成>=3项任务)")
