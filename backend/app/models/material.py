"""
用户素材模型
用户自定义学习素材及 AI 生成内容
"""
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON, ForeignKey
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class MaterialSourceType(str, Enum):
    """素材来源类型"""
    TEXT = "text"       # 文本粘贴
    URL = "url"         # 网页链接


class MaterialStatus(str, Enum):
    """素材处理状态"""
    PENDING = "pending"         # 待处理
    PROCESSING = "processing"   # 处理中
    COMPLETED = "completed"     # 已完成
    FAILED = "failed"           # 处理失败


class UserMaterial(Base):
    """用户素材表"""
    
    __tablename__ = "user_materials"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 关联用户
    user_id = Column(
        Integer, 
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False,
        index=True,
        comment="用户ID"
    )
    
    # 素材信息
    title = Column(String(200), nullable=False, comment="素材标题")
    source_type = Column(
        SQLEnum(MaterialSourceType),
        nullable=False,
        comment="素材来源类型"
    )
    source_content = Column(Text, nullable=False, comment="素材原文内容")
    source_url = Column(String(1000), nullable=True, comment="来源URL（如果是链接）")
    
    # 处理状态
    status = Column(
        SQLEnum(MaterialStatus),
        default=MaterialStatus.PENDING,
        nullable=False,
        comment="处理状态"
    )
    error_message = Column(String(500), nullable=True, comment="错误信息")
    
    # 统计信息
    word_count = Column(Integer, default=0, comment="单词数量")
    generated_vocab_count = Column(Integer, default=0, comment="生成的词汇数量")
    generated_question_count = Column(Integer, default=0, comment="生成的题目数量")
    
    # 时间
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(
        DateTime, 
        server_default=func.now(), 
        onupdate=func.now(),
        comment="更新时间"
    )
    processed_at = Column(DateTime, nullable=True, comment="处理完成时间")
    
    # 关联
    vocabularies = relationship(
        "GeneratedVocabulary",
        back_populates="material",
        cascade="all, delete-orphan"
    )
    questions = relationship(
        "ReadingQuestion",
        back_populates="material",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<UserMaterial(id={self.id}, title={self.title}, status={self.status})>"


class GeneratedVocabulary(Base):
    """AI 生成的词汇表"""
    
    __tablename__ = "generated_vocabularies"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 关联素材
    material_id = Column(
        Integer,
        ForeignKey("user_materials.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="素材ID"
    )
    
    # 词汇信息
    word = Column(String(100), nullable=False, index=True, comment="单词")
    phonetic = Column(String(100), nullable=True, comment="音标")
    translation = Column(String(500), nullable=False, comment="中文释义")
    definition = Column(Text, nullable=True, comment="英文释义")
    
    # 例句
    example = Column(Text, nullable=True, comment="例句")
    example_translation = Column(Text, nullable=True, comment="例句翻译")
    
    # 扩展信息
    synonyms = Column(JSON, default=list, comment="同义词")
    collocations = Column(JSON, default=list, comment="常见搭配")
    difficulty = Column(Integer, default=3, comment="难度等级(1-5)")
    
    # 学习状态
    is_learned = Column(Boolean, default=False, comment="是否已学习")
    is_mastered = Column(Boolean, default=False, comment="是否已掌握")
    review_count = Column(Integer, default=0, comment="复习次数")
    
    # 排序
    sort_order = Column(Integer, default=0, comment="排序顺序")
    
    # 时间
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    
    # 关联
    material = relationship("UserMaterial", back_populates="vocabularies")
    
    def __repr__(self):
        return f"<GeneratedVocabulary(word={self.word}, material_id={self.material_id})>"


class ReadingQuestion(Base):
    """阅读理解题目表"""
    
    __tablename__ = "reading_questions"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 关联素材
    material_id = Column(
        Integer,
        ForeignKey("user_materials.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="素材ID"
    )
    
    # 题目信息
    question_text = Column(Text, nullable=False, comment="题目内容")
    question_type = Column(
        String(50), 
        default="choice",
        comment="题目类型(choice/truefalse/fill)"
    )
    
    # 选项（JSON 格式：["A选项", "B选项", "C选项", "D选项"]）
    options = Column(JSON, default=list, comment="选项列表")
    
    # 答案
    correct_answer = Column(Integer, nullable=False, comment="正确答案索引(0-3)")
    explanation = Column(Text, nullable=True, comment="答案解析")
    
    # 排序
    sort_order = Column(Integer, default=0, comment="排序顺序")
    
    # 用户答题记录
    user_answer = Column(Integer, nullable=True, comment="用户答案")
    is_correct = Column(Boolean, nullable=True, comment="是否回答正确")
    answered_at = Column(DateTime, nullable=True, comment="答题时间")
    
    # 时间
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    
    # 关联
    material = relationship("UserMaterial", back_populates="questions")
    
    def __repr__(self):
        return f"<ReadingQuestion(id={self.id}, material_id={self.material_id})>"
