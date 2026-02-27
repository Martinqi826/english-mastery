"""
素材相关 Schema 定义
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, HttpUrl
from enum import Enum


class MaterialSourceType(str, Enum):
    """素材来源类型"""
    TEXT = "text"
    URL = "url"


class MaterialStatus(str, Enum):
    """素材处理状态"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


# ===== 请求 Schema =====

class MaterialCreateText(BaseModel):
    """文本方式创建素材"""
    title: str = Field(..., min_length=1, max_length=200, description="素材标题")
    content: str = Field(..., min_length=50, max_length=10000, description="文本内容")
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "TED演讲: 学习的力量",
                "content": "When I was nine years old, I went off to summer camp for the first time..."
            }
        }


class MaterialCreateURL(BaseModel):
    """URL方式创建素材"""
    title: Optional[str] = Field(None, max_length=200, description="素材标题（可选，自动提取）")
    url: str = Field(..., description="网页URL")
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "BBC News Article",
                "url": "https://www.bbc.com/news/article-123"
            }
        }


# ===== 响应 Schema =====

class VocabularyItem(BaseModel):
    """词汇项"""
    id: int
    word: str
    phonetic: Optional[str] = None
    translation: str
    definition: Optional[str] = None
    example: Optional[str] = None
    example_translation: Optional[str] = None
    synonyms: List[str] = []
    collocations: List[str] = []
    difficulty: int = 3
    is_learned: bool = False
    is_mastered: bool = False
    sort_order: int = 0
    
    class Config:
        from_attributes = True


class QuestionItem(BaseModel):
    """阅读理解题目"""
    id: int
    question_text: str
    question_type: str = "choice"
    options: List[str] = []
    correct_answer: int
    explanation: Optional[str] = None
    sort_order: int = 0
    user_answer: Optional[int] = None
    is_correct: Optional[bool] = None
    
    class Config:
        from_attributes = True


class MaterialListItem(BaseModel):
    """素材列表项（简略信息）"""
    id: int
    title: str
    source_type: MaterialSourceType
    source_url: Optional[str] = None
    status: MaterialStatus
    error_message: Optional[str] = None
    word_count: int = 0
    generated_vocab_count: int = 0
    generated_question_count: int = 0
    created_at: datetime
    processed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class MaterialDetail(BaseModel):
    """素材详情"""
    id: int
    title: str
    source_type: MaterialSourceType
    source_content: str
    source_url: Optional[str] = None
    status: MaterialStatus
    error_message: Optional[str] = None
    word_count: int = 0
    generated_vocab_count: int = 0
    generated_question_count: int = 0
    created_at: datetime
    updated_at: datetime
    processed_at: Optional[datetime] = None
    vocabularies: List[VocabularyItem] = []
    questions: List[QuestionItem] = []
    
    class Config:
        from_attributes = True


class MaterialStatusResponse(BaseModel):
    """素材状态响应"""
    id: int
    status: MaterialStatus
    error_message: Optional[str] = None
    generated_vocab_count: int = 0
    generated_question_count: int = 0


# ===== 词汇学习相关 =====

class VocabularyUpdateRequest(BaseModel):
    """更新词汇学习状态"""
    is_learned: Optional[bool] = None
    is_mastered: Optional[bool] = None


class AnswerSubmitRequest(BaseModel):
    """提交答案"""
    question_id: int
    answer: int = Field(..., ge=0, le=3, description="答案索引(0-3)")


class AnswerSubmitResponse(BaseModel):
    """提交答案响应"""
    question_id: int
    user_answer: int
    correct_answer: int
    is_correct: bool
    explanation: Optional[str] = None


# ===== AI 生成相关（内部使用）=====

class GeneratedVocabularyData(BaseModel):
    """AI 生成的词汇数据"""
    word: str
    phonetic: Optional[str] = None
    translation: str
    definition: Optional[str] = None
    example: Optional[str] = None
    example_translation: Optional[str] = None
    synonyms: List[str] = []
    collocations: List[str] = []
    difficulty: int = 3


class GeneratedQuestionData(BaseModel):
    """AI 生成的题目数据"""
    question_text: str
    question_type: str = "choice"
    options: List[str]
    correct_answer: int
    explanation: Optional[str] = None


class GeneratedContent(BaseModel):
    """AI 生成的完整内容"""
    vocabularies: List[GeneratedVocabularyData] = []
    questions: List[GeneratedQuestionData] = []
