"""FastAPI 入口 —— 路由注册、中间件、生命周期管理。

启动顺序：
1. lifespan 阶段校验 Neo4j 连接（失败只 warn，不阻止启动）
2. 注册 4 个路由模块：分析 / RAG / 知识图谱 / 学习路径
3. CORS 全开 —— 允许 SpringBoot 和 Streamlit 跨域调用
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.api import rag, knowledge, learning_path, analysis, pdf_parse, learning_agent
from app.services import kg_service, llm_service
from pydantic import BaseModel


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期：启动时初始化连接，关闭时释放资源"""
    try:
        kg_service.get_driver()
        print("[OK] Neo4j 连接成功")
    except Exception as e:
        print(f"[WARN] Neo4j 连接失败: {e}")  # 不阻止启动，运行时再重试
    yield
    kg_service.close_driver()


app = FastAPI(
    title="SmartLearn AI Service",
    description="基于知识图谱 + RAG 的个性化学习引擎 - AI 服务层",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Per-request API key: user's localStorage key via X-Api-Key header.
# If no header, use the .env default (not the previous user's key).
@app.middleware("http")
async def per_request_api_key(request: Request, call_next):
    key = request.headers.get("X-Api-Key", "")
    llm_service.set_request_key(key if key else None)
    response = await call_next(request)
    return response

# 注册 4 个路由模块，各自有独立的 prefix
app.include_router(rag.router)            # /api/rag/*
app.include_router(knowledge.router)       # /api/knowledge/*
app.include_router(learning_path.router)   # /api/learning-path/*
app.include_router(analysis.router)        # /api/analysis/*  ← SpringBoot 对接核心
app.include_router(pdf_parse.router)       # /api/pdf/*       ← PDF 解析
app.include_router(learning_agent.router)  # /api/learn/*     ← AI 带学 Agent


class ApiKeyRequest(BaseModel):
    api_key: str


@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "SmartLearn AI"}


@app.get("/api/config/api-key")
async def get_api_key_status():
    return llm_service.get_api_key_status()


@app.post("/api/config/api-key")
async def set_api_key(req: ApiKeyRequest):
    ok = llm_service.update_api_key(req.api_key)
    if not ok:
        return {"status": "error", "message": "API Key 不能为空"}
    return {"status": "ok", "message": "API Key 已更新", "masked": llm_service.get_api_key_status()["masked"]}
