"""知识图谱 API —— 知识点 CRUD + 关系管理 + 路径查询"""

from fastapi import APIRouter, HTTPException
from app.models.schemas import (
    KnowledgePointCreate, KnowledgePointResponse,
    KnowledgeRelation, KnowledgeSearchRequest,
    KnowledgePathRequest, KnowledgePathResponse,
)
from app.services import kg_service

router = APIRouter(prefix="/api/knowledge", tags=["Knowledge Graph"])


@router.post("/point", response_model=KnowledgePointResponse)
async def create_point(kp: KnowledgePointCreate):
    """创建或更新知识点（MERGE：id 已存在则更新属性）"""
    created = await kg_service.create_knowledge_point(kp.model_dump())
    if not created:
        raise HTTPException(status_code=500, detail="创建知识点失败")
    return KnowledgePointResponse(**created)


@router.get("/point/{kp_id}", response_model=KnowledgePointResponse)
async def get_point(kp_id: str):
    """按 ID 查询单个知识点"""
    kp = await kg_service.get_knowledge_point(kp_id)
    if not kp:
        raise HTTPException(status_code=404, detail="知识点不存在")
    return KnowledgePointResponse(**kp)


@router.post("/search", response_model=list[KnowledgePointResponse])
async def search_points(req: KnowledgeSearchRequest):
    """按关键词搜索知识点，可选按分类过滤"""
    results = await kg_service.search_knowledge_points(
        keyword=req.keyword, category=req.category, limit=req.limit,
    )
    return [KnowledgePointResponse(**r) for r in results]


@router.get("/point/{kp_id}/related", response_model=list[dict])
async def get_related(kp_id: str):
    """获取与某知识点直接关联的所有节点（不限方向）"""
    return await kg_service.get_related_points(kp_id)


@router.post("/relation")
async def create_relation(rel: KnowledgeRelation):
    """在两个知识点间创建关系（PREREQUISITE / RELATED_TO）"""
    ok = await kg_service.create_relation(rel.from_id, rel.to_id, rel.relation_type, rel.weight)
    if not ok:
        raise HTTPException(status_code=400, detail="创建关系失败，请检查知识点 ID 是否存在")
    return {"status": "ok"}


@router.post("/path", response_model=KnowledgePathResponse)
async def find_path(req: KnowledgePathRequest):
    """查询两知识点间的最短路径（Neo4j shortestPath 算法）"""
    nodes = await kg_service.find_shortest_path(req.from_id, req.to_id, req.max_depth)
    if not nodes:
        raise HTTPException(status_code=404, detail="未找到路径")
    return KnowledgePathResponse(
        nodes=[KnowledgePointResponse(**n) for n in nodes],
        length=len(nodes),
    )


@router.get("/categories")
async def get_categories():
    """获取所有知识点分类（用于前端下拉筛选器）"""
    return await kg_service.get_all_categories()
