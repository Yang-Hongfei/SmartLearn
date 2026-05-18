"""全局配置 —— 所有环境变量统一入口，通过 .env 文件覆盖默认值。"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ==================== DeepSeek API ====================
    # 通过 OpenAI 兼容接口调用
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com/v1"
    llm_model: str = "deepseek-chat"              # DeepSeek-V4-Flash (deepseek-chat)

    # ==================== Embedding（阿里云百炼）====================
    # DeepSeek 暂不提供 Embedding，保留百炼接口用于向量化
    embedding_api_key: str = ""
    embedding_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    embedding_model: str = "text-embedding-v4"
    embedding_dimensions: int = 1024

    # ==================== Cohere Rerank（可选）====================
    cohere_api_key: str = ""

    # ==================== Chroma 向量数据库 ====================
    chroma_path: str = "./chroma_data"

    # ==================== Neo4j 图数据库 ====================
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "Neo4j123456"

    # ==================== RAG 检索参数 ====================
    rag_top_k: int = 5
    rag_vector_weight: float = 0.7
    rag_keyword_weight: float = 0.3

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
