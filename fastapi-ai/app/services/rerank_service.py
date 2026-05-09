"""Cohere Rerank 重排序服务 —— 对混合检索结果精排。

降级策略（三层保护）：
1. 未配置 API Key → 直接跳过，保持原始顺序
2. API 调用失败（网络/额度）→ 捕获 CohereError，退回原序
3. 编程错误（KeyError 等）→ 不捕获，让它抛出以便发现 bug

为什么需要 Rerank：
- Chroma 的向量检索基于语义相似度，可能召回"相关但不精准"的文档
- 关键词检索更加粗糙
- Rerank 用交叉编码器（cross-encoder）精排，大幅提升 Top-N 准确率
"""

import cohere
from app.core.config import settings

_client: cohere.Client | None = None


def _get_client() -> cohere.Client:
    global _client
    if _client is None:
        _client = cohere.ClientV2(api_key=settings.cohere_api_key)
    return _client


async def rerank(query: str, documents: list[dict], top_n: int = 5) -> list[dict]:
    """对文档列表按与 query 的相关性重排序，返回 top_n。

    选择 rerank-multilingual-v3.0：
    - 原生支持中文，不需要额外翻译
    - v3 对技术文本（算法概念）的排序效果优于 v2
    """
    if not documents or not _cohere_configured():
        return _fallback(documents, top_n)

    try:
        client = _get_client()
        docs_text = [d["content"] for d in documents]
        response = client.rerank(
            model="rerank-multilingual-v3.0",
            query=query,
            documents=docs_text,
            top_n=min(top_n, len(docs_text)),
        )
        return [
            {**documents[item.index], "rerank_score": item.relevance_score}
            for item in response.results
        ]
    except cohere.CohereError:
        # API 故障：降级为按原始得分排序
        return _fallback(documents, top_n)


def _cohere_configured() -> bool:
    """判断 Cohere API Key 是否已配置"""
    return bool(settings.cohere_api_key) and settings.cohere_api_key != "your-cohere-key-here"


def _fallback(documents: list[dict], top_n: int) -> list[dict]:
    """无 Rerank 时退回原始顺序（向量检索得分已较高）"""
    for d in documents:
        d["rerank_score"] = d.get("score", 0.0)
    return documents[:top_n]
