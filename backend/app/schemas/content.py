"""
内容相关 Schema
词汇、课程等
"""
from typing import Optional, List
from pydantic import BaseModel, Field


class VocabularyResponse(BaseModel):
    """词汇响应"""
    id: int
    word: str
    phonetic: Optional[str] = None
    pronunciation_url: Optional[str] = None
    translation: str
    definition: Optional[str] = None
    example: Optional[str] = None
    example_translation: Optional[str] = None
    day: int
    category: Optional[str] = None
    level: str = "intermediate"
    synonyms: List[str] = []
    antonyms: List[str] = []
    collocations: List[str] = []
    
    class Config:
        from_attributes = True


class VocabularyListResponse(BaseModel):
    """词汇列表响应"""
    day: int
    words: List[VocabularyResponse]
    total: int
    learned_count: int = 0


class WordLearnedRequest(BaseModel):
    """标记词汇已学请求"""
    word_id: int


class UserVocabularyProgress(BaseModel):
    """用户词汇学习进度"""
    total_words: int
    learned_words: int
    today_words: int
    today_learned: int
    completion_rate: float


class CourseResponse(BaseModel):
    """课程响应"""
    id: int
    title: str
    description: Optional[str] = None
    cover_url: Optional[str] = None
    type: str
    level: str
    day: Optional[int] = None
    duration: int = 0
    is_premium: bool = False
    
    class Config:
        from_attributes = True


class CourseDetailResponse(CourseResponse):
    """课程详情响应"""
    content: dict = {}


class CourseListResponse(BaseModel):
    """课程列表响应"""
    courses: List[CourseResponse]
    total: int
