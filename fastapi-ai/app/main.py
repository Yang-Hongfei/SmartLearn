"""FastAPI 入口 —— 路由注册、中间件、生命周期管理。

启动顺序：
1. lifespan 阶段校验 Neo4j 连接（失败只 warn，不阻止启动）
2. 注册 4 个路由模块：分析 / RAG / 知识图谱 / 学习路径
3. CORS 全开 —— 允许 SpringBoot 和 Streamlit 跨域调用
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import rag, knowledge, learning_path, analysis
from app.services import kg_service


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

# CORS：允许 SpringBoot（任意端口）和 Streamlit（:8501）跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册 4 个路由模块，各自有独立的 prefix
app.include_router(rag.router)            # /api/rag/*
app.include_router(knowledge.router)       # /api/knowledge/*
app.include_router(learning_path.router)   # /api/learning-path/*
app.include_router(analysis.router)        # /api/analysis/*  ← SpringBoot 对接核心


@app.get("/api/health")
async def health():
    """健康检查 —— Streamlit 侧边栏用此接口判断服务状态"""
    return {"status": "ok", "service": "SmartLearn AI"}
