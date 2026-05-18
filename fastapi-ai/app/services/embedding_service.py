"""Embedding 服务 —— 文本转向量（阿里云百炼 text-embedding-v4）。"""

from openai import OpenAI
from app.core.config import settings

_embedding_client: OpenAI | None = None


def get_embedding_client() -> OpenAI:
    global _embedding_client
    if _embedding_client is None:
        _embedding_client = OpenAI(
            api_key=settings.embedding_api_key or settings.deepseek_api_key,
            base_url=settings.embedding_base_url,
        )
    return _embedding_client


async def embed_batch(texts: list[str]) -> list[list[float]]:
    client = get_embedding_client()
    response = client.embeddings.create(
        model=settings.embedding_model,
        input=texts,
        dimensions=settings.embedding_dimensions,
    )
    return [item.embedding for item in response.data]


async def embed_text(text: str) -> list[float]:
    return (await embed_batch([text]))[0]
