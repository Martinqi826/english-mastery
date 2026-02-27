"""
学习记录模型
"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, DateTime, Date, Float, ForeignKey, JSON, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class LearningProgress(Base):
    """学习进度表"""
    
    __tablename__ = "learning_progress"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(
        Integer, 
        ForeignKey("users.id", ondelete="CASCADE"), 
        unique=True, 
        nullable=False,
        index=True,
        comment="用户ID"
    )
    
    # 各项技能进度 (0-100)
    vocabulary = Column(Float, default=0, comment="词汇进度")
    listening = Column(Float, default=0, comment="听力进度")
    reading = Column(Float, default=0, comment="阅读进度")
    writing = Column(Float, default=0, comment="写作进度")
    speaking = Column(Float, default=0, comment="口语进度")
    overall = Column(Float, default=0, comment="总体进度")
    
    # 学习统计
    current_day = Column(Integer, default=1, comment="当前学习天数")
    start_date = Column(Date, default=date.today, comment="开始学习日期")
    total_study_time = Column(Integer, default=0, comment="总学习时长(分钟)")
    words_learned = Column(Integer, default=0, comment="已学词汇数")
    streak_days = Column(Integer, default=0, comment="连续打卡天数")
    
    # 时间
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(
        DateTime, 
        server_default=func.now(), 
        onupdate=func.now(),
        comment="更新时间"
    )
    
    # 关联
    user = relationship("User", back_populates="learning_progress")
    
    def calculate_overall(self) -> float:
        """计算总体进度（加权平均）"""
        weights = {
            "vocabulary": 0.2,
            "listening": 0.2,
            "reading": 0.2,
            "writing": 0.2,
            "speaking": 0.2
        }
        total = (
            self.vocabulary * weights["vocabulary"] +
            self.listening * weights["listening"] +
            self.reading * weights["reading"] +
            self.writing * weights["writing"] +
            self.speaking * weights["speaking"]
        )
        return round(total, 1)
    
    def __repr__(self):
        return f"<LearningProgress(user_id={self.user_id}, overall={self.overall})>"


class CheckinRecord(Base):
    """打卡记录表"""
    
    __tablename__ = "checkin_records"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(
        Integer, 
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False,
        index=True,
        comment="用户ID"
    )
    
    # 打卡信息
    checkin_date = Column(Date, nullable=False, comment="打卡日期")
    tasks = Column(JSON, default=list, comment="完成的任务列表")
    study_time = Column(Integer, default=0, comment="学习时长(分钟)")
    
    # 备注
    note = Column(Text, nullable=True, comment="学习备注")
    
    # 时间
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    
    # 关联
    user = relationship("User", back_populates="checkin_records")
    
    # 复合唯一索引：一个用户一天只能打卡一次
    __table_args__ = (
        {"mysql_charset": "utf8mb4"},
    )
    
    def __repr__(self):
        return f"<CheckinRecord(user_id={self.user_id}, date={self.checkin_date})>"
