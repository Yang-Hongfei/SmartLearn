"""RAG 混合检索编排 —— 7 步 Pipeline。

全流程：
  用户提问
    │
    ① Qwen3-Embedding 向量化（问题 → 1024维向量）
    │
    ② Chroma 向量检索（语义召回 top_k × 2）
    │     ③ 关键词检索（提取问题关键词，语义搜索补充）
    │
    ④ merge_dedup 合并去重（向量结果优先）
    │
    ⑤ Cohere Rerank 重排序（精排到 top_k）
    │
    ⑥ 拼接上下文（按编号拼成 Prompt）
    │
    ⑦ Qwen-Max 生成答案 + 标注引用

为什么向量检索取 top_k × 2：
- 额外召回留给 Rerank 精排空间
- 如果只取 top_k，Rerank 没有足够候选去做重排
"""

from langchain_core.prompts import ChatPromptTemplate
from app.core.config import settings
from app.core.utils import extract_keywords, meta, merge_dedup
from app.services import embedding_service, vector_service, rerank_service, llm_service

RAG_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """你是一个算法学习助手，基于提供的知识库资料回答用户问题。

回答要求：
1. 使用提供的参考资料来组织答案，在答案末尾标注引用来源（如 [1]、[2]）
2. 如果参考资料不足以回答问题，请说明，不要编造
3. 用中文回答，代码示例使用对应编程语言
4. 对复杂概念给出清晰的定义，配合具体的例子说明
5. 如果涉及易错点或常见误区，请特别指出"""),
    ("human", "参考资料：\n{context}\n\n请根据以上参考资料回答用户问题。\n用户问题：{question}"),
])


async def rag_query(
    question: str,
    top_k: int | None = None,
    knowledge_point_ids: list[str] | None = None,
) -> tuple[str, list[dict], list[str]]:
    """执行一次完整的 RAG 查询，返回 (答案, 来源列表, 关联知识点ID列表)。

    knowledge_point_ids: 可选的知识点过滤，用于精准搜索场景。
    """
    top_k = top_k or settings.rag_top_k

    # ①-② 向量化 + 语义检索
    q_embedding = await embedding_service.embed_text(question)
    vector_hits = await vector_service.query(
        embedding=q_embedding, top_k=top_k * 2, filter_kp_ids=knowledge_point_ids,
    )

    # ③ 关键词检索补充
    keywords = extract_keywords(question)
    keyword_hits = (
        await vector_service.keyword_query(keywords, top_k=top_k) if keywords else []
    )

    # ④-⑤ 合并去重 + 精排
    merged = merge_dedup(vector_hits, keyword_hits, key="id")
    merged = await rerank_service.rerank(question, merged, top_n=top_k) if merged else []

    # ⑥ 构建带编号的上下文
    context_parts = []
    for i, doc in enumerate(merged, 1):
        src = meta(doc, "source", "未知来源")
        context_parts.append(f"[{i}] 来源：{src}\n{doc['content']}")
    context = "\n\n---\n\n".join(context_parts) if context_parts else "暂无相关参考资料。"

    # ⑦ LLM 生成 via LangChain ChatPromptTemplate
    chain = RAG_PROMPT | llm_service.get_model()
    response = await chain.ainvoke({"context": context, "question": question})
    answer = response.content or ""

    # 组装结构化返回
    sources = []
    related_kps: list[str] = []
    for doc in merged:
        sources.append({
            "title": meta(doc, "source", "未知"),
            "content_snippet": doc["content"][:200],
            "score": doc.get("rerank_score", doc.get("score", 0.0)),
            "knowledge_point_id": meta(doc, "knowledge_point_id"),
        })
        kp_id = meta(doc, "knowledge_point_id")
        if kp_id and kp_id not in related_kps:
            related_kps.append(kp_id)

    return answer, sources, related_kps
