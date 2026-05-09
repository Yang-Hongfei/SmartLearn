"""Chroma 向量数据库操作 —— 基于 langchain_chroma + PersistentClient。

为什么用 langchain_chroma：
- 提供 Document 抽象，与 LangChain 生态互通
- 内部用 chromadb 的 PersistentClient（嵌入式模式），数据存本地文件
- 无需 Docker，首次访问自动创建 chroma_data/ 目录

为什么用 _PrecomputedEmbeddings 占位类：
- 实际向量由外部的 embedding_service 预计算并传入
- langchain_chroma 构造函数强制要求 embedding_function 参数
- 但如果它被意外调用，抛 NotImplementedError 而不是静默返回零向量
"""

import os
import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from app.core.config import settings
from app.core.utils import merge_dedup
from app.services import embedding_service

COLLECTION_NAME = "knowledge_base"
_vector_store: Chroma | None = None


class _PrecomputedEmbeddings(Embeddings):
    """占位类 —— 实际向量由外部预计算后通过 embeddings 参数传入。
    如果这些方法被调用了，说明代码有 bug，应立即暴露。"""

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        raise NotImplementedError("预计算模式，请通过 embeddings 参数传入向量")

    def embed_query(self, text: str) -> list[float]:
        raise NotImplementedError("预计算模式，请通过 embeddings 参数传入向量")


def _get_vs() -> Chroma:
    """获取 Chroma 向量存储实例（惰性初始化）"""
    global _vector_store
    if _vector_store is None:
        os.makedirs(settings.chroma_path, exist_ok=True)
        client = chromadb.PersistentClient(
            path=settings.chroma_path,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        _vector_store = Chroma(
            collection_name=COLLECTION_NAME,
            embedding_function=_PrecomputedEmbeddings(),
            client=client,
            collection_metadata={"hnsw:space": "cosine"},  # 余弦相似度
        )
    return _vector_store


async def query(
    embedding: list[float],
    top_k: int = 5,
    filter_kp_ids: list[str] | None = None,
) -> list[dict]:
    """向量检索：用预计算的 query embedding 搜索最相似的文档。

    filter_kp_ids: 可选，限定只从指定知识点中检索（用于精准搜索场景）。
    """
    vs = _get_vs()
    where = {"knowledge_point_id": {"$in": filter_kp_ids}} if filter_kp_ids else None
    docs: list[Document] = vs.similarity_search_by_vector(
        embedding=embedding, k=top_k, filter=where,
    )
    return [_doc_to_hit(d) for d in docs]


async def keyword_query(keywords: list[str], top_k: int = 5) -> list[dict]:
    """关键词检索：对各关键词分别做语义搜索，合并去重。

    这里用 Chroma 的 similarity_search_with_relevance_scores（语义搜索）
    而非纯关键词匹配，因为 Chroma 不支持原生 BM25。
    """
    vs = _get_vs()
    all_hits: list[list[dict]] = []
    for kw in keywords:
        try:
            docs_with_scores = vs.similarity_search_with_relevance_scores(kw, k=top_k)
            all_hits.append([
                _doc_to_hit(doc, score=score) for doc, score in docs_with_scores
            ])
        except (ValueError, TypeError):
            continue
    return merge_dedup(*all_hits, key="id")[:top_k]


async def upsert(
    documents: list[str],
    metadatas: list[dict],
    ids: list[str],
    embeddings: list[list[float]] | None = None,
):
    """插入或更新文档。若不传 embeddings 则自动生成。"""
    vs = _get_vs()
    embs = embeddings or await embedding_service.embed_batch(documents)
    vs.add_texts(texts=documents, metadatas=metadatas, ids=ids, embeddings=embs)


async def delete(ids: list[str]):
    """按 ID 删除文档"""
    vs = _get_vs()
    vs.delete(ids=ids)


def _doc_to_hit(doc: Document, score: float | None = None) -> dict:
    """将 langchain Document 转为内部使用的 dict 格式"""
    return {
        "id": doc.metadata.get("id", ""),
        "content": doc.page_content,
        "metadata": doc.metadata,
        "score": score or 0.0,
    }
