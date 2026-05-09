"""学习路径 API —— POST /api/learning-path/generate"""

from fastapi import APIRouter, HTTPException
from app.core.utils import now_iso
from app.models.schemas import (
    LearningPathRequest, LearningPathResponse,
    LearningPathNode, KnowledgePointResponse,
)
from app.services import path_service

router = APIRouter(prefix="/api/learning-path", tags=["Learning Path"])


@router.post("/generate", response_model=LearningPathResponse)
async def generate_path(req: LearningPathRequest):
    """根据薄弱知识点生成个性化学习路径。

    输入：薄弱知识点列表（ID + 掌握度评分）
    输出：按学习顺序排列的知识点 + LLM 生成的每步学习建议
    """
    weak_tuples = [(wp.knowledge_point_id, wp.score) for wp in req.weak_points]
    try:
        nodes = await path_service.generate_learning_path(
            user_id=req.user_id, weak_points=weak_tuples,
            target_ids=req.target_ids, max_nodes=req.max_nodes,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"学习路径生成失败: {e}")

    return LearningPathResponse(
        user_id=req.user_id,
        nodes=[LearningPathNode(
            order=n["order"],
            knowledge_point=KnowledgePointResponse(**n["knowledge_point"]),
            reason=n["reason"],
        ) for n in nodes],
        generated_at=now_iso(),
    )
