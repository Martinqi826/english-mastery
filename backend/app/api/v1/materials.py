"""
素材管理 API
用户自定义学习素材的创建、查询、删除
"""
import asyncio
import logging
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.material import (
    UserMaterial, 
    GeneratedVocabulary, 
    ReadingQuestion,
    MaterialSourceType,
    MaterialStatus
)
from app.schemas.material import (
    MaterialCreateText,
    MaterialCreateURL,
    MaterialListItem,
    MaterialDetail,
    MaterialStatusResponse,
    VocabularyItem,
    QuestionItem,
    VocabularyUpdateRequest,
    AnswerSubmitRequest,
    AnswerSubmitResponse,
)
from app.schemas.base import success_response, error_response, ErrorCode
from app.services.ai_service import ai_service
from app.services.scraper_service import scraper_service

logger = logging.getLogger(__name__)

router = APIRouter()


# ===== 素材创建 =====

@router.post("/text", summary="通过文本创建素材")
async def create_material_from_text(
    data: MaterialCreateText,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    用户粘贴文本创建学习素材
    """
    # 计算单词数
    word_count = len(data.content.split())
    
    # 创建素材记录
    material = UserMaterial(
        user_id=current_user.id,
        title=data.title,
        source_type=MaterialSourceType.TEXT,
        source_content=data.content,
        word_count=word_count,
        status=MaterialStatus.PENDING
    )
    db.add(material)
    await db.commit()
    await db.refresh(material)
    
    logger.info(f"Created text material: id={material.id}, user={current_user.id}")
    
    # 添加后台任务进行 AI 处理
    background_tasks.add_task(
        process_material_content,
        material.id,
        data.content
    )
    
    return success_response(
        data=MaterialListItem.model_validate(material),
        message="素材创建成功，正在生成学习内容"
    )


@router.post("/url", summary="通过URL创建素材")
async def create_material_from_url(
    data: MaterialCreateURL,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    用户提供 URL，抓取网页内容创建学习素材
    """
    try:
        # 抓取网页内容
        title, content = await scraper_service.fetch_content(data.url)
        
        # 使用用户提供的标题或抓取的标题
        final_title = data.title or title
        word_count = len(content.split())
        
        # 创建素材记录
        material = UserMaterial(
            user_id=current_user.id,
            title=final_title,
            source_type=MaterialSourceType.URL,
            source_content=content,
            source_url=data.url,
            word_count=word_count,
            status=MaterialStatus.PENDING
        )
        db.add(material)
        await db.commit()
        await db.refresh(material)
        
        logger.info(f"Created URL material: id={material.id}, url={data.url}")
        
        # 添加后台任务进行 AI 处理
        background_tasks.add_task(
            process_material_content,
            material.id,
            content
        )
        
        return success_response(
            data=MaterialListItem.model_validate(material),
            message="素材创建成功，正在生成学习内容"
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": ErrorCode.INVALID_PARAMS, "message": str(e)}
        )


# ===== 素材查询 =====

@router.get("", summary="获取素材列表")
async def get_materials(
    page: int = 1,
    page_size: int = 20,
    status_filter: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取当前用户的素材列表
    """
    query = select(UserMaterial).where(
        UserMaterial.user_id == current_user.id
    )
    
    # 状态过滤
    if status_filter:
        try:
            status_enum = MaterialStatus(status_filter)
            query = query.where(UserMaterial.status == status_enum)
        except ValueError:
            pass
    
    # 排序：最新创建的在前
    query = query.order_by(UserMaterial.created_at.desc())
    
    # 分页
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    
    result = await db.execute(query)
    materials = result.scalars().all()
    
    items = [MaterialListItem.model_validate(m) for m in materials]
    
    return success_response(data={"items": items, "page": page, "page_size": page_size})


@router.get("/{material_id}", summary="获取素材详情")
async def get_material_detail(
    material_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取素材详情，包含词汇和题目
    """
    result = await db.execute(
        select(UserMaterial)
        .options(
            selectinload(UserMaterial.vocabularies),
            selectinload(UserMaterial.questions)
        )
        .where(
            UserMaterial.id == material_id,
            UserMaterial.user_id == current_user.id
        )
    )
    material = result.scalar_one_or_none()
    
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": ErrorCode.NOT_FOUND, "message": "素材不存在"}
        )
    
    return success_response(data=MaterialDetail.model_validate(material))


@router.get("/{material_id}/status", summary="获取素材处理状态")
async def get_material_status(
    material_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    轮询获取素材处理状态
    """
    result = await db.execute(
        select(UserMaterial).where(
            UserMaterial.id == material_id,
            UserMaterial.user_id == current_user.id
        )
    )
    material = result.scalar_one_or_none()
    
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": ErrorCode.NOT_FOUND, "message": "素材不存在"}
        )
    
    return success_response(data=MaterialStatusResponse(
        id=material.id,
        status=material.status,
        error_message=material.error_message,
        generated_vocab_count=material.generated_vocab_count,
        generated_question_count=material.generated_question_count
    ))


# ===== 素材删除 =====

@router.delete("/{material_id}", summary="删除素材")
async def delete_material(
    material_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    删除素材及其关联的词汇和题目
    """
    result = await db.execute(
        select(UserMaterial).where(
            UserMaterial.id == material_id,
            UserMaterial.user_id == current_user.id
        )
    )
    material = result.scalar_one_or_none()
    
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": ErrorCode.NOT_FOUND, "message": "素材不存在"}
        )
    
    await db.delete(material)
    await db.commit()
    
    logger.info(f"Deleted material: id={material_id}, user={current_user.id}")
    
    return success_response(message="素材删除成功")


# ===== 词汇学习 =====

@router.get("/{material_id}/vocabularies", summary="获取素材词汇列表")
async def get_material_vocabularies(
    material_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取素材的词汇列表
    """
    # 验证素材归属
    result = await db.execute(
        select(UserMaterial).where(
            UserMaterial.id == material_id,
            UserMaterial.user_id == current_user.id
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": ErrorCode.NOT_FOUND, "message": "素材不存在"}
        )
    
    # 获取词汇
    result = await db.execute(
        select(GeneratedVocabulary)
        .where(GeneratedVocabulary.material_id == material_id)
        .order_by(GeneratedVocabulary.sort_order)
    )
    vocabularies = result.scalars().all()
    
    items = [VocabularyItem.model_validate(v) for v in vocabularies]
    
    return success_response(data=items)


@router.patch("/{material_id}/vocabularies/{vocab_id}", summary="更新词汇学习状态")
async def update_vocabulary_status(
    material_id: int,
    vocab_id: int,
    data: VocabularyUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新词汇的学习/掌握状态
    """
    # 验证素材归属
    result = await db.execute(
        select(UserMaterial).where(
            UserMaterial.id == material_id,
            UserMaterial.user_id == current_user.id
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": ErrorCode.NOT_FOUND, "message": "素材不存在"}
        )
    
    # 获取词汇
    result = await db.execute(
        select(GeneratedVocabulary).where(
            GeneratedVocabulary.id == vocab_id,
            GeneratedVocabulary.material_id == material_id
        )
    )
    vocab = result.scalar_one_or_none()
    
    if not vocab:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": ErrorCode.NOT_FOUND, "message": "词汇不存在"}
        )
    
    # 更新状态
    if data.is_learned is not None:
        vocab.is_learned = data.is_learned
    if data.is_mastered is not None:
        vocab.is_mastered = data.is_mastered
        if data.is_mastered:
            vocab.is_learned = True
    
    vocab.review_count += 1
    await db.commit()
    
    return success_response(data=VocabularyItem.model_validate(vocab))


# ===== 阅读练习 =====

@router.get("/{material_id}/questions", summary="获取素材阅读题目")
async def get_material_questions(
    material_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取素材的阅读理解题目
    """
    # 验证素材归属
    result = await db.execute(
        select(UserMaterial).where(
            UserMaterial.id == material_id,
            UserMaterial.user_id == current_user.id
        )
    )
    material = result.scalar_one_or_none()
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": ErrorCode.NOT_FOUND, "message": "素材不存在"}
        )
    
    # 获取题目
    result = await db.execute(
        select(ReadingQuestion)
        .where(ReadingQuestion.material_id == material_id)
        .order_by(ReadingQuestion.sort_order)
    )
    questions = result.scalars().all()
    
    items = [QuestionItem.model_validate(q) for q in questions]
    
    return success_response(data={
        "content": material.source_content,
        "questions": items
    })


@router.post("/{material_id}/questions/answer", summary="提交答案")
async def submit_answer(
    material_id: int,
    data: AnswerSubmitRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    提交阅读理解题目的答案
    """
    # 验证素材归属
    result = await db.execute(
        select(UserMaterial).where(
            UserMaterial.id == material_id,
            UserMaterial.user_id == current_user.id
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": ErrorCode.NOT_FOUND, "message": "素材不存在"}
        )
    
    # 获取题目
    result = await db.execute(
        select(ReadingQuestion).where(
            ReadingQuestion.id == data.question_id,
            ReadingQuestion.material_id == material_id
        )
    )
    question = result.scalar_one_or_none()
    
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": ErrorCode.NOT_FOUND, "message": "题目不存在"}
        )
    
    # 判断答案
    is_correct = data.answer == question.correct_answer
    
    # 更新答题记录
    question.user_answer = data.answer
    question.is_correct = is_correct
    question.answered_at = datetime.now(timezone.utc)
    await db.commit()
    
    return success_response(data=AnswerSubmitResponse(
        question_id=question.id,
        user_answer=data.answer,
        correct_answer=question.correct_answer,
        is_correct=is_correct,
        explanation=question.explanation
    ))


# ===== 后台任务 =====

async def process_material_content(material_id: int, content: str):
    """
    后台处理素材内容，调用 AI 生成学习材料
    """
    from app.database import async_session_maker
    
    async with async_session_maker() as db:
        try:
            # 获取素材
            result = await db.execute(
                select(UserMaterial).where(UserMaterial.id == material_id)
            )
            material = result.scalar_one_or_none()
            
            if not material:
                logger.error(f"Material not found: {material_id}")
                return
            
            # 更新状态为处理中
            material.status = MaterialStatus.PROCESSING
            await db.commit()
            
            logger.info(f"Processing material: {material_id}")
            
            # 调用 AI 服务生成内容
            generated = await ai_service.generate_learning_content(
                text=content,
                max_words=15,
                max_questions=5
            )
            
            # 保存生成的词汇
            for i, vocab_data in enumerate(generated.vocabularies):
                vocab = GeneratedVocabulary(
                    material_id=material_id,
                    word=vocab_data.word,
                    phonetic=vocab_data.phonetic,
                    translation=vocab_data.translation,
                    definition=vocab_data.definition,
                    example=vocab_data.example,
                    example_translation=vocab_data.example_translation,
                    synonyms=vocab_data.synonyms,
                    collocations=vocab_data.collocations,
                    difficulty=vocab_data.difficulty,
                    sort_order=i
                )
                db.add(vocab)
            
            # 保存生成的题目
            for i, question_data in enumerate(generated.questions):
                question = ReadingQuestion(
                    material_id=material_id,
                    question_text=question_data.question_text,
                    question_type=question_data.question_type,
                    options=question_data.options,
                    correct_answer=question_data.correct_answer,
                    explanation=question_data.explanation,
                    sort_order=i
                )
                db.add(question)
            
            # 更新素材状态
            material.status = MaterialStatus.COMPLETED
            material.generated_vocab_count = len(generated.vocabularies)
            material.generated_question_count = len(generated.questions)
            material.processed_at = datetime.now(timezone.utc)
            
            await db.commit()
            
            logger.info(f"Material processed successfully: {material_id}, "
                       f"vocabs={len(generated.vocabularies)}, questions={len(generated.questions)}")
            
        except Exception as e:
            logger.error(f"Error processing material {material_id}: {e}")
            await db.rollback()  # 回滚之前的修改
            
            # 更新为失败状态（使用新的事务）
            try:
                result = await db.execute(
                    select(UserMaterial).where(UserMaterial.id == material_id)
                )
                material = result.scalar_one_or_none()
                if material:
                    material.status = MaterialStatus.FAILED
                    material.error_message = str(e)[:500]
                    await db.commit()
            except Exception as inner_e:
                logger.error(f"Error updating material status: {inner_e}")
