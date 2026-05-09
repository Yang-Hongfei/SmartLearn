"""SpringBoot 对接核心接口：收到题目+用户答案 → 返回错题解析+薄弱点+学习路径"""
from fastapi import APIRouter, HTTPException
from app.core.utils import now_iso
from app.models.schemas import (
    AnswerSubmitRequest, AnswerAnalysisResponse,
    ErrorAnalysis, WeakPointAnalysis, LearningPathNode, KnowledgePointResponse,
)
from app.services import analysis_service

router = APIRouter(prefix="/api/analysis", tags=["Answer Analysis"])


@router.post("/submit-answer", response_model=AnswerAnalysisResponse)
async def submit_answer(req: AnswerSubmitRequest):
    try:
        result = await analysis_service.analyze_answer(
            user_id=req.user_id,
            question_id=req.question.id,
            question_content=req.question.content,
            question_type=req.question.type,
            correct_answer=req.question.correct_answer,
            user_answer=req.user_answer,
            options=req.question.options,
            knowledge_point_ids=req.question.knowledge_point_ids,
            difficulty=req.question.difficulty,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分析失败: {e}")

    return AnswerAnalysisResponse(
        user_id=result["user_id"],
        question_id=result["question_id"],
        is_correct=result["is_correct"],
        error_analysis=ErrorAnalysis(**result["error_analysis"]) if result["error_analysis"] else None,
        weak_point_analysis=[WeakPointAnalysis(**wp) for wp in result["weak_point_analysis"]],
        learning_path=[
            LearningPathNode(
                order=n["order"],
                knowledge_point=KnowledgePointResponse(**n["knowledge_point"]),
                reason=n["reason"],
            ) for n in result["learning_path"]
        ],
        generated_at=now_iso(),
    )
