"""
内容模型
词汇、课程、学习材料
"""
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON, ForeignKey
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.sql import func

from app.database import Base


class ContentLevel(str, Enum):
    """内容难度等级"""
    BEGINNER = "beginner"       # 初级
    INTERMEDIATE = "intermediate"   # 中级
    ADVANCED = "advanced"       # 高级


class Vocabulary(Base):
    """词汇表"""
    
    __tablename__ = "vocabularies"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 词汇信息
    word = Column(String(100), nullable=False, index=True, comment="单词")
    phonetic = Column(String(100), nullable=True, comment="音标")
    pronunciation_url = Column(String(500), nullable=True, comment="发音URL")
    
    # 释义
    translation = Column(String(500), nullable=False, comment="中文释义")
    definition = Column(Text, nullable=True, comment="英文释义")
    
    # 例句
    example = Column(Text, nullable=True, comment="例句")
    example_translation = Column(Text, nullable=True, comment="例句翻译")
    
    # 分类
    day = Column(Integer, nullable=False, index=True, comment="所属天数(1-30)")
    category = Column(String(50), nullable=True, comment="分类(商务/学术等)")
    level = Column(
        SQLEnum(ContentLevel), 
        default=ContentLevel.INTERMEDIATE,
        comment="难度等级"
    )
    
    # 扩展信息
    synonyms = Column(JSON, default=list, comment="同义词")
    antonyms = Column(JSON, default=list, comment="反义词")
    collocations = Column(JSON, default=list, comment="常见搭配")
    
    # 状态
    is_active = Column(Boolean, default=True, comment="是否启用")
    is_premium = Column(Boolean, default=False, comment="是否会员专属")
    
    # 时间
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(
        DateTime, 
        server_default=func.now(), 
        onupdate=func.now(),
        comment="更新时间"
    )
    
    def __repr__(self):
        return f"<Vocabulary(word={self.word}, day={self.day})>"


class Course(Base):
    """课程表"""
    
    __tablename__ = "courses"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 课程信息
    title = Column(String(200), nullable=False, comment="课程标题")
    description = Column(Text, nullable=True, comment="课程描述")
    cover_url = Column(String(500), nullable=True, comment="封面图URL")
    
    # 分类
    type = Column(String(50), nullable=False, comment="类型(listening/reading/writing)")
    level = Column(
        SQLEnum(ContentLevel), 
        default=ContentLevel.INTERMEDIATE,
        comment="难度等级"
    )
    day = Column(Integer, nullable=True, index=True, comment="所属天数")
    
    # 内容
    content = Column(JSON, default=dict, comment="课程内容(JSON结构)")
    duration = Column(Integer, default=0, comment="预计时长(分钟)")
    
    # 状态
    is_active = Column(Boolean, default=True, comment="是否启用")
    is_premium = Column(Boolean, default=False, comment="是否会员专属")
    sort_order = Column(Integer, default=0, comment="排序权重")
    
    # 时间
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(
        DateTime, 
        server_default=func.now(), 
        onupdate=func.now(),
        comment="更新时间"
    )
    
    def __repr__(self):
        return f"<Course(title={self.title}, type={self.type})>"


class LearningMaterial(Base):
    """学习材料表（音频、视频等）"""
    
    __tablename__ = "learning_materials"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 关联课程
    course_id = Column(
        Integer, 
        ForeignKey("courses.id", ondelete="SET NULL"), 
        nullable=True,
        index=True,
        comment="关联课程ID"
    )
    
    # 材料信息
    title = Column(String(200), nullable=False, comment="材料标题")
    type = Column(String(50), nullable=False, comment="类型(audio/video/document)")
    
    # 资源
    url = Column(String(500), nullable=False, comment="资源URL")
    thumbnail_url = Column(String(500), nullable=True, comment="缩略图URL")
    duration = Column(Integer, default=0, comment="时长(秒)")
    size = Column(Integer, default=0, comment="文件大小(字节)")
    
    # 内容
    transcript = Column(Text, nullable=True, comment="文字稿/字幕")
    description = Column(Text, nullable=True, comment="描述")
    
    # 状态
    is_active = Column(Boolean, default=True, comment="是否启用")
    is_premium = Column(Boolean, default=False, comment="是否会员专属")
    
    # 时间
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(
        DateTime, 
        server_default=func.now(), 
        onupdate=func.now(),
        comment="更新时间"
    )
    
    def __repr__(self):
        return f"<LearningMaterial(title={self.title}, type={self.type})>"
