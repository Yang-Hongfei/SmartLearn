"""Embedding 服务 —— 文本转向量，调用 Qwen3-Embedding（DashScope）。

设计要点：
- embed_text 委托给 embed_batch，消除重复的 API 调用代码
- 批量接口 embed_batch 是核心，一次请求处理多条文本
"""

from app.core.config import settings
from app.services.llm_service import get_client


async def embed_batch(texts: list[str]) -> list[list[float]]:
    """批量文本 → 向量列表，返回 [ [1024维], [1024维], ... ]"""
    client = get_client()
    response = client.embeddings.create(
        model=settings.embedding_model,
        input=texts,
        dimensions=settings.embedding_dimensions,
    )
    return [item.embedding for item in response.data]


async def embed_text(text: str) -> list[float]:
    """单条文本 → 向量，直接委托给批量接口"""
    return (await embed_batch([text]))[0]
