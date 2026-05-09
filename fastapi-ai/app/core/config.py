"""全局配置 —— 所有环境变量统一入口，通过 .env 文件覆盖默认值。

使用 pydantic-settings 实现：
- 自动读取 .env 文件中的同名环境变量
- extra="ignore" 表示忽略 .env 中未定义的键，不会报错
- 所有敏感信息（API Key、密码）不写死在代码中
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ==================== 阿里云百炼（DashScope）====================
    # 通过 OpenAI 兼容接口调用，一个 Key 同时支持 LLM 和 Embedding
    dashscope_api_key: str = ""
    dashscope_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    llm_model: str = "qwen-max"                 # 对话模型：知识抽取 / RAG生成 / 错题解析
    embedding_model: str = "text-embedding-v4"   # 向量模型：文本 → 1024维向量
    embedding_dimensions: int = 1024

    # ==================== Cohere Rerank（可选）====================
    # 未配置时 rerank_service 自动跳过，不影响核心流程
    cohere_api_key: str = ""

    # ==================== Chroma 向量数据库 ====================
    # 嵌入式模式：数据直接存本地文件，不需要 Docker
    # PersistentClient 会在首次访问时自动创建 chroma_data/ 目录
    chroma_path: str = "./chroma_data"

    # ==================== Neo4j 图数据库 ====================
    # 支持远程服务器或本地 Docker，通过 Bolt 协议连接（端口 7687）
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "Neo4j123456"

    # ==================== RAG 检索参数 ====================
    rag_top_k: int = 5                 # 最终返回给 LLM 的文档数量
    rag_vector_weight: float = 0.7     # 向量检索在混合排序中的权重
    rag_keyword_weight: float = 0.3    # 关键词检索在混合排序中的权重

    model_config = {"env_file": ".env", "extra": "ignore"}


# 全局单例，各 service 模块直接 import
settings = Settings()
