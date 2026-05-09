"""Pydantic 数据模型 —— 定义所有 API 的请求/响应格式。

FastAPI 利用这些模型自动完成：
- 请求体校验（类型、必填、范围）
- Swagger 文档生成
- 响应序列化
"""

from typing import Optional
from pydantic import BaseModel, Field


# ==================== RAG 问答 ====================

class RagQueryRequest(BaseModel):
    """RAG 查询请求"""
    question: str                                    # 用户问题
    user_id: Optional[str] = None                    # 可选用户标识
    knowledge_point_ids: Optional[list[str]] = None  # 可选：限定检索范围
    top_k: int = Field(default=5, ge=1, le=20)       # 返回文档数


class RagSource(BaseModel):
    """RAG 回答的引用来源"""
    title: str
    content_snippet: str
    score: float
    knowledge_point_id: Optional[str] = None


class RagQueryResponse(BaseModel):
    """RAG 查询响应"""
    answer: str
    sources: list[RagSource]
    related_knowledge_points: list[str]


# ==================== 知识图谱 ====================

class KnowledgePointBase(BaseModel):
    """知识点基础模型（请求和响应共用）"""
    id: str
    name: str
    description: str
    difficulty: int = Field(default=1, ge=1, le=5)
    category: str = ""


class KnowledgePointCreate(KnowledgePointBase):
    """创建知识点请求体"""
    pass


class KnowledgePointResponse(KnowledgePointBase):
    """知识点查询响应体"""
    pass


class KnowledgeRelation(BaseModel):
    """创建知识点关系"""
    from_id: str
    to_id: str
    relation_type: str = "PREREQUISITE"  # PREREQUISITE / RELATED_TO
    weight: float = 1.0


class KnowledgeSearchRequest(BaseModel):
    """知识点搜索"""
    keyword: str
    category: Optional[str] = None
    limit: int = Field(default=10, ge=1, le=50)


class KnowledgePathRequest(BaseModel):
    """路径查询"""
    from_id: str
    to_id: str
    max_depth: int = Field(default=5, ge=1, le=10)


class KnowledgePathResponse(BaseModel):
    """路径查询响应"""
    nodes: list[KnowledgePointBase]
    length: int


# ==================== 学习路径 ====================

class WeakPoint(BaseModel):
    """薄弱知识点"""
    knowledge_point_id: str
    score: float = Field(default=0.0, ge=0.0, le=1.0)  # 0=完全不会, 1=已掌握


class LearningPathRequest(BaseModel):
    """学习路径规划请求"""
    user_id: str
    weak_points: list[WeakPoint]
    target_ids: Optional[list[str]] = None
    max_nodes: int = Field(default=10, ge=3, le=30)


class LearningPathNode(BaseModel):
    """学习路径中的一个步骤"""
    order: int                                  # 学习顺序（1-based）
    knowledge_point: KnowledgePointBase          # 知识点详情
    reason: str                                  # 为什么要学这个（LLM 生成）


class LearningPathResponse(BaseModel):
    """学习路径规划响应"""
    user_id: str
    nodes: list[LearningPathNode]
    generated_at: str


# ==================== 答题分析（SpringBoot 对接核心） ====================

class QuestionItem(BaseModel):
    """一道题目 —— SpringBoot 传来的题目信息"""
    id: str
    type: str = "single_choice"                     # single_choice / fill_blank / true_false
    content: str                                     # 题目文本
    options: Optional[list[str]] = None               # 选项列表（填空题为 None）
    correct_answer: str                               # 正确答案
    knowledge_point_ids: list[str] = []               # 关联知识点 ID 列表
    difficulty: int = Field(default=1, ge=1, le=5)   # 难度 1-5


class AnswerSubmitRequest(BaseModel):
    """SpringBoot → FastAPI：提交答题记录"""
    user_id: str
    question: QuestionItem
    user_answer: str  # 用户选择的/填写的答案


class ErrorAnalysis(BaseModel):
    """错题解析"""
    user_answer: str
    correct_answer: str
    explanation: str       # 解题思路
    error_type: str = ""   # 错误分类
    error_detail: str = "" # 针对性分析


class WeakPointAnalysis(BaseModel):
    """薄弱点分析"""
    knowledge_point_id: str
    knowledge_point_name: str
    current_mastery: float  # 估算掌握度 0.0-1.0
    reason: str              # 判断依据


class AnswerAnalysisResponse(BaseModel):
    """FastAPI → SpringBoot：分析结果"""
    user_id: str
    question_id: str
    is_correct: bool
    error_analysis: Optional[ErrorAnalysis] = None       # 答对时为 null
    weak_point_analysis: list[WeakPointAnalysis]          # 始终返回
    learning_path: list[LearningPathNode]                 # 答错时有内容，答对时为空
    generated_at: str
