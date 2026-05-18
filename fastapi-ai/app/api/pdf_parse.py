"""PDF 解析 API —— 接收原始文本，返回结构化问答对。"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.services import pdf_parse_service

router = APIRouter(prefix="/api/pdf", tags=["PDF Parse"])


class PdfParseRequest(BaseModel):
    raw_text: str = Field(..., description="PDFBox 提取的原始文本")
    filename: str = Field(default="", description="原始 PDF 文件名")
    chunk_index: int = Field(default=0, description="当前分块索引（0-based）")
    total_chunks: int = Field(default=1, description="总分块数")


class ExtractedQuestion(BaseModel):
    topic: str = ""
    question_number: str = ""
    content: str = ""
    type: str = "essay"
    options: list[str] | None = None
    answer: str = ""
    difficulty: int = 3
    knowledge_point_ids: list[str] = []


class PdfParseResponse(BaseModel):
    questions: list[dict] = []
    total_extracted: int = 0
    topics_found: list[str] = []


@router.post("/parse-qa", response_model=PdfParseResponse)
async def parse_qa(req: PdfParseRequest):
    """接收 PDF 原始文本，调用 LLM 提取结构化问答对"""
    try:
        result = await pdf_parse_service.parse_pdf_text(
            raw_text=req.raw_text,
            filename=req.filename,
            chunk_index=req.chunk_index,
            total_chunks=req.total_chunks,
        )
        return PdfParseResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF 解析失败: {str(e)}")
