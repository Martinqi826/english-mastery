"""
词汇 API 路由
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.deps import get_current_user, get_current_user_optional
from app.models.user import User
from app.models.membership import MembershipLevel
from app.schemas.base import APIResponse, ErrorCode, success_response, error_response
from app.schemas.content import (
    VocabularyResponse, 
    VocabularyListResponse,
    UserVocabularyProgress
)
from app.services.content_service import content_service
from app.services.learning_service import learning_service


router = APIRouter()


@router.get("/today", response_model=APIResponse[VocabularyListResponse])
async def get_today_vocabulary(
    day: int = Query(1, ge=1, le=30, description="学习天数(1-30)"),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """
    获取今日词汇
    
    - 每天30个新词
    - 会员可获取全部词汇，免费用户有限制
    """
    # 获取用户会员等级
    membership_level = MembershipLevel.FREE
    if current_user:
        membership_level = await content_service.get_user_membership_level(
            db, current_user.id
        )
    
    # 获取词汇列表
    words = await content_service.get_vocabulary_by_day(
        db, day, 
        user_id=current_user.id if current_user else None,
        membership_level=membership_level
    )
    
    return success_response(VocabularyListResponse(
        day=day,
        words=[
            VocabularyResponse(
                id=w.id,
                word=w.word,
                phonetic=w.phonetic,
                pronunciation_url=w.pronunciation_url,
                translation=w.translation,
                definition=w.definition,
                example=w.example,
                example_translation=w.example_translation,
                day=w.day,
                category=w.category,
                level=w.level.value if w.level else "intermediate",
                synonyms=w.synonyms or [],
                antonyms=w.antonyms or [],
                collocations=w.collocations or []
            )
            for w in words
        ],
        total=len(words),
        learned_count=0  # TODO: 从用户学习记录中获取
    ))


@router.get("/{word_id}", response_model=APIResponse[VocabularyResponse])
async def get_vocabulary_detail(
    word_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    获取词汇详情
    """
    word = await content_service.get_vocabulary_by_id(db, word_id)
    
    if not word:
        raise HTTPException(
            status_code=404,
            detail=error_response(ErrorCode.CONTENT_NOT_FOUND, "词汇不存在")
        )
    
    return success_response(VocabularyResponse(
        id=word.id,
        word=word.word,
        phonetic=word.phonetic,
        pronunciation_url=word.pronunciation_url,
        translation=word.translation,
        definition=word.definition,
        example=word.example,
        example_translation=word.example_translation,
        day=word.day,
        category=word.category,
        level=word.level.value if word.level else "intermediate",
        synonyms=word.synonyms or [],
        antonyms=word.antonyms or [],
        collocations=word.collocations or []
    ))


@router.get("/search", response_model=APIResponse)
async def search_vocabulary(
    keyword: str = Query(..., min_length=1, description="搜索关键词"),
    limit: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """
    搜索词汇
    """
    words = await content_service.search_vocabulary(db, keyword, limit)
    
    return success_response({
        "keyword": keyword,
        "results": [
            {
                "id": w.id,
                "word": w.word,
                "translation": w.translation,
                "day": w.day
            }
            for w in words
        ],
        "total": len(words)
    })


@router.post("/{word_id}/learned", response_model=APIResponse)
async def mark_word_learned(
    word_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    标记词汇已学习
    
    增加用户已学词汇计数
    """
    # 验证词汇存在
    word = await content_service.get_vocabulary_by_id(db, word_id)
    if not word:
        raise HTTPException(
            status_code=404,
            detail=error_response(ErrorCode.CONTENT_NOT_FOUND, "词汇不存在")
        )
    
    # 更新学习进度
    from app.schemas.learning import ProgressUpdate
    await learning_service.update_progress(
        db,
        current_user.id,
        ProgressUpdate(add_words_learned=1)
    )
    
    return success_response({
        "word_id": word_id,
        "word": word.word
    }, "已标记为已学习")


@router.get("/progress/summary", response_model=APIResponse[UserVocabularyProgress])
async def get_vocabulary_progress(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取词汇学习进度汇总
    """
    progress = await learning_service.get_progress(db, current_user.id)
    
    total_words = 900  # 30天 * 30词
    today_words = 30
    
    return success_response(UserVocabularyProgress(
        total_words=total_words,
        learned_words=progress.words_learned,
        today_words=today_words,
        today_learned=0,  # TODO: 从今日学习记录获取
        completion_rate=round(progress.words_learned / total_words * 100, 1)
    ))
