"""
AI 服务
使用 Claude API 生成学习内容
"""
import json
import logging
from typing import Optional
import httpx

from app.config import settings
from app.schemas.material import (
    GeneratedContent,
    GeneratedVocabularyData,
    GeneratedQuestionData
)

logger = logging.getLogger(__name__)


class AIService:
    """Claude AI 内容生成服务"""
    
    def __init__(self):
        self.api_key = settings.ANTHROPIC_API_KEY
        self.api_url = "https://api.anthropic.com/v1/messages"
        self.model = "claude-3-haiku-20240307"  # 使用 Haiku 模型，速度快成本低
        self.max_tokens = 4096
    
    async def generate_learning_content(
        self,
        text: str,
        max_words: int = 15,
        max_questions: int = 5
    ) -> GeneratedContent:
        """
        从文本生成学习内容
        
        Args:
            text: 原文内容
            max_words: 最多提取词汇数
            max_questions: 最多生成题目数
            
        Returns:
            GeneratedContent 包含词汇列表和题目列表
        """
        if not self.api_key:
            logger.error("ANTHROPIC_API_KEY not configured")
            raise ValueError("AI 服务未配置，请联系管理员")
        
        # 截断过长文本
        if len(text) > 8000:
            text = text[:8000] + "..."
            logger.warning(f"Text truncated to 8000 characters")
        
        prompt = self._build_prompt(text, max_words, max_questions)
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    self.api_url,
                    headers={
                        "Content-Type": "application/json",
                        "x-api-key": self.api_key,
                        "anthropic-version": "2023-06-01"
                    },
                    json={
                        "model": self.model,
                        "max_tokens": self.max_tokens,
                        "messages": [
                            {"role": "user", "content": prompt}
                        ]
                    }
                )
                
                if response.status_code != 200:
                    logger.error(f"Claude API error: {response.status_code} - {response.text}")
                    raise ValueError(f"AI 服务请求失败: {response.status_code}")
                
                result = response.json()
                content_text = result["content"][0]["text"]
                
                return self._parse_response(content_text)
                
        except httpx.TimeoutException:
            logger.error("Claude API timeout")
            raise ValueError("AI 服务响应超时，请稍后重试")
        except Exception as e:
            logger.error(f"Claude API error: {str(e)}")
            raise ValueError(f"AI 服务错误: {str(e)}")
    
    def _build_prompt(self, text: str, max_words: int, max_questions: int) -> str:
        """构建 Prompt"""
        return f"""你是一位专业的英语教育专家。请分析以下英文文本，并生成学习材料。

## 输入文本
{text}

## 任务要求

### 1. 词汇提取
请从文本中提取 {max_words} 个最值得学习的词汇（优先选择：高频商务词汇、学术词汇、难词）。

对于每个词汇，提供：
- word: 单词原形
- phonetic: 国际音标（如 /ˈbɪznəs/）
- translation: 简洁的中文释义
- definition: 英文释义
- example: 一个包含该词的例句（可以引用原文或新造句）
- example_translation: 例句的中文翻译
- synonyms: 2-3个同义词
- collocations: 2-3个常见搭配
- difficulty: 难度等级(1-5, 其中1最简单，5最难)

### 2. 阅读理解题
请基于文本内容，生成 {max_questions} 道阅读理解选择题。

题目类型要多样化：
- 主旨理解题（What is the main idea...）
- 细节理解题（According to the passage...）
- 推断题（It can be inferred that...）
- 词义猜测题（The word "X" in the passage means...）

对于每道题，提供：
- question_text: 题目内容
- options: 4个选项（A/B/C/D，存储为数组）
- correct_answer: 正确答案的索引（0=A, 1=B, 2=C, 3=D）
- explanation: 答案解析

## 输出格式
请严格按照以下 JSON 格式输出（不要添加任何其他文字）：

```json
{{
  "vocabularies": [
    {{
      "word": "example",
      "phonetic": "/ɪɡˈzæmpl/",
      "translation": "例子，范例",
      "definition": "a thing characteristic of its kind or illustrating a general rule",
      "example": "This is a good example of modern architecture.",
      "example_translation": "这是现代建筑的一个很好的例子。",
      "synonyms": ["instance", "sample", "specimen"],
      "collocations": ["for example", "set an example", "classic example"],
      "difficulty": 2
    }}
  ],
  "questions": [
    {{
      "question_text": "What is the main idea of the passage?",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correct_answer": 0,
      "explanation": "The passage mainly discusses..."
    }}
  ]
}}
```"""
    
    def _parse_response(self, content: str) -> GeneratedContent:
        """解析 AI 响应"""
        try:
            # 尝试提取 JSON 块
            json_start = content.find("{")
            json_end = content.rfind("}") + 1
            
            if json_start == -1 or json_end == 0:
                logger.error(f"No JSON found in response: {content[:500]}")
                raise ValueError("AI 响应格式错误")
            
            json_str = content[json_start:json_end]
            data = json.loads(json_str)
            
            # 解析词汇
            vocabularies = []
            for v in data.get("vocabularies", []):
                try:
                    vocab = GeneratedVocabularyData(
                        word=v.get("word", ""),
                        phonetic=v.get("phonetic"),
                        translation=v.get("translation", ""),
                        definition=v.get("definition"),
                        example=v.get("example"),
                        example_translation=v.get("example_translation"),
                        synonyms=v.get("synonyms", []),
                        collocations=v.get("collocations", []),
                        difficulty=v.get("difficulty", 3)
                    )
                    if vocab.word and vocab.translation:
                        vocabularies.append(vocab)
                except Exception as e:
                    logger.warning(f"Failed to parse vocabulary: {e}")
                    continue
            
            # 解析题目
            questions = []
            for q in data.get("questions", []):
                try:
                    question = GeneratedQuestionData(
                        question_text=q.get("question_text", ""),
                        question_type=q.get("question_type", "choice"),
                        options=q.get("options", []),
                        correct_answer=q.get("correct_answer", 0),
                        explanation=q.get("explanation")
                    )
                    if question.question_text and len(question.options) >= 4:
                        questions.append(question)
                except Exception as e:
                    logger.warning(f"Failed to parse question: {e}")
                    continue
            
            logger.info(f"Parsed {len(vocabularies)} vocabularies and {len(questions)} questions")
            
            return GeneratedContent(
                vocabularies=vocabularies,
                questions=questions
            )
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}, content: {content[:500]}")
            raise ValueError("AI 响应解析失败")


# 创建服务实例
ai_service = AIService()
