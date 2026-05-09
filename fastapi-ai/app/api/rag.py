"""RAG 问答 API —— POST /api/rag/query"""

from fastapi import APIRouter, HTTPException
from app.models.schemas import RagQueryRequest, RagQueryResponse, RagSource
from app.services import rag_service

router = APIRouter(prefix="/api/rag", tags=["RAG"])


@router.post("/query", response_model=RagQueryResponse)
async def query_rag(req: RagQueryRequest):
    """智能问答：混合检索 + LLM 生成，返回答案及引用来源"""
    try:
        answer, sources, related_kps = await rag_service.rag_query(
            question=req.question,
            top_k=req.top_k,
            knowledge_point_ids=req.knowledge_point_ids,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG 查询失败: {e}")

    return RagQueryResponse(
        answer=answer,
        sources=[RagSource(**s) for s in sources],
        related_knowledge_points=related_kps,
    )
